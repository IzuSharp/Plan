# DB-Runtime-Compare-01：EF Core / Java 独立源审

## 结论与边界

当前结论是**源逻辑与原 35 类业务契约总体一致，可继续有限正确性准备；不得给予正式比较或 30 分钟验收信用**。本审查仅读取客户端源码、既有 fixture 身份与其他代理已生成的有限回执。审查者没有启动数据库、运行客户端、执行压测、修改客户端源码或任何远端对象。

主快照在 `source/`，逐文件 SHA-256、大小及采集时间在 `source-snapshot.json`。初始采集后，其他代理继续修改源码；已读取的变更快照在 `live-recheck/`，差异身份及机械核对结果在 `review-checks.json`。不把某一个旧快照的审查、旧二进制回执或编译通过转移给尚未冻结的新候选。

权威业务来源是 Korda `36bd5ba169b628ba4d61dd9fe260eaef5ff15599` 的 `benchmarks/db-perf/workload/queries-v3.json`，SHA-256 为 `76443b1c88bf011f57b3c9819dc85a8bedb5376121d3ef2670304f96b6d2aae2`。原 Dapper `LifecycleCases.cs`、共享 `OfferedLoad.cs` 和 DTO/digest 源码同时作为对照。这里允许用户授权的等价 Fluent SQL 调整。

## 需先关闭的风险

| 项目 | 已观察到的事实 | 状态 / 必要动作 |
| --- | --- | --- |
| 128 MiB C# 客户端限制 | 已读取本批 `memory-verification` 的真实有限探针：Stock GC 在 120 MiB 数组时观察到 OOM，但 RSS 为 157,945,856 B；Satori 同时报出配置值 134,217,728，却保留了 201,326,592 B 数组且没有 OOM。两者都没有证明进程总内存 128 MiB 上限。 | **正式比较阻断。** 不可把配置读数当作限制有效；数据库不受此客户端限制。现行 EF RuntimeIdentity/RunReceipt 均为 false，≥1800 秒入口拒绝；Java现行 TimingComparisonEligible 也已固定 false。 |
| Java 业务错误退出码 | 主快照 Main.main 在写出结果后只检查 sticky Oracle；OfferedLoad 捕获普通数据库异常并计 Failed，而这些异常不一定进入 Oracle，因此可能 Failed>0 但进程退出 0。 | 已向 Java 实施代理提出；其确认将保留回执并对 Failed>0 返回非零。需重读最终源并核对失败路径，不能只以“编译成功”关闭。 |
| Java 清理与异常保留 | 主快照 Main.finally 的第一个 close 异常会立即抛出，跳过其余连接；可能覆盖主异常。 | 已提出继续清理所有连接、聚合或附加清理异常。需重读最终源。 |
| Java JIT 诊断标签 | 主快照为 JIT 诊断也固定记录 Route=native-image 和“Serial GC selected at Native Image build”。NativeAot=false 虽然存在，描述仍易误读。 | 已提出按真实运行模式区分 Route/GCContract，并以可用运行时 collector 数据记录诊断。 |
| 新编译配置的证据归属 | EF 已加入 `runtime-async=on`、编译器参数记录、加载程序集的 Async 方法元数据检查；attempt01 两份 SQLite 回执来自此前配置。 | attempt01 只证明其旧二进制。新 Workstation SQLite attempt02 已看到 19 个 Async 方法、全部 35 case 成功；Satori/PG 等新候选需各自新回执。 |

之前读 Program/RuntimeIdentity 时曾向主代理报告 EF 缺少 false 标签；随后完整读取 Measurement 已确认其原本就将 TimingComparisonEligible 写 false，已明确更正。当前不保留这一误报。

## 35 类契约核对

Java `Contract.java` 的 35 个名称、expectedRows、无符号 FNV 值已用脚本逐项对照权威 manifest，全部相同。EF 既有 SQLite 回执中的 35 个 ExpectedResults 也逐项相同；这同时检查了原始固定 oracle 与移植计算 oracle 没有漂移，仍不能替代所有实际 provider/编译组合的执行。

