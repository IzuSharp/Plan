# DB-Exec-Parity-01：受控托管工作线程直接执行 C++ 的只读策略审查

状态：**条件可行，现有 ABI 不能直接实现；未选为产品方案，未实施、未构建、未测量。**

审查日期：2026-11-26。产品基线为 `7ff7b57b907b689defb880b8af62d83679608603`。本报告只检查代码和契约，不把结构上的可行性当作正确性或性能证据。原 Stage 1 的 32 批/34 个 native job、队列时间线和 spin 采样，以及 common-A 未稳定降低端到端成本，是本次问题的输入；没有重新执行它们。现行策略文档也明确限定了这些证据的解释范围。[D1]

## 1. 结论与建议范围

“公共 Async 先离开发起调用栈，再在受控托管工作线程上同步进入 C++”**没有被 Async 规范本身禁止**。规范禁止发起线程静默等待原生完成，并没有要求数据库 I/O 必须由 C++ 创建的 OS 线程执行。现有 C++ `Session::open_cursor`、`Cursor::fetch`、`ProviderConnection::prepare`、`ProviderStatement::append_next` 本来就是同步函数；SQLite 使用 `SQLITE_OPEN_FULLMUTEX`，当前 native worker pool 也没有将一个 Session 固定到唯一线程，单物理连接由 Session/CommandGate 和 CursorReadAdmission 排他保护。因此，没有发现“必须绑定 native 创建线程”这一直接阻断。[D2][K1][K2]

但这不是把 `Task.Run` 包在现有 `Request` 外面即可完成的优化。现有导出入口会自行创建并排入 native worker，然后通过反向 ready callback 交给托管 coordinator。若托管 worker 调用旧 Request 后阻塞等 ready，只是额外占住一个托管线程，原 native 队列和回调仍在。[K3][K4][K5]

**最窄的可评估后续候选，是只改变 cursor pull 的执行调度：**保留创建时输入快照和 Session gate，保留每代请求的 native 准入、取消、资源票据；将已准入的一代交给有界、保证不内联的托管执行队列；同一个托管工作项同步调用新增的 C++ run/take 边界，返回后领取原有 batch owner，再完成原 ValueTask。最初保留池准入、管理操作、最终关闭、Source join 和事务完成协调的现有 native 路径。普通写入可以在 pull 结果独立成立后再评估同类二阶段接口，不能顺手把全部控制路径合并进去。

这一范围是审查建议，不是采纳决定。是否值得实现仍由 root 根据当前候选结果与成本判断。

## 2. 现有调用边界是否支持

| 现有代码边界 | 已有能力 | 直接复用的限制 |
| --- | --- | --- |
| `DataSession.OpenPlanStreamAsync` → `NativeHost.CreatePull` → `capture_execution` → `CursorPull::create` | 同步快照输入，验证 source/plan，持有 Session 单操作 gate，创建惰性 channel；尚未调用 provider prepare/step | 这段可以保留在原准入位置。不能把整个捕获过程推迟到后台，再读取调用者可能修改的输入或改变并发 Session 的拒绝次序。 |
| `HostPullController.Request` | 一代一个 ValueTask；预留 coordinator slot、安装取消注册，发起 native request；记录 setup/control/callback/drain 状态 | 它的状态机以 native ready callback 为进度事件，不能删除 callback 后仅假装 `_ready=true` 而不重证 native accessor 和 registration 的完成边界。 |
| `nw_db_cursor_pull_request_v1` → `CursorPull::request` | 在 native 锁内检查关闭、上一批、代号和预算，创建 Cancel/Worker，登记 source 与 channel 票据 | 接受后无条件尝试 `source->workers.post`。没有同步运行参数，也没有可从 C# 调用的“已准入 run”入口。 |
| `CursorPull::run` | 可复用完整的 open/全列验证/二次准入/fetch/异常归类流程 | 它是私有方法，结尾必经 `complete` 的 ready callback；直接暴露它会同时暴露原 callback 和票据假设。 |
| `Cursor::fetch` / provider | 已是同步执行并返回有界 Buffer；无需改 libpq/sqlite3 算法 | 必须继续经过原 channel、CursorReadAdmission 和预算边界，不能让托管代码直接绕到 provider。 |
| `nw_db_cursor_pull_take_v1` | 从精确代号领取一次 batch owner、view、KnownEnd | 可以沿用其所有权规则。它只能取 ready 的结果，不会执行 fetch；不是可代替 run 的同步执行入口。 |
| `CommandCompletion::create/start/Worker::run` | 输入捕获、独立结果、取消和 native fences 已分开 | `start` 会 post native pool；`Worker::run` 首先等待 `submitted`。将现有 `run()` 原样塞入 `start()` 调用栈会在尚未发布的 gate 上自等待。 |
| `OpenSessionAsync` / Source admission | 独立、有界连接等待队列，不占 provider worker 等空闲连接 | 不应改成托管 worker 阻塞占位等待 Session；否则有限执行线程可以全被等待者占住，归还或清理得不到进度。 |

