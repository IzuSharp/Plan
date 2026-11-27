# Coordinator 队列偏好：现有四份 trace 的只读归因

作者 `/root/worker_boundary_review`；没有产品改动、新 worktree、新构建或 workload。tail06 的普通去留由另一份独立短测分析决定，本报告不预先接受 tail06，也不选定新产品候选。

## 判断

**现有数据支持一个可隔离的小实验假设，但还不足以把 global queue 称为已证明的 CPU 热点。** 每个千行业务确实还有 33 个 coordinator offer/dispatch，而且 78–86% 的发送和执行跨线程；发送者全部是此进程中此前已经实际执行过 coordinator 的线程。实际机器码又明确把这类工作强制放到非本地队列。这个“已在池线程上，却强制非本地入队”的路径有直接计数和代码位置，足以提出仅切换成熟 ThreadPool 队列偏好的可证伪问题。

没有直接观测 global queue 的独占 CPU、缓存失效、锁竞争、enqueue 指令时间、OS 唤醒次数或普通路径的线程迁移比例。现有 intrusive 间隔不能证明这些队列操作造成了剩余 6–10× CPU 差距，更不能证明 preferLocal 会消除 RhSpinWait。是否修改产品，需要先由 Plan 决定，随后用单变量短 A/B 作因果验证。

## 直接计数

来源都是已通过严格 parser 与独立回读的 `mechanism-01` 四格，未执行新测量。每格 16 次稳态业务 / 512 pull / 528 coordinator offer。`summary.json` 的每业务结果和四份 `*.offers.json` 保留原 controller/generation/version、offer ID、发送/执行 managed 与 native TID、原 event seq 与时间戳。

| 现有诊断格 | 跨线程 offer/总 offer | 比例 | 含 native Run 的跨线程 turn/512 | 每业务跨线程 turn 范围/33 | Execute 早于 offer-return |
| --- | ---: | ---: | ---: | ---: | ---: |
| SQLite before | 440/528 | 83.33% | 424/512 | 19–32 | 283 |
| SQLite tail | 421/528 | 79.73% | 406/512 | 13–33 | 81 |
| PostgreSQL before | 456/528 | 86.36% | 444/512 | 21–32 | 364 |
| PostgreSQL tail | 414/528 | 78.41% | 400/512 | 18–31 | 42 |

四格全部 528 个发送方都在发送前已出现过本进程的真实 `Execute`；这不是 `Thread.IsThreadPoolThread` 或 runtime TLS 字段的直接探针。结合实际 scheduler 和 Dispatch 的 ThreadPool thread-local 初始化源码，可推断这些发送线程有本地 work-stealing queue 可用。候选若获准，仍应绑定实际 ELF 参数和选中的分支，不把这个推断伪装成已运行过 local 路径。

跨线程判定要求 managed TID 与 Linux TID 这对身份不同；同一 TID 后来执行也不是 inline。所有接受的 offer 对应一次 execute；每业务 32 个含 native Run 的 turn 加 1 个没有 native Run 的 turn。没有去掉最后一个 turn 来美化比例。

### 时间只用于描述事件关系

| 现有诊断格 | offer-enter→Execute-enter p50 / p95，μs | offer-return→Execute-enter p50，μs |
| --- | ---: | ---: |
| SQLite before | 3.629 / 20.812 | -2.809 |
| SQLite tail | 18.123 / 41.351 | 11.059 |
| PostgreSQL before | 3.719 / 24.320 | -4.783 |
| PostgreSQL tail | 22.516 / 56.424 | 13.909 |

使用 nearest-rank 分位数。BeginOffer 在真正 queue API 之前，EndOffer 在 API 返回之后；两端还包含 clock、日志锁和写入。真实 enqueue 指令未单独记录，因而仅处于这个调用包络内。不同线程可在发送方尚未写完返回探针时进入 Execute，上表大量负值是正常并发关系，不能裁成 0 后称为纯 queue wait。

