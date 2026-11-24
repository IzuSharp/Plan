# DB-Perf-01：并发工作区固定快照的独立审查

## 结论与证据边界

本次审查发现一项会直接改变并发测量含义的代码问题：Korda 的 `per-operation` 会话模式始终额外保留每个 worker 的初始化物理会话，在 `MaxConnections = concurrency + 1` 下，只剩一个连接槽可供测量请求使用。除此之外，快照还处于基准前置实现阶段：Korda 有 30 个读取路径的分支，直接 C++ 只有 5 个投影，Dapper.AOT 只有两条能力探针；同名 `mixed` 不代表相同负载。当前快照不能支持四列混合负载横比、完整框架 0 B 或 8 段长测验收。

这是一份**未提交、开发中的中间快照审查**，不是对已合并代码的缺陷公告。原工作区可能已在快照之后修复或补全相关部分。本次只读固定快照，没有读取其后持续变化的工作区，没有编译、启动数据库或运行负载，也没有新增任何有效长测信用。

- 快照捕获时间：`2026-11-24T09:25:45.953000+00:00`。
- 基线提交：`771bc77cbd68d3f932b99ed2497c0697bbba5f02`。
- 审查对象：`/workspace/scratch/754bc732518e/concurrent-snapshot-001`。
- `snapshot.json` SHA-256：`9347eabf58bde478402da2c2cc6860e5134131a0ac01c9b72b1774577fef7a5d`。
- 对清单内 23 个文件重新计算 SHA-256，全部与二次读取稳定快照的记录一致。
- 文件完整 SHA-256、行数、补充基线源码身份及静态清单核对结果见同目录 [concurrent-harness-snapshot-001.sources.json](concurrent-harness-snapshot-001.sources.json)。下文文件与行号均指此固定快照；仅明确标注的物理会话契约引用固定 main 源码。

优先级中，P1 表示应在使用相应数据作正式结论之前解决；P2 表示应在完整 campaign 或验收记录之前补足。下文将实际代码问题与尚未完成的能力分开。

## 1. P1 · 每次操作取还连接的并发模式被初始化会话串行化

**位置：** `managed/Korda/Measurement.cs:21–23, 34–38, 148–157, 185`；`managed/Korda/Program.cs:13–18`。以上路径均位于 `benchmarks/db-perf/` 下。

`Worker.Create` 无条件调用 `source.OpenSessionAsync()`，并把得到的会话存入 `_session`。选择 `--session per-operation` 后，`Execute` 不使用它，而是再打开一个临时会话，完成后归还。所有初始化会话直到测量结束才释放。与此同时，构造数据源时的上限是 `options.Concurrency + 1`。

因此 N 个 worker 在开始测量前已经占用 N 个物理会话；每次操作最多只能争夺剩下的 1 个槽。`concurrency=8` 并不测八个并行数据库请求，而是八个 worker 争夺一个可用槽的行为，且会把人为池等待、等待对象分配和唤醒开销归入结果。它会直接污染吞吐爬坡、尾延迟及每次操作分配。

这个判断所依赖的产品契约来自固定 main：`src/Data.NativeHost/DataSource.cs:89–102` 说明 `OpenSessionAsync` 取得独立物理会话；`src/Data.NativeHost/DataSession.cs:7–18` 说明会话拥有一个物理原生会话。两个文件在本会话基线 worktree 中未修改，SHA-256 记录在 sources JSON 中。

**建议：** 用有明确所有权的初始化会话构建与 source 绑定的计划，随后在计量前释放；仅 `persistent` 模式保留每个 worker 的物理会话。保留源容量的同一公开契约，不通过无说明地扩大一倍池容量掩盖初始化所有者。短验证应记录测量前实际持有会话数和测量期间最高在途请求数，证明 `per-operation` 下 N 个可用槽确实能够工作。

## 2. P1 · 同名 mixed 在 Korda 与原生程序中执行不同负载

