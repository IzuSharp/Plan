# DB-Runtime-Compare-01：四种实现、双库八段 30 分钟实测

## 完成结果

按用户最后确认的 **C# 192 MiB GC 配置、无需 cgroup** 执行完毕。
四种实现分别运行 SQLite 和 PostgreSQL，八段串行，**每段实际提供负载至少 1,800 秒**；
暖机、排空和连接释放后的空闲观测另计。没有继续优化 Korda。

执行时间为 **2026-11-28T00:35:25.184245-08:00 至 2026-11-28T04:42:27.341481-08:00**（America/Los_Angeles）。
合计计划 47,520,000 次业务、成功 **47,395,943**、拒绝 **124,057**，
业务错误和结果 Oracle 错误均为 **0**。所有格的 35 类结果、数据恢复、连接归还、客户端退出均通过核对。

原始严格状态为 **7 passed、1 failed**。第 02 格 Dapper/PostgreSQL 完成了完整业务窗口，
但请求 15 秒的释放后空闲实际为 **14.997119729 秒**，少 2.880271 毫秒。
独立评审仅接受这份精确 SHA 绑定记录的业务窗口比较资格，原始 `failed/released_idle`、
原始时长和严格错误原样保留，未增加通用容差、未改写成功、未重跑该格。
详见 [偏差评审](campaign/analysis/02-idle-deviation-review.md)。

## 本次数据支持的结论

1. 在固定到达率下，四种实现的成功吞吐接近。Dapper.AOT 两库的拒绝数、OS 报告的生命周期 maxRSS 和释放后 RSS 最低。
2. EF Core Workstation 相对 Dapper 的客户端 CPU/成功业务，本次 SQLite 高 **4.61%**、PostgreSQL 高 **10.56%**；全进程托管分配 **B/成功业务** 分别约为 **3.08 倍、3.40 倍**。
3. Satori 相对 Workstation，本次未观察到更低的 CPU/成功业务或更低的 RSS；PostgreSQL 成功业务服务 p99 和计划到完成 p99 较低。运行时、JIT 版本和实际 GC 可用内存也不同，不能把这些差异全部归因于 GC。
4. Java Native 相对 Dapper，本次 SQLite CPU/成功业务低 **0.70%**，PostgreSQL 低 **9.38%**。SQLite 的 0.70% 差值没有重复实验支持，不能称为稳定优势；Java 的进程内存仍高于 Dapper。
5. 所有格均有拒绝。本轮是原压力条件的一次长测比较，**没有测出最大持续吞吐、开始拒绝的压力拐点或零拒绝时的成本**，也不作统计显著、性能已对齐或 GC 单因素因果结论。

完整派生值、每类成功构成和来源在 [离线报告](campaign/analysis/offline-01/report.md)、
[summary.json](campaign/analysis/offline-01/summary.json) 和 [35 类分布](campaign/analysis/offline-01/case-distribution.md)。
以下表格均由同一份 summary 数据生成。

## 吞吐、拒绝与客户端成本

成功吞吐 = 全部成功业务 / 消费者 EffectiveSeconds，包含已准入业务的排空时间。
CPU 为业务窗口前后全进程 user + system 差，包含客户端、驱动、DTO、校验和进程内压测调度成本；
没有扣除猜测的工具开销。托管分配同样是全进程计数，不能据此宣称框架本身分配多少或零分配。
所有格业务错误/Oracle 错误均为 0；拒绝计入下表，不当作已执行业务错误。


### SQLite

| 实现 | 成功数 | 拒绝数 | 拒绝率 | 成功/s | CPU ms/成功业务 | 托管分配 B/成功业务 |
| --- | --- | --- | --- | --- | --- | --- |
| Dapper.AOT | 5,395,182 | 4,818 | 0.089% | 2,997.32 | 0.565287 | 7,457.71 |
| EF Core / Workstation | 5,383,490 | 16,510 | 0.306% | 2,990.81 | 0.591321 | 22,967.24 |
| EF Core / Satori | 5,378,653 | 21,347 | 0.395% | 2,988.13 | 0.599472 | 23,127.72 |
| Java / jOOQ Native | 5,385,710 | 14,290 | 0.265% | 2,992.05 | 0.561326 | 不可用 |

