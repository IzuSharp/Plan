# tail-completion06：真实包消费者的完成派发机制闭合

作者：`/root/worker_boundary_review`（本候选实施者，独立审查由另一个代理完成）。范围是新组合的因果机制门禁；本报告没有普通 CPU、延迟、分配、RSS 或最终对齐信用。

**四条真实 NuGet PackageReference / Release Native AOT 路径均通过：tail06 使符合条件的预登记完成回调与 GetResult 进入本请求自己的 setter 动态区间；原来每个查询的 33 次 coordinator offer/dispatch 没有减少。** 因此观测支持“省掉 core completion 的异步交接”这一具体假设，不支持“原生任务或 coordinator 调度次数一起减少”。下一步必须由冻结普通消费者的交错 A/B 判定实际成本及回退。

## 身份、条件和业务等价

普通对照仍是 integrated05 `2ea67ce1902f330679c3ebff4d6d5733be20f69c`；普通 tail06 冻结为 `4a9e4435ea5c836be44fb00dc4219301567072c6`。本次执行的是两者各自独立的诊断镜像 `197f0d3444cf3cfc120982273d48d1dcf74f60db` 与 `ba4e7ec9bf93ad313dbbb167457189a5f95429da`，包版本分别为 `0.1.0-parity06diagbefore.1` 与 `0.1.0-parity06diagtail.1`。诊断 overlay 只放在独立分支，不进入产品、CI 或普通消费者。

四个消费者均使用实际 PackageReference、实际生成的 TextRow reader、匹配符号的 AOT ELF，以及同一 provider 的相同原生库。`mechanism-01/input-identities-before.json` 记录每个消费者 98 项文件 SHA；每个子进程之后及全部结束后重新读取，全部相同。同库的 before/tail 15 个业务源码文件与 TextRow 生成代码字节完全一致。包、依赖、构建回执、生成代码、ELF、debug 与 loaded native 分别绑定。精确文件与 SHA 汇总在 `mechanism-review-index-01.json`，实际命令/PID/startTicks 位于各格 `process.json`。

每格独立进程、4 次暖机与 16 次稳态业务，闭环、并发 1、prepared/persistent、1000 行、批大小 32；SQLite before→tail 后，PostgreSQL before→tail 串行运行。客户端 CPU 0–3，PG CPU 4–7，驱动 CPU 8。没有修改默认运行时，没有 profiler；两次 fixture 初始化不启用日志。没有执行全部 35 类业务或最终 30 分钟验收。

DTO 是 `TextRow(long Id, string Note)`，tenant 参数与 LIMIT 参数保持一致。两库 SQL 都选择 `orders.Id` 与 `orders.Note`，按 TenantId 过滤、Id 排序、LIMIT 1000；参数占位符分别是 `?` 和 `$1/$2`。同库 before/tail 实际 SQL 完全相同；每次结果均 1000 行，digest `8271652422540811358`。四格各 16 成功、0 业务错误、0 重试、0 oracle 错误，且现有八类 native owner/operation/source/session/cursor/buffer/channel/completion 终态计数均为 0。每格实际 SQL execution 增量 16。PG 现有 ProtocolSubmissions 计数增量 64，SQLite 0；这些是已有 native 计数器，不能改名为逐个线上的 Parse/Bind/Execute 消息或 OS 等待次数。

## 直接观测与有边界的推断

下表都是每格 16 次稳态业务的总数，不是百分比换算的 CPU 时间。

| 观测 | SQLite before | SQLite tail | PG before | PG tail |
| --- | ---: | ---: | ---: | ---: |
| 成功业务 / 独立 cursor controller | 16 | 16 | 16 | 16 |
| pull 请求（每业务 32） | 512 | 512 | 512 | 512 |
| OnCompleted 登记 | 507 | 474 | 511 | 512 |
| 已正常登记返回且早于 setter 的 eligible 请求 | 506 | 474 | 511 | 512 |
| continuation 与 GetResult 在自身 setter 内 | 0 | 474 | 0 | 512 |
| 登记/完成区间交叠，保守 eligible 未知 | 1 | 0 | 0 | 0 |
| 未登记，已完成结果直接领取 | 5 | 38 | 1 | 0 |
| 已直接计数的 coordinator offers | 528 | 528 | 528 | 528 |
| 已直接计数的 coordinator dispatches | 528 | 528 | 528 | 528 |
| 直接 native prepare / run / take（各自） | 512 | 512 | 512 | 512 |
| 由实际条件及锁定 runtime/ELF 推断的 core completion enqueue | 507 | 0 | 511 | 0 |

每个业务实际为 32 个 pull 与 33 个 coordinator turn。四格均没有 rejected offer、skipped execute 或 queued-key / dispatch-entry-key 的 generation 差异。额外 turn 在最后 generation 的 GetResult 后可见；本次没有用单独钩子为它指定更细的高层调用原因。它的存在及未减少是直接计数结果。prepare/run/take 是 pull 边界次数，不等同 SQL 次数、全部产品 FFI 次数或时钟探针次数。

所有实际登记的 flags 都是 0，effective scheduler kind 都是 0；本次没有请求 ExecutionContext flow，也没有捕获 SynchronizationContext/TaskScheduler 的业务样本。`registrationFlags` 与 `FlowExecutionContextRequested` 已在每请求及汇总保留。一般情况下 requested flag 不等于“捕获了非空 ExecutionContext”；这里只能据实说本次 flags 为 0。