`*.offers.json` 同时保留 scheduler-call 包络的 elapsed 和发送线程 CPU 差值。它们包含插桩，可能与 executor 的工作重叠；本报告不汇总为独占成本，不拿 before/tail 的时间差当收益。特别是 tail 中 continuation 的工作位置和诊断 trampoline 都不同，不能由这些 μs 判断普通 tail06 去留。

## 实际源码与 ELF 路径

产品入口是 `src/Interop.Callbacks/CallbackCoordinator.cs:91–94`，`ThreadPoolCallbackScheduler.TryQueue` 当前调用 `ThreadPool.UnsafeQueueUserWorkItem(item, preferLocal: false)`。没有单独保留该小 wrapper 的机器码符号；actual `CoordinatedCallback.Signal` 中它已内联为真实直接 call。

`machinecode/receipt.json` 保存 32 条只读 objdump/addr2line 命令，四个实际 ELF/debug 前后 SHA 均与既有独立机器码回执一致，符号表自身也核对了原 SHA。没有重新构建或执行这四个 ELF。

| 实际诊断 ELF | Signal 中把参数清为 0 | 紧接的实际 queue call target | WorkQueue.Enqueue |
| --- | --- | --- | --- |
| before SQLite | `0x10b02a xor esi,esi` | `0x194d30` | `0x193fd0` |
| before PostgreSQL | `0x10b12a xor esi,esi` | `0x194fd0` | `0x194270` |
| tail SQLite | `0x10b02a xor esi,esi` | `0x194f30` | `0x1941d0` |
| tail PostgreSQL | `0x10b12a xor esi,esi` | `0x1951d0` | `0x194470` |

实际 UnsafeQueueUserWorkItem(IThreadPoolWorkItem,bool) 将 preferLocal 取反再传入 Enqueue。以 before SQLite 为例，`0x194d71` 的 test / sete 产生 forceGlobal；Enqueue `0x193fe4` 测试该参数并在 true 时跳过 local TLS 路径。非本地路径调用实际 ConcurrentQueueSegment.TryEnqueue / ConcurrentQueue.EnqueueSlow；local 路径调用 WorkStealingQueue.LocalPush。两者最后都进入 PortableThreadPool.EnsureWorkerRequested。**改 local 偏好不会移除 EnsureWorkerRequested，也不会把 33 次 coordinator dispatch 变成 0。**

锁定 `ThreadPoolWorkQueue.cs` 的相关实现：

- 610–640：`Enqueue` 在 `!forceGlobal` 且 threadLocals 非空时 LocalPush；否则使用全局或 assigned-global ConcurrentQueue。不能未经读取运行时字段就宣称本机只有一个全局队列。
- 111–181 与 266–330：本地 owner 从尾部 push/pop；有扩容、内存屏障和竞争慢路径，不是零成本。
- 336–388：其他 worker 从头部偷取；local 偏好不保证同线程，也不禁止并行执行。
- 740–826：Dequeue 先取自己的 local，之后 high-priority/global/其他 global，最后才尝试偷其他 local；实际 Dequeue ELF 的第一条取工作路径对应 LocalPopCore。
- 896、941–945、1015：Dispatch 先建立 thread-local queue，执行开始与结束清理 ExecutionContext/SynchronizationContext。
- 1030、1153：worker 被要求退出或 thread-local 清理时转移剩余本地工作；这是避免遗留工作的机制，不是有界公平性保证。
- 1634–1652：接口重载不创建用户 delegate wrapper、不捕获发送方 EC；只入队，返回 true。

`runtime-source.json` 绑定现有上游原文、SHA 和锁定 VMR/runtime commit。这里没有把当前网上新版本的行为代入已构建镜像。

## 契约评估与实际反例

