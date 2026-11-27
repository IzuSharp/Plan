# tail-completion06：Worker-D 之后的尾部 completion 因果假设

状态：**仅只读设计，尚无候选、构建、诊断或普通性能结果**。root 决定先将假设与 zero-cost 结果记入 Plan，然后另行授权实施。当前 pressure05 quiet 中没有修改运行中的源码或 binary。

## 决策与可证伪主张

应在最后长测 freeze 前检验这一个组合。当前 integrated05 的千行客户端 CPU 仍重复地高于 Dapper 约 6–10 倍；sampler04 已在实际普通消费者 ELF 上把大量 RhSpinWait 的真实 caller 定位到 ThreadPool 的 `LowLevelLifoSemaphore.WaitSlow`。这些事实足以支持检查仍存在的强制 completion dispatch，但没有证明多少 CPU 可被删除。

唯一假设是：**在 Worker-D 已将 provider Run/take 合并到一个 managed 执行工作项后，若当前实际 pull 的 continuation 已在 setter 前登记且无 captured scheduler，则在完整退休之后允许它 inline，可以去掉该 generation 的一次强制 completion 排队，并可能减少客户端 CPU/端到端成本。** 下一批 provider 执行的 coordinator 工作项仍存在。不是把 provider I/O 搬到业务发起线程，也不声称总 dispatch 减半。

旧 Common-A 单独方案的双轮普通无重复收益仍然成立，但不回答 Worker-D 后的交互。相反，复杂度本身也不足以拒绝这个仍有直接观察线索的组合。此次检验若机制不成立、完整契约无法保持，或机制成立但普通收益仍不重复，则可给出针对这个组合的明确停止依据。

sampler04 的 9350 个 WaitSlow 关联样本是样本，不是 queue 调用、唤醒次数或可删除的精确 CPU 预算。其 money1 场景也不是当前千行路径的独立 CPU 归因。不得把它们换算成预期收益百分比。

## 来源、身份与审查角色

新候选必须从 root 指定的 integrated05 `2ea67ce` / tree `4e3989` 完整身份起步；实施前从实际仓库读取完整 commit/tree，创建新任务 worktree/branch。原 Common-A commit `8ac1be5caa2d8d2c3d501da3bec3361f9f1dd1c2` 的完整源码当前没有恢复，因此本次是新合成，不能标成旧源码继续构建。

本设计作者此前是 Worker-D/计数/普通 wrapper 的独立审查者；root 现指定其转任本候选实现者。之前报告保留原身份；新候选由 `/root/candidate_contract_review` 独立审查，本人不自称新实现的独立审核者。

只读起点参考：

- `worktrees/Korda-worker-d/src/Interop.Callbacks/CallbackCoordinator.cs`：`Signal` / `IThreadPoolWorkItem.Execute` / `Process`。
- `worktrees/Korda-worker-d/src/Data.NativeHost/HostPullController.cs`：`Request` / `Resume` / `OnReady` / `Process` / `ExecutePrepared` / `GetResult` / `OnCompleted`。
- `experiments/worker-d-diagnostic/common-a-combination-prediction-04.md`：已封存的机制预测与契约风险。
- Plan `phase-2/common-a-implementation-01.md` 与 `common-completion-result-02.md`：旧实现描述及否定普通结果；不是当前候选源码。
- 锁定 runtime 文件：`restored-stage1/diagnostics/runtime-source-297acf/src/runtime/src/libraries/System.Private.CoreLib/src/System/Threading/Tasks/Sources/ManualResetValueTaskSourceCore.cs`。VMR `297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f`，runtime `deae2e32bf0e018e09d64597b7c59b62b73bb3ce`。其 `OnCompleted`、`SignalCompletion`、`InvokeContinuationWithContext` 分支是诊断分类依据；后续仍须匹配实际新 ELF。

## 最小产品触点