以上分别来自现行 Host、Host ABI、C# controller 和 bindings；私有 pull/command 扩展本来就与冻结 operation ABI 分开。[K1][K3][K4][K5][K6][K7][K8]

当前正常路径大致是：native queue → C++ 执行 → UCO ready → managed coordinator/take → 异步 continuation。建议范围则是：有界 managed queue → C++ 同步执行并返回 → 同一工作项 take → 异步 continuation。仍保留调用者与工作线程之间的调度，也仍保留安全的 continuation 发布；没有“消除所有跨线程”这一结论。

## 3. 最小内部接口应承载什么

需要的是一个新的、明确协商的私有同步执行扩展，或者等价的内部二阶段协议；不能修改旧 `request_v1` 的非阻塞语义。下面是**职责草案，不是已经设计冻结的 ABI 名称或结构**。

### A. 非阻塞 prepare/admit

在原接受位置完成一代请求的验证、输入/owner 捕获、Cancel 建立、Source pending 预留及 channel/source retirement 票据登记。它只返回一个不可重复执行的已准入工作票据，不 post native queue、不执行 provider I/O、不保留托管栈指针。

必须在工作项向托管队列承诺接受前，把 native 生命周期登记完。若只在后台 worker 真正开始时才 `reserve_operation`，Source close 可能先看到 `pending==0`、停止 native pools 并声明 retired，而托管队列仍持有被当作已接受的工作。现有 `Source::join` 正是先等待 `leased/pending`，然后等待三类独立 fences；新队列必须进入同一证明链。[K1]

票据可以由独立 opaque owner 承载，也可以是 channel 内受精确代号保护的等价所有权；后者必须证明不存在 channel↔worker 的自持有环，并处理“已 prepare、尚未 run、消费者放弃”的退休。现有 `OwnerLease` 是 `ref struct` 同步借用，明确不允许 pointer/view 逃出调用作用域，不能把它或借来的 `nint` 直接放进后台队列。队列必须拥有新的 native 工作引用或其他明确持有到实际完成的 owner。[K8]

### B. worker-only synchronous run，随后同项 take

工作项只在受控托管执行线程上进入新入口，消费一次已准入票据，复用 `CursorPull::run` 的业务部分和 `Cursor::fetch`。正常返回时原生执行局部引用、Cancel provider hook 和读 admission 已结束，返回现有 batch 记录或者可领取的精确终态。托管代码在**同一工作项**内执行既有结果校验/Attach。

初始实现不必把 run 和 take 强行压成一个 FFI：一个同步 run 后马上调用现有语义的 take 已能检验队列假设，也便于保留富错误的“一次领取”规则。若合并为 run-take，则必须在输出 handoff 的任何异常中补偿 Buffer owner，不得重发 SQL。run 返回和 take 所有权必须写清；不能将同步返回一概称作 Source/事务已 quiet。[K3][K8]

正常路径无需 ready UCO cookie。异常、异步取消注册 drain 或关闭控制仍可需要独立进度，不应承诺所有情况下只出现一次 managed dispatch。

### C. 已准入但未开始的 cancel/abandon/retire

需要明确的单次补偿路径。托管调度拒绝、关闭或构造失败发生在 native 接受之后时，必须把该代精确结算并归还 reservation/fence。可以复用当前 stop 语义，但“Stop 只标记了取消”本身不够：如果没有任何 worker 会进入 run，Source pending 会永久不归零。应通过受保证的补偿工作项或有明确安全前提的未运行票据撤销来完成，不能依赖未来 ready callback。