### PostgreSQL

| 实现 | 成功数 | 拒绝数 | 拒绝率 | 成功/s | CPU ms/成功业务 | 托管分配 B/成功业务 |
| --- | --- | --- | --- | --- | --- | --- |
| Dapper.AOT | 6,470,481 | 9,519 | 0.147% | 3,594.70 | 0.456513 | 7,352.88 |
| EF Core / Workstation | 6,461,859 | 18,141 | 0.280% | 3,589.91 | 0.504730 | 24,972.80 |
| EF Core / Satori | 6,459,584 | 20,416 | 0.315% | 3,588.64 | 0.508141 | 25,361.66 |
| Java / jOOQ Native | 6,460,984 | 19,016 | 0.293% | 3,589.43 | 0.413672 | 不可用 |


Java 的实际运行时不提供所需分配计数，因此保持 `null`，不能填成 0。
本轮正式计时没有原生分配插桩，原生分配及框架/驱动/DTO 的独立归因也保持不可用。

## 内存与 192 MiB 的实际含义

三条 C# 路径均设置 `DOTNET_GCHeapHardLimit=0xC000000`，即 201,326,592 B。
没有施加 cgroup。Workstation 正式回执报告 GC 可用内存为 201,326,592 B；
Satori 虽报告相同配置值，实际 GC 可用内存为 **10,451,427,328 B**。
本轮未证明 Satori 的 192 MiB 堆边界受到强制执行，不能把配置值解释为进程总内存硬限。
Dapper 原消费者没有记录相应的启动 GC 可用内存字段，报告未用独立探针代填。
历史 128 MiB 探针保留原身份，不冒称 192 MiB 验证。

PostgreSQL 服务端不受 C# 客户端预算约束；历史 `shared_buffers=128MB` 是数据库缓存设置，
不是数据库总内存上限。SQLite 原生引擎在客户端进程内，其驻留内存包含在客户端 RSS。
Java 没有施加这项 C# 预算。

| 实现 | 数据库 | OS wait4 生命周期 maxRSS MiB | 消费者结束快照自报峰 MiB | Observer 稳态采样峰 MiB | 释放后 RSS MiB |
| --- | --- | --- | --- | --- | --- |
| Dapper.AOT | sqlite | 33.07 | 31.36 | 31.43 | 28.76 |
| Dapper.AOT | postgresql | 42.22 | 38.05 | 38.35 | 34.81 |
| EF Core / Workstation | sqlite | 130.86 | 130.86 | 131.39 | 107.33 |
| EF Core / Workstation | postgresql | 132.93 | 132.93 | 133.56 | 98.98 |
| EF Core / Satori | sqlite | 194.61 | 194.61 | 194.70 | 125.51 |
| EF Core / Satori | postgresql | 219.35 | 219.35 | 219.90 | 119.08 |
| Java / jOOQ Native | sqlite | 100.44 | 100.44 | 99.89 | 66.18 |
| Java / jOOQ Native | postgresql | 104.05 | 104.05 | 103.32 | 68.22 |


三种峰值对应不同 API、时间和采集范围，分别保留，未合并或强制排序。
例如部分 smaps 采样峰高于 wait4 报告值，具体差异机制未在本轮证明。
释放后 RSS 是无强制 GC 的实际空闲观测，单次约 15 秒不能证明有或没有内存泄漏。
Java 的 `Runtime.totalMemory()/maxMemory()` API 原值 8,360,820,736 B 另存于 JSON；
不能将名为 `JavaHeapCommittedBytes` 的历史字段当作物理 RSS 或操作系统实际提交的内存。

## 服务延迟与从计划到达到完成的延迟

单位为毫秒，三个数依次为 p50 / p95 / p99，均为原始直方图 bin 上界。
成功延迟不包含被拒绝的请求。计划到完成包含 producer 迟发、录入、排队及执行；
不能把两个 p99 相减得到排队 p99。独立 StartDelay 指标也包含唤醒/调度等成本，并非纯队列驻留时间。