**位置：** `managed/Korda/Workload.cs:7–11, 73–79`；`managed/Korda/AdvancedCases.cs:36–105`；`native/main.cpp:198–218, 513–523, 535–540`；`workload/queries-v1.json:20–260`；`managed/DapperProbe/Program.cs:48–62`。

静态核对得到以下范围：

| 路线 | 已存在的执行实现 | mixed 的实际含义 | 此快照可据此证明的范围 |
| --- | --- | --- | --- |
| Korda | 5 个基础投影及 25 个高级读取分支 | 固定顺序遍历 30 个名字，每个 worker 从同一个名字开始 | 存在相应代码；没有附带可据此审定的逐项执行收据 |
| 直接 C++ | `numeric/text/money/json/wide` | 固定顺序遍历 5 项，拒绝额外契约项 | 五投影对照实现 |
| Dapper.AOT | 一条键查询和一条 32 行流式查询 | 没有 mixed、计量循环或并发入口 | 真实 ORM 能力探针源码 |

Korda 的 `mixed` 包括联接、聚合、CTE、窗口、集合、关联加载等，而原生 `mixed` 仅仅改变同一订单范围查询的投影。即使数据库、时长、并发和参数名字相同，这两份收据也不能计算相对原生差距。Dapper 的 `build_orm.py:21,27–29` 提供 `--kind benchmark` 选择，但本快照没有它期望的 `managed/Dapper` 目录；不能把这个参数视为第四列已经实现。

**建议：** 以带哈希的共同 case/参数/权重清单冻结同一个混合负载，运行前核对四列支持集合和预期每类操作数。五投影小范围对照可继续独立使用，但命名和报告必须维持五投影范围，不能与 Korda 的 30 项 `mixed` 汇总到同一行。

## 3. P1 · 当前调度只测闭环容量，不能建立相同到达负载的前后尾延迟

**位置：** `managed/Korda/Measurement.cs:46–69, 75–90, 198–204`；`managed/Korda/Options.cs:5–20, 31–46`；`native/main.cpp:535–552, 594–601`。

两个计量循环都是完成上一个操作后立即发起下一个。时长模式的 `Planned` 直接赋值为实际 `started`；没有独立计划到达时刻、到达速率、排队时间、未能发起的截止时间或拒绝计数。因此它的 planned/start/complete 数字可以描述闭环内部守恒，却无法显示因为消费者变慢而没有生成的外部请求。

延迟直方图从实际开始执行起计时，且仅包含成功操作。它可以报告该闭环并发下的成功服务时间分布；不能作为“冻结同一可持续负载”的响应尾延迟。若优化后更快，闭环自然施加更大负载，直接比较 p99 会混入负载变化；若饱和时更慢，到达数也自动减少，等待的需求没有出现在统计里。

这里不是字段造假：代码明确输出 `closed-loop; ... no external arrival rate`。问题是尚无完成用户要求的调度路线。

**建议：** 保留闭环作为容量诊断，另加固定计划时刻的有界负载入口；记录 scheduled、started、成功、失败、拒绝、逾期未开始和重试，以及 scheduled-to-complete 与 service 两套延迟。最大可持续吞吐应使用同一错误率和尾延迟门槛搜索，并冻结独立的前后延迟负载。所有最终汇总应验证计数守恒和每类 case 的数量。

## 4. P1 · 分配计量是合格的原始总量入口，尚不是框架自身 0 B 归因

**位置：** `managed/Korda/Measurement.cs:159–174, 200–204`；`managed/Korda/Workload.cs:77, 92–127`；`managed/Korda/Models.cs:17–59`；`managed/Korda/AdvancedCases.cs:271–283`；`tests/Data.Streaming/AllocationProbe.cs:10–12, 123–133, 150–180`。

应保留的正确做法：测量使用 `GC.GetTotalAllocatedBytes(precise: true)`，记录 before/after 累计值、代际 GC 次数、操作数与行数；主要计量结构在边界前建立；每次真实查询的异步消费状态与 DTO 物化保留在端到端总量中。它没有用线程局部计数漏掉回调线程，也没有通过四舍五入或减去空驱动宣称零分配。