| 契约集合 | 检查结果 |
| --- | --- |
| numeric / text / money / json / wide | 字段序与类型相同；SQLite 将 BIGINT cents 精确转 decimal/BigDecimal，PG保留 NUMERIC(18,2)；JSON 物化为 Channel/Gift；完整 Order 包含 TenantId、Id、CreatedAt、CustomerId、Total、Note、Version、Settings、InternalMemo。 |
| optional-filter / range / null-notes / literal-note | 固定 tenant、customer、时间窗口、LIKE escape、排序与 32 行界限在源逻辑上一致。 |
| left-join / inner-join / three-join | nullable customer 联接语义保留，left join 的空 Name保留，三表按 OrderId/LineId 排序。删除原多余投影属于等价优化。 |
| customer-totals / product-totals / empty-sum | customer NULL 组最后；聚合 HAVING 阈值相同；empty-sum 必须产出一个业务 NULL 标量。EF 用空分组的 nullable default 避免 SUM 被默认变成零；Java直接 SQL SUM，无 COALESCE。 |
| cursor / offset / exists / in-subquery / cte | 复合 cursor 顺序与中点、offset 768、无关联 EXISTS、IN 子查询、cte 的过滤/排序/limit 一致。EF 不保留命名 CTE 的拼写，原契约没有强制物化边界。 |
| window / running-total | 分区与顺序、ROWS UNBOUNDED PRECEDING 到 CURRENT ROW 一致。EF 明确使用参数化 Database.SqlQuery 两处例外；不可宣传全部业务均为 Fluent。Java使用 jOOQ window DSL。 |
| union-all / union / intersect / except | 1..16 与 9..24 的多重集/集合操作及最终顺序相同，行数为 32/24/8/8。 |
| anti-association / nullable-order / raw-sql | NOT IN 的源子查询非空键类型一致；nullable-order 是 **CustomerId NULLS FIRST**，不要与 customer-totals 混淆；raw-sql 本来就是特定的显式 SQL 业务。 |
| related | 32 个父键、全部子 DTO、空父组、子行 ID 顺序与 digest 保留；期望 53 子行。EF 一个连续范围查询；Java一个 IN 查询并按组缓冲；都不是 32 条独立 SQL。 |
| tx-commit / tx-rollback / partial-update / stale-conflict | 与原 Dapper 一样操作 tenant1/order1024；真实全行读、真实 UPDATE、受影响行数检查、恢复提交或回滚、结束事务后完整 persisted-read。检查未修改字段/NULL/version。3/3/3/2 行及 digest一致。EF --verify 另做独立连接检查在计时前，未增加 steady SQL。Java的最后读取使用恢复自动提交后的 retained connection，与原 steady 契约相同。 |
| early-stop | 两实现都请求 1024 行完整 Order 并只消费 3 行后释放 reader/cursor，没有变成 LIMIT 3 或窄 DTO。 |

Digest 检查包括 FNV-1a64 初值与乘数、Int64 小端八字节、nullable presence byte、字符串 UTF-8 字节长度/NULL=-1、exact cents、JSON 两字段与无行分隔符。Java `BigDecimal` 统一 scale=2 后比较完整 DTO，避免以数值相同但 scale 不同误判；所有目标数据在已核对 fixture 的范围内。

## 调度、计时与资源口径

EF `OfferedLoad.cs` 与原共享实现**逐字节相同**，SHA-256 为 `2adb14584476da8b8a49bb2e5db6bd85b136f3823aee5e2f004bc263eb2bc92b`。全局到达序号用于业务轮转；绝对单调时钟计划 `ceil(seconds*rate)` 个到达；队列预分配；不等待容量并明确计 rejected；已接纳任务全部排空；对 attempt/sent/rejected/started/succeeded/failed 做账本恒等式校验。

Java 移植采用预分配有界 FIFO、全局序号、同样绝对到达及拒绝/排空规则，阻塞 JDBC 工作线程与 C# async 的调度机制不同且已有描述。源逻辑里未看到偷偷改为 closed-loop 或重试。每秒 ledger 和四份 histogram 分别保留成功服务时间、成功含排队时间、全完成含排队时间、开始延迟。base2/128 子桶报告上界，非精确分位数。数据产出前仍须验证最终候选短有限调度回执中的 histogram population 与账本一致，不能只验证闭环35操作。

Prepared/persistent 的意思已经分开描述：EF 每worker复用 IQueryable graph，普通 EF 查询缓存；Java每worker复用普通 jOOQ graph，related/transaction 重建，没有保留 JDBC statement，PG prepareThreshold=0；Dapper使用生成 command factory缓存。三者的物理 statement prepare/缓存行为不能因名称都叫 prepared 就宣称相同。现有说明没有作这种错误宣称，后续性能报告应保留此实现差异。

分配采用进程总量，包含驱动、DTO/string/JSON和工具自身；没有凭空声称 framework-only 或 0 B。Java ThreadMXBean 不可用则 null，native allocation 未插桩则 null；Native Image 对这些管理 API 的真实支持仍要看构建后回执。GC 时间保留运行时计数口径，不能称全局停顿直方图。客户端 CPU/RSS 读进程自身；PG 服务端须由外部采集，不能混在客户端。15秒释放后观察是无强制GC的单独阶段。

## 已看见的有限运行证据