1. `src/Interop.Callbacks/CallbackCoordinator.cs` 增加内部 stack-local readonly `CallbackPublication`，绑定 publisher、generation、MRVTS version、result reference、选定 exception。`Process(ref publication)` 只准备它。`Execute` 完成原有 catch、scheduled/dirty bookkeeping 及已经需要的下一次 Signal 之后，最后执行 publication。真正 publish 不在 `SchedulingFault` catch 或会读写旧 coordinator 状态的 finally 里。
2. `src/Data.NativeHost/HostPullController.cs` 保留现有 Run/Abandon 返回、借用 lease 释放、registration drain、control/callback entry 归零、take、root/slot 释放与 failure 优先级。测试 observer 可能抛出的失败也必须在选定 publication 之前处理。publisher 在 setter 前核 captured generation/version；setter 后不访问 controller/native owner、batch 字段、callback cookie、registration、测试 hook 或新 generation。
3. `Resume` 无 reservation 的 setup-failure 路径同样使用局部 publication，process 的故障处理结束后才最终发布。不能只修主 coordinator 路径。
4. 完成上述边界后，只有 HostPull 的 MRVTS 允许 inline。其他派生类只适配空 publication 签名：`CallbackRegistration.cs`、`AsyncOperation.cs`、`RaceSuite.cs`、`HostCommandController.cs`、`HostCursorCloseController.cs`；不改它们的 completion 策略。
5. 回归只扩展既有 `tests/Data.NativeHost/ReadySchedulingTests.cs` / `Program.cs` 的 correctness 场景，并使用现有组件/真实 provider gate。诊断 hook/日志只放独立诊断构建，不能进入产品 CI 性能任务。

不改 C++、libpq/sqlite3、SQL、参数类型、DTO、batch32、消费者业务代码、runtime 参数或 public Fluent API。不得用共享 mutable pending publication 替代不可变局部值；否则 g1 setter 内的消费者发起 g2 后，旧 frame 可能读取新的 batch/error。

## 已有反例的复用与需要改变的断言

| 现有文件/方法 | 此组合必须保持的行为 |
| --- | --- |
| `ReadySchedulingTests.SetupPrecedesWorkerAndReady` | setup 先归还，provider Run 只在预约 coordinator 执行；真实 ready 不提前 publish。 |
| `ReadySchedulingTests.WorkerWaitsForNativeCallbackTail` | native callback entry 与完整 Run frame 退出后才交付；不是把用户 continuation 移进 OnReady/PInvoke。 |
| `ReadySchedulingTests.RejectedWorkerScheduling` | scheduler 拒绝不丢 accepted work，retry reservation 与 native 义务仍正确。 |
| `ReadySchedulingTests.HeldCompletionPostPreservesNextWorker` | 当前旧断言要求 g1 的 Post 持有时 g2 dirty 但不能跑；新候选必须显式改为 g1 退休后 g2 可独立 Run/take/publish，释放旧 Post 后不改 g2。保留旧预期和变更理由，不能静默删掉阻塞验证。 |
| `WorkerExecutionTests.UnrunSettlement` 两分支 | 从未执行的 accepted prepare 可由取消/Source close 安全结算；不依赖可接受新 queue。 |
| `WorkerExecutionTests.ExecutionFailure` BeforeRun/RunReturned | 第一失败、未知执行完成证明、native retirement 不受 setter 改动影响。 |
| `Program.PrivateFetchOwnerFailures` | setup/take/Published hook 的原始错误身份与资源释放顺序保留。 |
| `Program.ReusablePullBatches` / `RejectConsumed` / `HeldPull` | 同一 owner 复用、stale/重复 GetResult、持有 read scope 与 batch generation 隔离。 |
| `Program.PrivatePullStopBeforeReservation` / `RejectedPullScheduler` | unreserved setup 与并发 Stop、调度全拒绝、Stop 自身失败仍只发布一次，原始异常/归零正确。 |
| `BorrowedBatchHostTests`、cursor close 与 command/transaction 套件 | mapping 内 cancel/dispose/source close/错误；EOF/提前停止；错误顺序和 transaction unknown 语义不被共享基类签名改动影响。 |
| `tests/Interop.Callbacks/Program.cs` 与 `Verification.Interop/RaceSuite` | coalesced dirty/retry、不丢通知、拒绝计数及其他 completion 策略保持原样。 |

旧 Common-A 新增六类反例在当前源码不存在，必须重新实现且绑定本候选：无 captured scheduler 的实际 inline；ExecutionContext 恢复/还原；晚登记仍排队；captured Post 在 dispatch 前抛出；Post 在消费 g1、创建 g2 后抛出且同一异常只离开 managed executor 一次；四个已经消费但 publisher 仍被任意 Post 持有的 generation 并行存活，随后全部释放并确认第五代和 owner 归零。

至少一个 baseline-negative 应只放新异常边界测试，保留 baseline 产品字节，证明测试能区分旧 `SchedulingFault` 污染 g2 的路径。不能用“baseline 不 inline”作为失败负控来声称原 baseline 不正确。

任意用户 continuation/Post 可长期阻塞自己的 publisher stack。候选必须诚实声明它只提前结束 library processing ownership，并不保证任意用户阻塞下活栈/线程总数有界。固定 worker 池或吞掉 Post 异常均不属于此候选。