| 实现 | 数据库 | 服务 p50 / p95 / p99 ms | 计划到完成 p50 / p95 / p99 ms |
| --- | --- | --- | --- |
| Dapper.AOT | sqlite | 0.097 / 1.343 / 3.965 | 0.166 / 1.917 / 4.456 |
| Dapper.AOT | postgresql | 0.317 / 2.359 / 3.850 | 0.342 / 2.687 / 5.210 |
| EF Core / Workstation | sqlite | 0.139 / 1.450 / 3.621 | 0.210 / 2.064 / 5.145 |
| EF Core / Workstation | postgresql | 0.397 / 3.178 / 5.112 | 0.434 / 3.736 / 7.995 |
| EF Core / Satori | sqlite | 0.148 / 1.409 / 3.539 | 0.217 / 1.991 / 5.079 |
| EF Core / Satori | postgresql | 0.383 / 2.933 / 4.489 | 0.410 / 3.277 / 6.193 |
| Java / jOOQ Native | sqlite | 0.156 / 1.384 / 2.753 | 0.209 / 1.696 / 3.932 |
| Java / jOOQ Native | postgresql | 0.330 / 2.425 / 3.801 | 0.365 / 2.638 / 4.719 |


## GC 与 PostgreSQL 服务端成本

GC 次数和计时时长按进程口径保留。Dapper 的原消费者没有 GC 暂停时长字段；
EF 的累计 GC API 时长不假定在 Satori 与 stock GC 间等价；
Java MXBean collection time 不是经过验证的 STW 暂停分布。

| 实现 | 数据库 | 进程 GC 计数差 | 进程 GC 计时时长与口径 |
| --- | --- | --- | --- |
| Dapper.AOT | sqlite | 19,471 / 180 / 18（Gen0/1/2） | 不可用 |
| Dapper.AOT | postgresql | 11,648 / 6,735 / 101（Gen0/1/2） | 不可用 |
| EF Core / Workstation | sqlite | 59,734 / 196 / 18（Gen0/1/2） | 25.790931 s GC API 时长 |
| EF Core / Workstation | postgresql | 78,003 / 198 / 19（Gen0/1/2） | 41.018925 s GC API 时长 |
| EF Core / Satori | sqlite | 15,229 / 15,224 / 118（Gen0/1/2） | 7.754826 s GC API 时长 |
| EF Core / Satori | postgresql | 18,080 / 18,080 / 140（Gen0/1/2） | 7.202840 s GC API 时长 |
| Java / jOOQ Native | sqlite | 8,327 次 collection | 9.304 s collection time |
| Java / jOOQ Native | postgresql | 13,135 次 collection | 26.951 s collection time |


冻结 observer 在当前环境的 `/proc` 子进程枚举不完整，四格 PG 均只枚举到 postmaster，
遗漏活跃 backend；`rssComplete=true` 只表示已枚举记录可读。因此 **整个 PostgreSQL 实例在精确业务窗口内的 CPU/RSS/PSS 不可用**。
原始子集观测保留为子集，不冒充整库成本。正常停止后的 OS wait4 生命周期 CPU 如下，
包含初始化/fixture、暖机、释放、空闲及退出等更宽范围，不能改称精确 1,800 秒稳态 CPU，也不与子集 CPU 相加。

| 实现 | PG OS wait4 生命周期 CPU 秒 | PG 精确业务窗口整库 CPU/RSS/PSS |
| --- | --- | --- |
| Dapper.AOT | 2,129.51 | 不可用 |
| EF Core / Workstation | 1,930.51 | 不可用 |
| EF Core / Satori | 1,939.92 | 不可用 |
| Java / jOOQ Native | 1,878.44 | 不可用 |


详细覆盖、端点和数据库统计另见 [服务端观测评审](campaign/analysis/server-coverage-policy.md)。

## 冻结条件与实际运行时