| 契约 | 从源码可确认的部分 | 仍需约束的部分 |
| --- | --- | --- |
| never-inline / public async | queue API 和 LocalPush 不调用工作项 Execute；调用栈内不会直接执行 driver。公共调用仍只安排工作 | 另一个 worker 可在 TryQueue 返回前 steal 并执行；不能增加“必定返回后才开始”的错误保证。同线程稍后执行也仍是异步派发 |
| EC / SynchronizationContext | 仍使用相同 UnsafeQueue 接口，未改变 capture policy；Dispatch 仍在工作项边界清理 EC/SC | MRVTS 的捕获/late registration 与 tail06 是否保留是独立问题，不得把队列偏好与 completion policy 同时切换 |
| generation、所有权、错误顺序 | 单改队列参数不改 gate、dirty/scheduled、Run lease、取消 registration、Take、token、retirement 或 poison 路径 | 更早执行/不同交错仍会行使这些状态机；原有拒绝、取消、提前停止、冷关闭、异常顺序回归必须保持 |
| 取消/关闭的可达性 | 非池线程且无 local TLS 时仍回落非本地；pool worker 的 local 可被其他 worker steal，停止 worker 会转移工作 | 当前 worker 持有用户 Post/continuation 或同步等待时，新工作可能只能靠其他 worker 的 steal 进展；完成延迟不能从源码保证不恶化 |
| 公平性 | 没有承诺全局 FIFO；现有代码也没有在产品 API 中指定公平调度顺序 | local LIFO + local-first 会改变竞争顺序，可能使旧 global 工作或旧 local 项反复让位。短闭环单 cursor 无法排除该风险 |

一个明确反例形态是：某 worker 每完成一个本地工作就产生下一个本地工作，而其他请求已在 global 排队。它每次 Dequeue 都先看到新的 local 项，因此较早到达的 global 请求可能持续被推迟；30 ms dispatch quantum 也不能单独证明公平，因为下一轮仍先读 local。另一反例形态是 tail 的旧 continuation/Post 把 publisher worker 持有不放，同时下一代工作只排在该 worker 的 local；能否及时由别的 worker 偷走，取决于池负载。不能把成熟 runtime 的 stealing 机制当成固定延迟保证。

现有 ReadyScheduling 的 held Post、异常及独立 generation 反例仍有价值，但它们注入的 RecordingScheduler 自己明确使用 preferLocal:false。因此这些测试通过不能独自证明生产默认 scheduler 改 true 后的 local 进展/公平性。最低限度需在真实默认 scheduler 下检查“持有一个 publisher worker，另一工作/取消/关闭仍能完成”，以及两个竞争 cursor 的短窗口进展；不要把这项缺口埋在 fake scheduler 全过里。

另一个范围约束：ThreadPoolCallbackScheduler 是共享默认 scheduler。直接改这一个参数会同时影响 HostPullController、HostCommandCallback、HostCursorCloseController、CallbackRegistration 和 AsyncOperation；不能报告为仅查询的内部改动。若决定仅试 pull，需要明确构造注入范围，但不能为此重新写自定义线程池或 trampoline。

## 可证伪的小假设与停止点

建议供 Plan 决策的单一问题是：**在保持选定基线的 completion policy、native、SQL、DTO、批大小、默认 runtime 和操作次数不变时，只让已处于 ThreadPool 的 coordinator 工作优先使用成熟 runtime 的 local queue，是否能获得重复的客户端 CPU/业务下降，且不损害其他请求、取消或关闭的进展与尾延迟？** 这不是已接受候选，也不依赖 tail06 最终被接受；基线必须先由当前普通短测去留决定。

如果获准，先以最小源码变更和独立诊断镜像证明参数实际为 true，非池调用仍 fallback，保持 native SQL/pull/offer/dispatch 及 owner/generation 一致。复用现有每 provider 16 业务 trace 可检查线程交接是否变化；cross-thread 比例不下降会否定“通过减少交接获益”的子解释，但不能仅凭它否定其他队列实现成本变化。最终 CPU 因果归因仍由同机交错普通短 A/B 决定。

普通验证只需同一 text1000 主问题与有竞争的短混合/取消关闭控制，不预先扩大到新的广泛诊断。若队列路径按预期切换而 CPU 改善不能重复、进入噪声，或尾延迟/取消关闭/公平进展出现实际回退，应拒绝这个方案并保留证据；不能以改更多 runtime 设置、重新设计 trampoline 或启动长测来追逐收益。本轮全部 1800 秒及 before-long 测试已按用户要求取消。