正常执行和撤销必须用一个原子状态转换互斥，确保只能有一个路径调用 provider、转移结果或归还票据。重复 run、过时代号、错误 source、重复 take 都应确定拒绝。采用新扩展的协商、布局检查和 capability 必须覆盖两个独立 provider 包；旧 ABI 保持原含义。[K1][K3][K7]

## 4. 必须保留的约束

| 约束 | 具体源码事实 | 对该策略的要求 |
| --- | --- | --- |
| 发起线程不等待 native | 公共规范禁止 initiating thread 等原生完成；现有 `ICallbackScheduler` 要求不内联、不重复接受、不能接受后抛错 | 受控 worker 必须有可验证的 never-inline 调度。`ConfigureAwait(false)` 不保证换线程；`Task.Yield` 也可能回原 SynchronizationContext。不得在共享 `_gate`/Session/Source 锁中调用阻塞 run。 |
| 有限队列与进度 | `WorkerPool::post` 的 deque 本身没有硬容量；普通 work 依靠 `Source::reserve_operation` 上限 `nodes+connections+waiters`。managed coordinator 容量为该和加 2；控制有独立 native workers | 新 managed queue、等待者和 retained payload 都必须有限，容量先预留。不能误把 `Task.Run`/ThreadPool 的全局队列视为有界，也不能把所有控制放入被阻塞 provider 填满的同一工作池。保留原资源限额与拒绝分类，不擅自缩小 admission 以换取更好延迟。 |
| Session 并发拒绝 | `Session::admit` 用 `active.exchange(true)` fail-fast；cursor 从创建至退休持有 CommandGate | 继续在原接受点持有 gate。不能改为后台 worker 开始才占 gate，否则同 Session 两次并发调用可能先都入队，变成隐式串行命令队列。 |
| 快照和所有权 | `capture_execution/relation/mutation` 将输入变为 owned plan/typed values；Query/SQL plan 有一次提交和 source identity 规则 | 只移动已捕获的工作。不能推迟读取调用者参数或持有借来的 Span/OwnerLease 跨队列；不能重做编译或重放副作用。 |
| 元数据与 DDL | `CursorPull::run` 先 `open_cursor` 全形状验证，再检查 Source、Session、取消和 closing，之后才 fetch/step/Bind Execute | 必须完整复用这两次准入和新鲜元数据；不可因已有 managed worker 就把检查合并到 prepare 或直接执行 SQL。SQLite 仍用同一 statement describe/bind；PG 原 Parse/Describe/Sync 和 Execute 边界不变。 |
| 取消先后 | `request_close` 在 channel 锁中先 `mark_requested` 并置 closing，再锁外 provider wake；`CursorReadAdmission::check` 保留 live-batch/end/concurrent-use 先后；provider detach 与 request 用独立 Cancel mutex | 在运行中直接维持现有 stop 进度，不能将 cancellation 也排在该阻塞工作后面。SQLite 保留 `sqlite3_interrupt`，PG 保留取消标记和 `poll` 前后的 context 检查；不能臆造本路径已有 PQcancel 消息。运行后才到达的取消不能改写已经冻结的成功或 provider failure。托管注册仍可能同步触发；发布前必须完成注册返回和 DisposeAsync drain。 |
| 超时口径 | relation/mutation 在 capture 时记 admitted，run 扣除已过时间；普通 `open_cursor` 依现有 plan timeout 建立 deadline | 不统一改成“后台开始重新计时”或“所有路径都从入队算起”。移动排队归属时保留每条现有业务路径的绝对时间和错误选择。 |
| 结果与富错误 | native complete 先处理清理副作用、保留主错误和 cleanup 附注，再 ready；take 精确代号并只转移一次 | callback 可去掉，但完整错误冻结点不可提前。无论 native run、结果 adoption 或 managed observer 失败，都必须补偿 owner；原 SQLSTATE/code/correlation、bulk 进度及 OCE token/classification 不变。 |
| 回调与 continuation 安全 | `HostPullController` 只让 UCO 做有界状态更新；`ManualResetValueTaskSourceCore` 使用异步 continuation；状态回收早于发布 | 新路径在 C++ 返回之后才能做托管领取和发布，不能从 native reverse callback 调用任意 DTO mapper。初始候选保留异步 continuation，避免把 common-A 的另一变量同时混入；不得在工作项发布后再读可被下一代重用的 controller 状态。 |
| 并发 Dispose 和早停 | `TypedStream` 的 moving fence 保护正在 materialize 的行；batch 释放等待已有 read；CursorPull join 等实际执行票据而非仅 result ready | 新票据进入原 native fences。取消公共等待不等于释放 native call owner；工作项在阻塞 FFI 时必须仍有 strong root/owner。清理不能等待自己的票据；被提前停止、未领取的 buffer 必须归还，已交给 mapper 的 buffer 不能提前回收。 |
| 连接安全归还 | `Cursor::retire_provider` 对未耗尽 PG reader 做有界 drain/确认；未知退休 poison/discard 并保留 accessor；Session 清理和 pool return 独立存在 | “同步 fetch 已返回”只证明该次调用退栈，不证明 cursor EOF、PG ReadyForQuery 或连接已可复用。最终 close 继续走原 join/snapshot/错误路径，不能为了省一个队列跳过。 |
| 事务结果未知 | `Transaction::finish` 启动独立 finish/deadline workers，只等 primary_ready；deadline 可先返回 Unknown，而真实 COMMIT/清理仍未退休 | 不把 COMMIT 改成普通同步 SQL 返回就宣布 Committed，也不由取消 token 终止已分发 COMMIT。保持独立事务 workers/fences、Unknown 不可被后续 rollback 重写、连接隔离以及 cleanup snapshot。最窄 pull 候选无需碰此层。 |