原条件来自最新**完成**的 Korda #37 / Plan #34 长测；#40 的长测已取消，未用作完成基线。
同一观测 Linux x64 主机/boot，客户端固定 CPU 0–3，PG 固定 4–7，observer 固定 8；
八段无重叠，期间没有构建或新增诊断负载。物理宿主独占和不可见祖先配额没有获得证明。

| 条件 | SQLite | PostgreSQL |
| --- | --- | --- |
| 每段提供负载 | 1,800 秒 | 1,800 秒 |
| 并发 | 4 | 8 |
| 到达率 | 3,000/s | 3,600/s |
| 计划业务 | 5,400,000 | 6,480,000 |
| 队列容量 | 64 | 64 |
| 业务行数 / 批行数 | 32 / 32 | 32 / 32 |
| 数据 | 8 tenants × 1,024 orders | 相同 |
| 模式 | prepared / persistent | 相同逻辑模式 |
| 暖机 | 全 35 类验证，再每 worker 64 次 | 相同 |
| 引擎 | 同一 SQLite 3.51.3 动态库、同编译选项 | 同 PostgreSQL 18.0 构建及配置，每格新集群 |

每格使用新数据库副本/集群，完整 schema、索引和存储行在前后核对。
所有业务保留 DTO/hash/null/decimal/JSON 契约；提前停止仍查询 1,024 行完整 DTO 并消费三行，
未改成 LIMIT 3；四类写入/事务执行真实读写、冲突和数据恢复。
SQLite 引擎版本和编译选项与恢复条件一致，但本轮 GCC 构建不是历史 Clang ELF，不冒称历史二进制相同。

| 路径 | 实际运行时和主要依赖 |
| --- | --- |
| Dapper.AOT | .NET SDK 11.0.100 / runtime 11.0.0，Release Native AOT；Dapper 2.1.100 / Dapper.AOT 1.1.0；Npgsql / Microsoft.Data.Sqlite.Core 11.0.0 |
| EF Workstation | .NET 11.0.0 JIT，EF Core / provider 11.0.0；实际 IsServerGC=false |
| EF Satori | PublishWithSatoriGC 11.0.2-satori.45942668844.1；实际 .NET 11.0.2-ci / SatoriGC=true / IsServerGC=true |
| Java Native | GraalVM Community 25.6.5.1+2.1，Java 25.0.5.1+2-jvmci-25.6-b29；Serial GC，-O3，x86-64，无 PGO；jOOQ 3.21.10 / pgJDBC 42.7.15 / sqlite-jdbc 3.51.3.0 |

版本及工具链是准备阶段实际检索、下载校验和执行的身份，不是示例版本。
Oracle 下载返回 403，最终使用官方 GraalVM Community 发行版及匹配发布校验和。
Java 的 JNI 使用匹配 Xerial 层连接本轮公共 SQLite 库，未使用 JAR 自带的不同 SQLite 引擎。
来源、锁文件、构建日志、生成代码和实际 ELF/runtime hashes 均在准备记录内。

两个 EF JIT 变体均设置：

```xml
<PropertyGroup>
  <TargetFramework>net11.0</TargetFramework>
  <Features>$(Features);runtime-async=on</Features>
</PropertyGroup>
```

四个实际 EF 发布程序集的编译参数均包含该 feature，均验证到 **19 个 Async 方法元数据标志**。
没有声称预编译的 EF/驱动依赖也重新以该 feature 编译。Satori XML SDK 替换 CoreCLR 和 JIT 资产，
实际版本与 stock runtime 不同，因此这不是只改一个 GC 开关的实验。

## Fluent 实现与可比性边界

EF 使用 Fluent IQueryable、AsNoTracking、明确的类型投影，每 worker 一个 DbContext；
prepared 模式复用表达式图及正常查询缓存，没有冒称 EF.CompileQuery 或物理语句缓存。
32 类使用 Fluent/EF 事务 API，`window`、`running-total` 以参数化 EF SqlQuery 保留窗口语义，
`raw-sql` 保留原业务要求的原始 SQL。等价改写包括固定连续 parent keys 的 related 范围查询、
非物化 CTE 的过滤派生查询，以及保留 NULL SUM、精确金额和 NULL 排序的翻译。
详见 [EF 实现说明](clients/efcore/README.md)。