- EF SQLite Workstation attempt01：35/35成功，0业务错误，0Oracle错误；旧配置。
- EF SQLite Satori attempt01：35/35成功，0业务错误，0Oracle错误；旧配置。
- EF SQLite Workstation attempt02：新 runtime-async 配置；35/35逐case成功，0业务错误，0Oracle错误，四次计时前独立状态检查，logical connection归零；RuntimeAsyncMethodCount=19；TimingComparisonEligible=false。
- 上述都是既有有限正确性回执，不是审查者执行结果，不代表 C4/C8持续负载、PG结果、JavaNative结果或128MiB约束成功。

相应文件 SHA、程序集 SHA 和完整35项机械核对保存在 `review-checks.json`。任何之后新增的回执或源码变更均需追加审查，不可覆盖旧失败/旧候选证据。

## Java 源码整改复核（08:01 UTC）

追加读取 Java Main 的整改后版本（SHA-256 `b6b67c080a3238e8244bf23d33ac0e3694fb3a37763513c8b2479b619ae1520a`，归档 `live-recheck-02/java/Main.java`）：已确认先写完整回执，然后 Failed>0 抛错并退出2；closeAll逐个尝试全部连接并聚合清理Oracle；Route和GcContract按NativeAot/JIT区分，额外记录真实可用GcIdentity。TimingComparisonEligible仍为false。原三项问题可在**源码层面**关闭；尚未以该源码构建的执行文件或故障注入验证。finally中的清理异常仍可能覆盖普通主异常，这不会误给通过，但异常链保留尚可改善，已告知实施代理。

另已读取 Java SQLite JIT 的已有有限诊断回执：35类验证加64次暖机，OracleFailures=0，35项期望oracle与manifest完全相同，NativeAot=false、TimingComparisonEligible=false。该旧回执包含修正前的Route/GC描述，须按JIT诊断解释，不得回填为新源码或Native Image证据。路径、hash和核对结果见 `review-java-followup.json`。Native Image首轮构建仍未由本审查观察完成，PG也没有给予通过。

## EF attempt02 最终有限验证复核

已追加独立核对 `clients/efcore/verification/attempt02-summary.json` 及每组原始 build/run/result/compiler/admission 文件，结论为：**SQLite / PostgreSQL × Workstation / Satori 四组的当前 runtime-async 候选，通过已执行的有限35类正确性检查与身份绑定；正式内存及性能验收继续阻断。** 这取代前文“PG未给予通过”在 EF 有限正确性层面的状态，保留此前 attempt01 和 Java未完成状态的原事实。

| 有限检查 | SQLite WS | SQLite Satori | PG WS | PG Satori |
| --- | ---: | ---: | ---: | ---: |
| 发布/运行退出码 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| 35个业务各成功一次 | 是 | 是 | 是 | 是 |
| 业务错误 / Oracle错误 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| 35组期望行数/hash与原manifest一致 | 是 | 是 | 是 | 是 |
| 计时前独立连接持久状态检查 | 4 | 4 | 4 | 4 |
| 逻辑连接归零 | 是 | 是 | 是 | 是 |
| 实际 runtime Async 方法数 | 19 | 19 | 19 | 19 |
| 程序集/PDB/运行库hash一致 | 是 | 是 | 是 | 是 |
| TimingComparisonEligible | false | false | false | false |

身份绑定不是仅相信 summary：审查用纯 Python 读取了四份 Portable PDB 的 Document 表，核对了 **64个C#源码文档记录**（每组16个）的 SHA-256 与当前源码，全部相同。另核对所有 summary source/lock hash、五类发布产物 hash、运行回执里的程序集 hash，以及实际 CoreCLR/JIT 文件 hash，全部相同。四份 compiler-args 原始文件均包含独立的 `/features:runtime-async=on` 参数；程序运行反射到 Async method implementation metadata。可复现只读脚本为 `review-ef-binding.py`，细节为 `review-ef-attempt02-binding.json`，运行该脚本不会编译、加载CLR、连接数据库或执行压测。

四组真正的 `--seconds 1800` 准入探针均在约0.15–0.23秒内 exit2，stderr有 `DB_PERF_ADMISSION_DENIED`，没有 `DB_PERF_RESULT`。两SQLite探针指定的新数据库文件均未创建。PG探针使用拒绝连接目标；Program源码在 VerifyDataset/打开会话前返回，未开展数据库操作。此验证证明拒绝路径生效，**不是四次1800秒运行**。

这些有限检查只覆盖单worker、一次35类验证+64次暖机+35次闭环操作；没有声明C4/C8排队/拒绝/持续30分钟、取消异常、内存上限或性能对齐。实际 Satori 是11.0.2-ci及不同CoreCLR/JIT，不能将今后所有差异只归因于GC。现有128MiB限制阻断与明确SQL窗口例外仍须在最终对外叙述中保留。