尚缺的归因路径很具体：

- 记录只输出端到端 `AllocatedBytes` 及 B/成功操作、B/行，没有独立的框架 B/操作、B/补充批次或业务输出累计字节。
- `--empty-driver` 直接返回预先计算的 `OperationResult`，不产生 DTO、JSON、字符串和真实 I/O 挂起。减去它后仍混合业务物化、消费者异步状态与框架成本；它也没有证明工作线程上各项分配来自何处。
- `related` 使用 `OrderBy` 排序返回的子行，排序对象与缓冲属于基准消费者的工作，必须与框架关联加载分配和业务结果集合分开标注。这个排序在测量区间内。
- `ActualStreamSuspensions` 仅观察 `MoveNextAsync`/`DisposeAsync` 是否未完成，不能证明所有计划提交、绑定、连接获取和事务的挂起路径都覆盖，也没有补充批次数的独立计数。
- 内部 `AllocationProbe` 的 `sync-inbatch` 窗口明确从第一行之后开始，排除了流构造、获取批次、解析及关闭；synthetic transport 的结果不能转移为两个公开 provider 的全路径结论。

快照已经诚实输出 `framework-only attribution unproven`，内部 probe 也写明 `publicProviderAcceptance=false`；这些标签必须保留。**建议：** 按实际公共调用链补业务输出归因、独立消费进程的分配栈或隔离实验、每次查询/每批/每行累计原始计数，再给已证实的生产路径增加短回归门槛。任何一个内部窗口得到 0 B，都只能覆盖该窗口。

## 5. P2 · 30 个名字主要是读取覆盖，关键状态变化语义未进入工作负载

**位置：** `managed/Korda/Workload.cs:7–11`；`managed/Korda/AdvancedCases.cs:43–104, 118–249, 251–285`；`managed/Korda/Dataset.cs:20–92`。

30 个名字均能在源码中找到分支，不宜把它们称为“只有目录、没有实现”。但当前覆盖不能写成 30 个完整业务场景均已实际通过：

| 读取类别 | Korda 分支名 | 当前边界 |
| --- | --- | --- |
| 基础及宽窄物化 | numeric、text、money、json、wide | 5 项存在完整读取与摘要逻辑 |
| 过滤及 NULL 排序 | optional-filter、range、null-notes、literal-note、nullable-order | optional-filter 永远 `WhereIf(true)`，没有未启用分支或不同参数组合 |
| 联接 | left-join、inner-join、three-join | 有两表及三表读取 |
| 聚合 | customer-totals、product-totals、empty-sum | 有 HAVING 与空 SUM |
| 分页 | cursor、offset | 有复合游标与 3/4 深度 offset |
| 子查询 | exists、in-subquery、anti-association | 有相应读取实现 |
| CTE、窗口、集合 | cte、window、running-total、union-all、union、intersect、except | 存在 Fluent 构造分支 |
| SQL/关联 | raw-sql、related | raw-sql 与 text 读取相同业务字段；related 是批量关联 API |

事务仅用于 `Dataset.Initialize` 的种子写入。测量分支没有事务读写、部分更新、乐观并发冲突、显式回滚、取消或提前结束枚举。`Read` 虽有 `stopAfter` 参数，所有调用均采用默认值；Dapper 唯一 cancellation 参数是 `CancellationToken.None`。静态搜索 `BeginTransaction/Commit/Rollback/Update/Delete/Insert` 也未发现测量内状态变化分支。

此外默认 `Rows=32`、`OrdersPerTenant=1024`；可配置更大值并不等于已经验证流式大结果。当前表的声明范围应是“30 个读取入口的源码覆盖”，执行通过需有二进制身份、输入和实际收据；本快照没有提供这些记录。

**建议：** 给状态变化用例明确前置/后置持久化断言和不相互干扰的复位规则，分别标识 Fluent 与 SQL 路线。取消和提前结束必须验证最终归还及随后可正常复用；不能把初始化事务计入该业务覆盖。