以上约束的权威实现分别是 Host/ABI/provider、HostPullController/HostStreamTransport、TypedStream、Owners、CallbackCoordinator 和 DataSource；通用并发契约只用于补充容量/生命周期规则，不把其历史 Rust/SQLx 描述当作当前 C++ 线程实现。[K1][K2][K3][K4][K8][K9][K11][K12][K14][D3]

## 5. 明确应拒绝的实现变体

1. **在 public Async 调用栈里直接执行 SQLite/libpq。**直接违反 initiating-thread 规范；不能用 native 很快这一经验替代契约。
2. **`Task.Run(() => old Request + wait)`。**旧接口仍会排 native queue；没有实现所要隔离的因果变量，还多占一个阻塞线程。
3. **仅把 `CursorPull::request` 内的 post 替换为 `run()`，旧 C# 不变。**所有现有调用者都会同步等原生；旧接口的回调/接受语义也被悄然改变。CommandCompletion 还有 submitted gate 的直接自等待问题。
4. **只拿 raw Session/connection 指针在后台调用 provider。**跳过 owned snapshot、single-command gate、DDL/形状检查、CursorReadAdmission、错误附注和 retirement fences，不能满足现有契约。
5. **把 Source close、Cursor close、COMMIT/ROLLBACK、池等待全部塞入同一个有限 managed blocking pool。**关闭可能在等待同池中尚未执行的工作或自身 reservation；事务 deadline 与真实 native 退休不是一个终态。现有 Source close 特意使用独立线程，不能无证明地删除。
6. **用 token 把排队 Task 取消即认为工作已释放。**只要 native 已接受，就仍欠实际 terminal、输入和 owner 退休及票据归还。

这些拒绝针对具体实现，不构成对“先换到受控线程再同步进入 C++”这一总体方向的否定。

## 6. 工作线程选择与实际收益仍未知

使用共享 ThreadPool 的有界工作项只限制 Korda 占位数量，不保证执行线程不会被应用其他工作占满。PG 的 `receive/flush` 在需要时进入 `poll/WSAPoll`，SQLite busy/step 也可阻塞；若把这些调用直接放进一般 ThreadPool，要单独证明取消、timer、close 和应用 continuation 的进度。使用 Source 拥有的有限托管专用线程更容易保留“数据库阻塞不吃尽应用 ThreadPool”的结构，但会引入工作线程/队列/关闭管理，并可能与仍保留的 native pools 叠加 RSS。两者没有现成性能结论。[K1][K2][K4]