## 独立诊断：实际 inline、eligible 与 queue 边界

先做同输入的 current integrated05 与 tail06 **独立有插桩构建**，不获得普通计时/分配/RSS 信用，不修改最终 runtime。初始机制集合限于双库的相同 full1000 窄 DTO；small/early-stop 等契约由 correctness 套件先覆盖。是否补 money1 作为普通回退控制由 root 统一窗口决定。

每条记录绑定 request、generation、MRVTS version、provider、managed/native TID、单调 timestamp。记录真实 OnCompleted entry/return 与 flags、当时可见的有效 captured scheduler；setter entry/return；continuation trampoline entry/return；GetResult entry/return；native Run/Abandon return、take、资源退休与 coordinator TryQueue/Execute。日志缓冲必须有 loss/overflow 计数，缺记录不可当成零。

- **pre-registered 确证**：对应 OnCompleted 已正常返回，且其区间早于本 generation 的 setter entry；无自定义 SynchronizationContext / 非默认 TaskScheduler。只有 ExecutionContext 的情况另列。重叠区间归未知，不把 OnCompleted entry 早于 setter 当注册已成功。
- **实际 inline 确证**：同一 generation/version 的 GetResult（或 continuation entry）在同 TID 的该 setter 动态调用区间内。用独立诊断的 thread-local 嵌套 frame token 关联；仅相同 TID 不足。setter 的 finally 日志只写独立的局部/诊断记录，不读被下一代重置的 controller 字段。抛异常也要落 setter exit，并原样传播。
- **actual coordinator queue**：直接计 `ICallbackScheduler.TryQueue` offer/accepted/rejected 与 `Execute`，按 generation 与 processing turn 区分。此计数不等于 completion queue，下一代 Run 工作项不应凭空消失。
- **MRVTS 内部 queue 的证据范围**：不修改 runtime 时，library probe 不能直接读取内部 ThreadPool enqueue 计数。对已证实 pre-registered/no-scheduler 的真实执行区间，结合匹配 ELF 的实际 `SignalCompletion` 分支，可证明默认源进入一次 enqueue、候选进入 continuation call；这是“观测条件 + 已核源码/机器码”的路径归因。要声称直接观测了内部 enqueue，则必须另有真实该调用点探针；不能将 setter/GetResult 计数改名成全进程 queue 次数。late-registration/captured scheduler/未观测重叠分别报告。
- **计数不变量**：每代最多一次 publication / GetResult；SQL、native Run/take、批数、行数/列数与字节校验相同；先归零 native execution/lease/controls/callback-entry 再 setter；最终 owners 0。baseline 与 candidate 各自报告 eligibility，不能假定两者相同节奏。

诊断本身会改变竞态的相对时间；eligible 比例仅属于该诊断身份，不直接当成无插桩 ordinary 比例。机制证明足够后退出诊断；只有无插桩、默认 runtime 的交错 ordinary A/B 能决定收益。无需先重开全流程 CPU 采样，也不需要 spin0。

## 分阶段停止依据

1. 若正确性反例暴露无法在该边界解决的资源/错误语义改变，拒绝此候选；保留失败 raw 与最小反例，不弱化验证器。
2. 若 current full1000 没有可观测的 eligible completion，先确认没有日志丢失/区间重叠分类导致的不可见性；若证据仍不支持可删除的 dispatch，停止该组合。候选已有 eligible 但没有去掉对应强制 dispatch，则实现未实现假设。两者都不能用更多普通测量替代机制缺失，也不能把诊断中未观察到 eligible 扩张为“普通路径绝无 eligible”的证明。
3. 机制成立且 correctness/package gate 通过后，冻结两条普通输入，用同机交错反向次序比较 current integrated05 与 tail06 的 full1000 主场景；money1 是已知 spin/尾延迟风险控制，SQL/DTO/批大小和默认 runtime 不变。以重复 CPU/成功、端到端服务时间与 p95/p99 一起判断，保留全部轮次与 contemporaneous baseline spread。
4. 若排队减少但普通 CPU/延迟没有重复收益、方向处于本次重复噪声内，或出现稳定实质回退，则拒绝新组合并给出这些具体数据作为停止依据。不能只说“实现太复杂”。
5. 若有重复收益且风险控制成立，才合并到待冻结候选并重新跑必要 mixed/freeze 输入验证，最终四段长测使用同一最终身份。此时仍只对有证据的指标说改善或对齐；残余 6–10 倍差距不能改名为 parity。

本设计只决定检验上述一个有观察支持的组合；没有授权泛列或实现其他未观测热点。