SQLite before 的一个真实交叠样本没有被强行归入 eligible。其 before 策略和实际不在 setter 内的回调仍支持 enqueue 路径推断。两个 after 样本没有 observed overlap；其中 SQLite after 更多结果在登记前已经完成。四次短运行的登记比例不作稳态概率预测，也不能直接外推普通消费者中的队列节省百分比。

`actualInline` 必须同时满足同 controller/generation/version、同 managed TID 与 Linux TID、同 TLS setter frame、continuation 与 GetResult 的 entry/exit 全在本 setter entry/exit 以内。仅同线程不算 inline。每请求的 native Run 返回、完整 execution frame 结束、take、六项 retirement obligation 归零均早于 setter。每个 generation 的 token、一致 owner、唯一消费与正常成功状态也逐条校验。

## 源码、机器码与计数边界

`HostPullController` 的普通尾部 publisher 在 gate 内只验证 generation/version/已发布状态，离开 gate 后才调用 setter；setter 之后没有产品状态访问。`CoordinatedCallback.Execute` 与三个 Resume 的调度/失败处理已先结束，最后才用局部不可变 payload publish。捕获的 scheduler/continuation 抛错不再回流旧 generation 的 SchedulingFault。原有 native Run/Abandon 借用 lease 与控制计数语义保持不变。

独立机器码审查 `independent-machinecode-review-01/README.md` 对四个 actual ELF、匹配 `.dbg`、Build ID 做了 48 个只读命令。实际 Host setter 跳到 core SignalCompletion；无 context 分支比较异步 flag 后，false 直接 delegate jump，true 调用实际 UnsafeQueueUserWorkItem。before 构造函数实际存 true，tail 没有该 store。实际 core OnCompleted 的 late registration 分支仍 queue。源码映射锁定 VMR `297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f` / runtime `deae2e32bf0e018e09d64597b7c59b62b73bb3ce`。

实际共享机器码符号名含 `ManualResetValueTaskSourceCore<Int64>`，审查跟随真实 call target；这不表示业务 DTO 或结果类型改为 Int64。AOT code sharing/folding 是对此命名的有依据解释，不能用预期泛型名称替代实际地址。

这里没有在 runtime 队列入口插桩。因此 507→0 与 511→0 是“原始事件条件 + 实际源码/机器码分支”的推断，不是独立的 ThreadPool enqueue 指令计数；更不是 OS 唤醒、LifoSemaphore 等待、RhSpinWait 采样或线程排队时间。直接 coordinator counter 与这项推断保持分列。

诊断 trampoline 改变了 delegate identity；锁定 ThreadPool 实现对 async-state-machine delegate 的特殊识别可能因此不再适用。加上全局日志锁、时钟 PInvoke、TLS frame 与额外对象，诊断会改变实际调度和分配成本。`requests.json` 保留观测到的 elapsed/thread CPU 区间，但它们可重叠且包含插桩；本报告不相加为独占阶段成本，不报告任何诊断 CPU/延迟/分配收益。原业务回执 `TimingComparisonEligible=true` 原样保留，外层 plan/analysis/summary 的 `ordinaryTimingCredit=false` 明确取消普通比较信用。

## 严格解析、原始记录和关闭

全部进程日志都有完整 footer；记录数分别为 13550、13418、13562、13566；drop、clock error、active setters/continuations/registrations/results/executions/offers、pending offers 和 recorders 全部 0；没有 `.late` sidecar。四个 header PID 与实际 Popen PID/startTicks 绑定。每条 seq 连续且唯一；全局文件写入先后不被误当为跨线程单调时间顺序。逐线程时钟单调，动态 frame 配对完整，所有 footer clock call 数与 event 数一致。全进程 642 pull = 2 个 metadata pull + 4×32 暖机 + 16×32 稳态；稳态筛选使用真实业务 monotonic window 与 request identity。

旧 `analyzer-controls-01` 的 22 个控制和原源 SHA 保留在 `analyzer-source-v1`。`analyzer-controls-02` 在保留原有严格门禁的基础上增加 EC-request-only 和真实 OnCompleted 返回/ setter 区间交叠控制，共 24 项通过。旧的 before-cross-thread-overlap 仅测试 delivery 与 setter 跨线程交叠，没有冒认它覆盖注册区间交叠。没有实际 workload 失败需要重跑或豁免；准备阶段发现的 PG URI query 不受支持问题在首次启动前修正，未重复已知失败。v1 driver 源仍保留。

PG fixture 由 `pg_ctl -w` 启动与 fast stop；停止返回 0、postmaster.pid 消失，后续 PID 73 / startTicks 1927370 在当前 /proc 不再可见。证据是 `mechanism-01/postgresql/postgres-owner.json` 与命令日志；这不是直接 postmaster wait4 回执，不能声称子进程 CPU 已完整累计或给服务端成本信用。该诊断 fixture 目前留存数据文件，所有 DB/消费者已停止。

## 决定与恢复点

候选已通过产品正确性、具有辨别力的 before 负控、四个真实包机制观察及实际源码/机器码对应。此处完成的是机制门禁；独立 raw 审查另存相邻目录。当前唯一合理下一步是用 root 已冻结的普通消费者交错 A/B 检查 CPU、分配及尾延迟是否真的改善，并覆盖已有明确回退风险。不追加广泛采样，不更改运行时/SQL/批大小，不修改当前四个诊断 ELF。

如果普通收益落入噪声或回退/契约风险使其不可接受，就保留这个已证明的机制结果而拒绝产品方案；机制成立本身不等于值得采用，更不等于已经对齐 Dapper.AOT。最终四段 30 分钟验收和剩余 6–10× CPU 差距仍由整体任务处理，不能从这里标为完成。