## 6. P2 · SQL、参数和执行计划尚未形成跨路线核验链

**位置：** `managed/Korda/Workload.cs:29–50, 70–79, 82–103`；`managed/Korda/AdvancedCases.cs:21–24, 86–104, 253–258`；`managed/Korda/Measurement.cs:183–184, 209–211`；`native/main.cpp:198–218, 451–488`；`workload/manifest.py:24–69`。

五投影 catalog 含按顺序排列的参数、值、列和摘要；本次在内存中重新执行其生成函数，解析后的 JSON 与固定文件完全相等。其整数、NULL、UTF-8、金额 cents、typed Settings 摘要设计也与 Korda/原生消费逻辑相符。直接 C++ 会检查 SQL 重构一致、列别名和参数数量，并取完结果和验证摘要。这些是可复用的基础。

但 Korda 程序不读取该 catalog，参数及预期值另在 C# 中实现，没有跨路线冻结校验。`ActualDiagnosticSql` 记录构造时的 `ToSql()`，没有逐项有序实际绑定值。`related` 的对应值是一段英文解释而非实际 SQL；它无法用于检查 UNION ALL 参数布局和执行计划。快照没有 EXPLAIN/计划捕获入口。Dapper 两条 probe SQL 也不是五条 catalog 的执行适配器。

**建议：** 先用短正确性阶段导出全部路线的实际 SQL、有序参数和列契约、行数/摘要以及数据库执行计划，绑定同一个 workload 哈希；`related` 的说明应另列，不能占用 actual SQL 字段。SQL 或计划不同的独立 ORM 结果保留原样，另增加相同 SQL 的分层对照。不能仅凭查询名字、数据集元数据或摘要相同宣告执行计划相同。

## 7. P2 · 原生程序的产品协议模拟层应与直接原生最佳复用层分开

**位置：** `native/main.cpp:44, 349–375, 437–486, 595–606`；`native/README.md:35–65`。

原生程序的默认值是 `physical=per-operation`、`confirmation=product`。PostgreSQL 每次读取进行 prepare、describe、前置 Sync、execute、结束 Sync，共五个协议提交；复用语句且 `drain-only` 的实现也已经存在。README 明确区分这些层，并且物理 RTT 字段为未测量，没有把 poll 次数当作网络往返。

同 SQL、同结果、相同释放语义不自动要求直接 libpq 消费者重复 Korda 内部用于所有权确认的额外 Sync。若只把默认产品模拟层放到“直接原生 C++”主列，会把额外内核/协议成本共同加入两边，从而缩小所呈现的差距。反过来，把原生物理语句复用与 Korda 仅复用查询形状混称为同一种 prepare 也不准确。

**建议：** 正式报告明确 query construction、compiled shape reuse、physical statement reuse 和 protocol confirmation 四项命令值。原生直接路线与产品协议模拟路线分别报告；解释剩余差距时用分层数据定位额外提交的成本。没有实际网络跟踪时继续把 RTT 标为未测。

## 8. P2 · ORM 能力探针使用了真实 ORM，但生成器和完整能力证明仍须补齐

**位置：** `managed/DapperProbe/DapperProbe.csproj:12–23`；`managed/DapperProbe/Program.cs:13–15, 20–32, 43–69`；`managed/build_orm.py:34–56`。

这里确实通过公开 Dapper 泛型 `QueryAsync<ProbeRow>` 和 `QueryUnbufferedAsync<ProbeRow>` 访问真实 provider，声明 `[module: DapperAot]`，并在运行时拒绝动态代码；不能误归类为纯 SQL 驱动探针。SQLite 也校验实际映射库的路径与 SHA，并输出 compile options。

不过这份固定快照只给出源码，没有实际 publish 日志、生成的拦截器或执行收据。`build_orm.py` 仅在指定 generated 目录存在时复制，既不要求该目录存在，也不检查这些调用点是否产生拦截器或保存 generated 文件哈希。项目未带依赖锁；脚本保存解析后的 assets 和包哈希，有助追溯该次构建，但不等于后续 restore 自动重现同一依赖图。

