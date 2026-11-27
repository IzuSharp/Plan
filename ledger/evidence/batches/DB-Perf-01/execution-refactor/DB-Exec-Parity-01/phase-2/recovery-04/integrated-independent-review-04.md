# DB-Exec-Parity-01 集成候选独立审查 04

审查者：独立 worker_boundary_review agent。范围是只读代码/契约审查、已封存计数证据复核；没有修改产品文件、没有运行普通 A/B、没有执行合并或发布。

目标最初为 commit `485477cef973555bed0807a3a0b0dc5503f83243`。审查期间 root 整理提交后 HEAD 为 `9709eace96ce3eb0e1be7325581fce3f28c25115`；两者 tree 均为 **2455cfb7635e5eadcc68e34ede48ec160102b2a8**，`git diff 485477cef… 9709eac…` 为空。因此本审查绑定该 tree，下面行号对应这个 tree。起点 main 为 `7ff7b57b907b689defb880b8af62d83679608603`。

## 结论与保留项

未发现可定位的 correctness blocker。Worker-D 的同步运行必须仍在受预约的托管工作项内执行；它减少的是每批一次 native WorkerPool post，没有消除 managed scheduling，也没有减少全部 FFI。计数证据已确认这一边界。该结论不是完整形式化证明，也不替代这个集成 tree 的编译、Native AOT 实际包消费、现有双库 correctness、安全和 owner drain 验证。

尚未关闭的性能问题是小查询 CPU 与 RhSpinWait 的实际 caller。历史叶子采样比例不能区分 semaphore、锁或 Thread.SpinWait 上层 caller；本轮 sampler04 正在为实际 machine IP 增加 caller 证据。decimal 单独候选的小查询上升不应因为“native 样本减少”就被解释为已解决。32/1000 行收益、单行成本、联表组合的尾部风险均需按各自匹配的普通测量保留原结论。

## Worker-D：准入、执行帧与 retirement

| 检查点 | 实现位置 | 审查结果 |
|---|---|---|
| Prepare 与旧 Request 共用准入 | `native/cpp/src/host.cpp` 2810–2882，`CursorPull::start_request` | callbacks/capacity、Source/session admission、pending/live cursor、严格递增 generation 都在接受前检查。Cancel、Worker、retirement tickets 在接受前准备；external 分支不进入 provider I/O、不 post native worker。 |
| 唯一执行 claim | 同文件 2891–2926，`CursorPull::execute_prepared` | 同时匹配 current generation、external generation、未 claim；在同一 mutex 内取出 pending Worker。重复 Run、重复 Abandon、旧 generation 不能偷取新请求。 |
| Source join 覆盖整个 exported frame | 同文件 2560–2591、2893–2926 | Worker 是最早声明的 owner-bearing local，最后析构。显式 `self.reset()` 发生在运行前。Worker 析构先释放 pull 和 Source reservation/capture，再完成 channel/source tickets，覆盖最后一个 native accessor，而非只覆盖 ready callback。 |
| 已接受但从未排上队 | 同文件 3194–3236，`CursorPull::request_close` | close 在 gate 内 mark cancel 并取走 pending Worker，gate 外沿原 run admission/error path abandon。先丢弃局部 cursor/gate 捕获，避免自己持有 join 的资源；不存在只靠 shared_ptr 环而永久等待 worker 的设计。 |
| close 与晚到 claim | 同文件 2899–2922、3194–3236 | close 夺走 pending Worker 后的一次晚到合法 claim 返回，但 callback 可能仍在 close 线程尾部。托管端仍必须等 readiness/control/registration drain；“Run 返回”不能替代此证明。 |
| cancel 与运行中 provider | `CursorPull::run`、`request_close`；`HostPullController.ExecutePrepared` 357–396 | 原 Cancel hook 和 provider cleanup 保留。Abandon 在 channel gate 内标 token；同步 native owner lease 限定于 Run/Abandon 调用，没有跨 await。 |

托管端 `src/Data.NativeHost/HostPullController.cs` 357–396 的 gate 保证 active、accepted、setup returned、尚未 claim、未 closed/indeterminate；还要求 `_slot >= 0`。这阻止 provider 工作通过 setup-failure 的 inline Resume 路径运行。`_controls` 覆盖同步调用及 observation boundary。调用前或返回后的异常都进入 indeterminate cold-close，保留首个业务错误和 owner/root，直到现有关闭证明安全。`OnReady` 仅在 `_executing` 时抑制重复 Signal；当前 Process 在 Run 返回后继续 take/drain。完成发布之后允许 continuation 推进下一 generation，既有 coordinator dirty handoff 负责尾部竞态。