`DatabaseOptions` 当前声明 `EngineThreadingModel.EngineLocalAsync`，其公开说明为 instance-owned native executor。保留 native admission/control/transaction/close、只把明确的已准入同步边界放到 managed workers，属于混合内部策略，必须在 Design 准确说明。若以后删除全部 native executor，就不能不经契约核对继续宣称执行模型完全未变；这里不建议改公共 enum，也不把该声明自动当作当前窄候选的硬阻断。[K10][K13]

该策略与 common-A 不同：common-A 保留 native executor，只尝试减少完成后的第二次 managed hop；本策略把阻塞执行和结果领取放入同一个受控 managed 工作项，移除选定 pull 的 native queue/反向通知边界，初始保留 completion continuation 策略。**结构不同并不保证降低当前 AOT spin 或端到端成本**。现有采样不能把每个 spin 样本精确归给这一处，shared/dedicated worker 的调度行为和缓存亲和性也尚未测量。[D1]

不能把 34 native job 直接宣布会减少成某个新总数：需要逐类型重新计数剩余的 Session、pull、close 和控制任务。也不能将 native→managed callback 数减少直接写成 SQL、协议消息或必须等待的回复减少。引擎执行与协议工作应保持原量。

## 7. 若 root 后续选择实验，最小证明清单

本报告不执行以下事项；仅列出该候选应能被证伪的条件。

- 使用独立诊断身份，给同一 generation 记录 public entry/return、native prepare/admit、managed enqueue/dequeue、sync native enter/leave、take、publish、registration drain 和 retirement；记录单调时间、线程 ID/CPU、queue slot 与 pending/fence 变化。主动阻塞 provider 的 correctness gate 必须证明 public 调用已返回且发起栈没有在 native 等待。
- 计数实际 queue submissions、callback、FFI、SQL dispatch/protocol、批数、结果字节、native/managed 分配。目标是相同 SQL/行/批/字节下，选定 pull 的 native post 和 UCO ready 消失、native execute 与 managed take 属于同一个工作项；其它指标是否下降由数据回答。
- 针对 prepare 成功但 managed enqueue 拒绝、取消早于 worker、worker 执行中取消、Source close 抢先、未运行票据放弃、重复 run/take、所有权交接失败、held row + Dispose、晚到旧代工作项，验证唯一执行/唯一终态和最终 ledger。保留错误先后、DDL、异常清理、PG 协议确认以及原事务 Unknown 回归。
- 无插桩普通 A/B 仍按两库 1/32/100/1000、提前停止和原混合业务交错，特别观察 CPU/operation、服务与排队延迟、线程数量/RSS、队列容量拒绝拐点和取消/关闭进度。不能只看少了一次 post 就采纳。
- 若候选实际跨 `Data.NativeHost`、`Query.Binding`、共享 native Host/ABI，提交后重新运行 impact，按结果分别验证两个顶层包；不改 CI 加入任何 benchmark、剖析、校准或压力入口。

## 8. 审查引用

下列链接绑定本次产品基线；符号名在正文中给出。Design 链接绑定本轮已存在的策略头。只读源审没有执行信用。

[K1]: https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/native/cpp/src/host.cpp
[K2]: https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/native/cpp/src/provider.cpp
[K3]: https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/native/cpp/src/host_abi.cpp
[K4]: https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/src/Data.NativeHost/HostPullController.cs
[K5]: https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/src/Data.NativeHost/HostCommandController.cs
[K6]: https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/src/Data.NativeHost/DataSession.cs
[K7]: https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/src/Query.Binding/CursorPullCalls.cs
[K8]: https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/src/Query.Binding/Owners.cs
[K9]: https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/src/Data.Streaming/TypedStream.cs
[K10]: https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/src/Data.NativeHost/DatabaseOptions.cs
[K11]: https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/src/Interop.Callbacks/CallbackCoordinator.cs
[K12]: https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/src/Data.NativeHost/DataSource.cs
[K13]: https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/src/Interop.Negotiation/EngineMetadata.cs
[K14]: https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/src/Data.NativeHost/HostStreamTransport.cs
[D1]: https://github.com/IzuSharp/Korda-Design/blob/9435043/docs/database/execution-parity-01.md
[D2]: https://github.com/IzuSharp/Korda-Design/blob/9435043/docs/standards/csharp-public-api-and-documentation.md
[D3]: https://github.com/IzuSharp/Korda-Design/blob/9435043/docs/contracts/concurrency-v0.1.md