**建议：** 在真实 Native AOT 最小运行通过后，把实际生成路径、拦截器对应调用点、锁定依赖图与哈希变成前置门槛；逐项扩展成熟 ORM 可支持的业务查询，缺项明确记录。`QueryUnbufferedAsync` 的 API 名称本身不证明底层真的异步挂起，仍需实际观察完成状态。此项不否认本会话另行完成的独立 ORM preflight；两组源码/二进制身份不同，不能替代本快照的证据。

## 9. P2 · 资源采样可复用，但四列需要的排空/空闲及原生分配记录不齐

**位置：** `run.py:30–61, 110–145, 164–167`；`managed/Korda/Measurement.cs:122–142, 174–188, 203–211`；`native/main.cpp:557–588, 607–617`。

控制器正确分开客户端与 PostgreSQL 进程树，保留 user/system ticks 和采样 RSS/PSS，最终 wait4 保留客户端整个生命周期 CPU 与峰值 RSS。它也明确说明生命周期包含启动/暖机/排空，应按客户端收据时间过滤稳态样本。

具体缺口如下：Korda 收据的 `ProcessAfter` 在关闭 worker/source 前读取，之后仅保存 native owner 数；因此没有关闭后的进程 RSS/PSS/保留量或稳定空闲 CPU 窗口。控制器在子进程退出后结束采样，不能事后补出已经退出进程的空闲保留量。原生入口已有排空及 idle 观测，但 `nativeAllocationCalls/nativeFreeCalls/nativeHeapPeakBytes` 明确为 null；glibc 当前块量与 SQLite allocator 高水位不能替代全进程原生堆峰值。

所有路线目前只保存每 worker 第一条异常字符串；没有完整错误分类直方图。Korda 失败后继续下一次操作，原生失败后停止该 worker（`Measurement.cs:65–69` 对比 `native/main.cpp:545–552`）；在出现故障的长测里，后续施加负载和有效时长含义不同，必须统一或明确区分，不能只拿成功 ops/s 比较。

**建议：** 在同一可计量资源上加入等长、预定义的 before/after idle 和 drain 保留窗口；按实际阶段边界汇总客户端及 PostgreSQL 服务端 CPU，保留原始树级样本以处理退出子进程；另用可归因的原生分配观测记录峰值及分配/释放，不从 RSS 推导。错误发生时采用一致的业务重试/停止策略并保存全部分类计数。

## 允许复用的部分与验收判断

当前源码适合继续作为短正确性、能力探针和定位热点的基础：外部 PackageReference 构建、AOT 运行时守卫、已加载原生库身份、完整 typed 字段摘要、原始全进程累计分配数、显式未证明标签和独立客户端/服务端采样都值得保留。`managed/build.py:28–46, 58–92` 还隔离了消费源码、限制 Korda 包图并记录实际产物哈希。

不得把它升级为已完成验收的依据：

| 验收项 | 本次审查结论 |
| --- | --- |
| 至少 24 个语义业务案例 | Korda 有 30 个读取入口的源码，完整状态变化矩阵及逐项实测未证实 |
| 四列 × 两库共同负载 | 未实现；native 5 项、ORM 2 条 probe，mixed 不同义 |
| 全框架正常路径 0 B | 未证实；总量计量有基础，框架归因与公开 provider 完整覆盖不足 |
| 真异步/高并发的零分配覆盖 | 未证实；per-operation 并发还受第 1 项影响 |
| 固定到达负载尾延迟/饱和及恢复 | 未实现；现有是明确标注的闭环 |
| 8 段、至少 4 小时有效混合长测 | 本次没有运行或接受任何一段；控制器本身设 `longRunAcceptance=false`、`hostQualifiedForLongRuns=false` |
| 生产合并/公开 preview | 本审查不作判断；固定快照不是提交或发布身份 |

下一次审查应针对新冻结候选重新读取相关哈希与命令，再逐条关闭以上问题；不要把本报告的中间状态外推为原会话后续代码、main 或实际发布包的状态。