Java 使用 jOOQ Fluent DSL 和手写 typed DTO；原 `raw-sql` 类保留原始 SQL。
采用等价直接 LEFT JOIN 和单个 bounded IN related 查询；图按 worker 复用，related/事务图按业务构造。
没有保留 JDBC statement，PG prepareThreshold=0，不能把 prepared/persistent 解释为物理语句复用完全相同。
详见 [Java 实现说明](clients/java/README.md)。

共同到达/拒绝/排空业务契约经核对；C# 使用 Channel/async Tasks，Java 使用平台线程和 monitor。
高层 sleep/spin 策略一致，但机器指令成本、唤醒、锁竞争和调度 CPU 占比没有单独测量。
因此客户端 CPU 保留整条实现和工具成本，不扣假设值。拒绝还会改变 35 类实际准入构成；
不能把整个混合样本差异直接当成某一查询或 GC 的加速。
详见 [调度与计量范围复核](campaign/analysis/harness-scope-review.md)。

## 证据、审查与交付

- [执行矩阵](campaign/matrix-01.json)：冻结命令、依赖、源码、运行时和实际二进制身份。
- [完整离线分析](campaign/analysis/offline-01/report.md) 与 [机器可读结果](campaign/analysis/offline-01/summary.json)。
- [独立最终复核](campaign/analysis/final-independent-review.md)：原始计数、时间、35 类、哈希身份、延迟/CPU/分配算术和全部资源采样。
- [原始归档清单](raw/long-campaign-01/manifest.json)、[完整解压验证](raw/long-campaign-01/verification.json)、[SHA256SUMS](raw/long-campaign-01/SHA256SUMS)。
- [归档实际执行回执](raw/long-campaign-01-execution.json)：103 文件、93,870,632 原始字节 → 9 档、5,605,260 压缩字节；103 成员完整回读一致，11 项标准校验和全通过。
- [当前状态](final-state.json) 与 [恢复位置](handoff.md)：8/8 已完成，不应因中断重新启动长测。

原始归档保留 JSON/JSONL、执行命令、环境/状态、stdout、DB 前后验证、PG 配置和服务器日志。
不包含可重建的数据库文件、pgdata、完整工具链和大型 ELF；这些实际构建产物仍保留在本地任务目录，
其身份、来源、命令和关键生成代码已经记录，不把“有哈希”描述为“Git 中包含整个二进制”。

### PR、既有 CI 与停止位置

在 24 个连接仓库的范围内完成非 Dependabot PR 清理：Plan #36、Plan #35、Korda #39 关闭且未合并，
原分支和证据保留，Dependabot 未动。当前唯一新增记录 PR 为
[Plan #37](https://github.com/IzuSharp/Plan/pull/37)，按请求保持 **draft/open**。
Korda 与 Korda-Design 产品/设计实现没有本轮改动，不选择合并、NuGet 发布或新增产品包验证。

CI workflow 没有改动，也没有添加或间接触发 benchmark、剖析、校准或压力执行。
本地历史静态验证及一次当前分支旧门禁的范围失败均原样保留，原因见
[静态验证说明](validation/README.md)。按现有 CI 指定的不可变历史输入运行同一 performance-record gate 通过；
这不是新性能结果验收，也没有把旧 acceptance 的 in_progress/0 段改写成本轮结果。

冻结提交 dc0480de708ba5fa4dc87e69339986cc3804e301 的既有 CI run 46126507300 已取消，
日志显示停在不可变 DB-Rename 输入的 checkout；后续历史步骤跳过，不能称绿。
[当时原始 CI 回执](ci/frozen-dc048-01/receipt.json) 已保留。
**本结果提交的最终 head 与其既有 CI 状态，以 Plan #37 正文和对应 Actions run 为准**，避免文件自引用提交哈希。

停止依据是已完成用户选定的四种实现、双库八段测试、证据归档和独立复核。
本轮没有额外优化候选、Korda 对照或重测计划；结果中的缺测和单次测量限制已经明确保留。