已阅读、需由集成验证实际覆盖的定向测试：

- `native/cpp/tests/streaming_tests.cpp` 836–1119：prepared generations、never-run 五种关闭方式、run/run 与 run/abandon 竞争、ready 后执行帧仍被 Source join 覆盖、in-flight stop、close callback 未退出时的 late claim。
- `tests/Data.NativeHost/WorkerExecutionTests.cs`：拒绝调度、never-run 取消和 Source close、before/after run observer failure；恢复可调度后不能偷偷执行原 SQL，保留原终端错误。
- `tests/Data.NativeHost/ReadySchedulingTests.cs` 155–357：实际 native callback tail、拒绝 worker scheduling、下一 generation 在 coordinator 尾部进入、并行读取被拒绝。
- actual C ABI 的 Prepare/Run/Abandon export 与 capability binding 审查；新增 capability bit30，unsupported bit31 拒绝与 inventory/packer 对齐。

这里没有将旧分支上的 test receipt 写成集成 tree 已通过，也没有新增 CI 测量入口。

## decimal、SQLite prepare 与 consumed relation

`native/cpp/src/contracts.cpp` 219 的 `canonical_decimal_configuration` 只接受精确 canonical 字节形状：`{"precision":N,"scale":M}`，precision 1–29，scale 0–min(precision,28)。任何不符的字节仍回落到原 JSON validator；profile-specific rejection 先于快捷路径。611 的配置校验和 1532 的 scalar 使用保持原错误优先级。数字范围是固定小范围，溢出保护在累加前；没有看到合法/非法配置接受集合被扩大。

`native/cpp/src/provider.cpp` 727 改用 `sqlite3_prepare_v3(..., 0, ...)`。现有物理 statement 仍按 command 生命周期 finalize，所以这是去掉不匹配的 PERSISTENT hint，使 SQLite lookaside 可使用；不是语句缓存，不应写成 prepare 次数减少。DDL 变化仍走原 prepare 路径。

`src/Query.Binding/QueryBinding.cs` 166–179 的 `ConsumeAndImport` 只用于私有临时分支。它拒绝 self/different Source，两个 semantic admission 均为 fail-fast，未引入阻塞互锁。destination import 先拥有 retained graph，随后才把 source disposed 标记置位；失败发生在成功 import 之前时不消费 source。`src/Query.Fluent/QueryContext.cs` 127–136 仅封闭该私有 context。公共 SnapshotAndImport 的独立快照路径保持；输入快照与对象生命周期仍是正确性边界，不可把该内部 consume 扩大到公共可复用选择对象。

## 与原始计数对照

封存证据：`analysis-recovery-04-attempt-02/README.md`、`summary.json`、`requests.json`。24 个原始进程、48 笔测量业务、2510 项验证全部通过。双库一致：

| 业务 | native WorkerPool post，baseline → Worker-D | 实际 C ABI entry，baseline → Worker-D | batch bytes |
|---|---:|---:|---:|
| full1000 | 34 → 2 | 104 → 136 | 68008 → 68008 |
| exact32（含空 EOF 批） | 4 → 2 | 13 → 15 | 2274 → 2274 |
| earlystop（native 取32、只物化1） | 3 → 2 | 10 → 11 | 2146 → 2146 |

Worker-D 每批新增 Run C ABI，移除该批 native post；cleanup worker 和 final control close 两次 post 保留。所有 candidate Run/take 落在同一托管工作项，Run 先返回、再 take，且不在同步 MoveNext 调用栈上。已观察线程的 self-switch 共17713条，但这些有限计数进程的业务窗口内 CPU 叶子样本为0；不能靠这批计数把 CPU 或 RhSpinWait 归因关闭。

PostgreSQL complete 查询消息数与 DataRow 数保持。earlystop 时服务端仍发1000个 DataRow，native 读32、托管物化1；关闭/同步边界增加的 Sync 必须独立解释。代理收到消息的时刻不等于客户端实际阻塞时刻。

## 剩余验收边界

1. 合并前 root 以同一 tree 的真实包消费和正确性结果关闭集成门禁，并执行既定 impact selection；仅保留既有 CI 编译、correctness、安全、AOT 包消费和规则发布。
2. sampler04 的 caller、runtime spin sensitivity 只用于归因。default runtime 下未插桩普通结果独立保留；不修改最终 runtime 配置来掩盖成本。
3. 不把任何样本份额换算为精确阶段时间，不把 SQL/message/FFI/post 计数互相替换，不把此次审查写成已完成最终四段1800秒验收。
