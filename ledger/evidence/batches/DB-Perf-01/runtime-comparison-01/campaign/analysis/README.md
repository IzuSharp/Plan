# 八格结束后的离线分析（当前仅完成脚本准备）

此目录只新增分析工具和报告结构，不属于冻结受测客户端，也不修改 matrix、frozenInputs、历史原始记录或已有review。`analyze_campaign.py` 为纯Python标准库脚本，无subprocess、数据库、网络、客户端或绘图入口。初始准备只写源文件并用ast.parse检查语法。后续按root明确授权读取02 PG末两条资源记录定位进程枚举缺口，并在02结束后独立核对该格结果的34项业务验收，形成精确Hash绑定的idle偏差评审。**尚未执行全八格分析器或生成综合性能结果，也未启动任何负载。**

## 调用接口

等待主代理确认八格运行结束后，在CPU8调用：

```bash
taskset -c 8 python3 campaign/analysis/analyze_campaign.py   --matrix /absolute/path/to/frozen-matrix.json   --campaign /absolute/path/to/eight-cell-output   --output /absolute/path/to/campaign/analysis/offline-01
```

输出目录必须是本analysis目录下的一个全新子目录，不能覆盖旧文件。脚本要求当前CPU affinity恰为8；在读各格结果或大JSONL前，先对campaign.lock获取非阻塞共享锁，并检查八格均已有终态及结束时间。runner仍持有独占锁、格数不全或缺少终态时退出，不做部分运行的结果分析。

成功分析输出 `summary.json`、`report.md`、`case-distribution.md`、`analysis-receipt.json`。退出码0表示八格业务窗口均通过严格检查或明确列入的精确Hash评审，1表示已生成结果但仍存在未获业务比较资格的格，2表示入口/结构条件不满足。`allCellsAccepted`继续表示严格检查全通过，02有idle偏差时保持false；`allBusinessMeasurementsAccepted`另表示业务窗口资格，不能把两者混为一谈。八格中任何格完全缺失result或command JSON时，脚本拒绝把这种情况伪造为一个0指标结果，应另做失败专项复核。

## 验收边界

- 锁定SQLite C4/R3000与PG C8/R3600、1800秒、队列64、prepared/persistent、35case、每worker暖机64、8tenant×1024orders、32rows和15秒释放后idle。
- 校验frozen matrix与host、各格plan、result/status及observer资源/日志Hash绑定。脚本不再发起编译或负载；冻结产物本体的运行前后Hash门由原runner提供。
- 要求Attempted=Planned=rate×1800，Attempted=Sent+Rejected，Sent=Started=Completed，Completed=Succeeded+Failed。顶层Completed是Succeeded，不是OfferedLoad.Completed。
- 复核四套直方图样本总数、每秒与每类Started/Succeeded/Failed/Rows对账、所有oracle及连接归还、稳态单调时间、非截断序列、PG清洁退出。
- normalized matrix provider是sqlite/postgresql；C#结果Provider实际是Microsoft.Data.Sqlite.Core或Npgsql，Java才是sqlite/postgresql，分析按实现精确映射，原标签同时保留。
- 原observer的longRunAcceptance字段是低层历史字段，未被正式runner改成true；不拿它替代1800秒、结果与cell-status的实际验收。
- C#的OfferedLoad.DrainedTicks来自完成后Snapshot，通常比顶层SteadyEndMonotonicNs稍晚，不能强求两者相等。资源采样按顶层SteadyStart/End对齐。

## 指标约定

主成功吞吐为Succeeded / EffectiveSeconds，包含已准入任务drain；另外保留Succeeded/1800、前1800秒真正完成的成功数、drain后的完成数、实际producer时长和超期量，避免混淆计划到达窗口与完成窗口。

Service与Scheduled均报告成功业务p50/p95/p99；另有全部完成Scheduled与StartDelay。直方图复用实际消费者的base-2纳秒、每指数128分桶规则，数值是bin上界。Scheduled与StartDelay含producer迟滞及队列等待，不能将两个p99相减解释为排队p99。拒绝没有成功延迟样本。

客户端CPU主指标来自本格ProcessBefore/After的进程CPU差，并除以成功业务数；原observer wait4生命周期CPU单列。二者不能相加。全进程managed/Java allocated为累计计数边界差，包含运行时、驱动、DTO、JSON及工具，不声称框架单独分配；不支持的Java/Native计数保留null。RSS不能代替分配量。

内存报告将三个既有来源分别成表：OS wait4在进程退出回收时报告的生命周期maxRSS；消费者ProcessAfter快照所见的自报高水位（可能包含此前暖机，不能称作退出后的全生命周期值）；observer在同PID/startTicks且采集全程完整落于steady窗口内的离散RSS/PSS样本最大值。最后一项不能保证捕获瞬时峰。三者不合并max，不强制数值大小排序，不因彼此差异增加业务失败门；具体Linux/API计数机制未证实。

Root已指出03消费者自报130.85546875MiB与已见observer RSS样本131.23828125MiB的差异，本次修改没有重读正式数据或改写这两个观察。综合报告仍分别使用完整原始证据的各自字段/筛选算法，不为匹配已见数字改变steady窗口，不预先把某个已见sample标成最终全程峰值。释放后idle的Before/After按请求15秒、实际观察时长单列；没有强制GC，也不能单独判断泄漏或无泄漏。进程内SQLite原生引擎及页面缓存计入客户端；外置PG单列。

192MiB=201326592B只是用户接受的C#请求GC设置，不是总进程硬限。EF RuntimeIdentity中的实际GC available与configured limit保留并展示；Satori较大的实际available不能被隐藏或倒填成192MiB。未在Dapper正式回执采集的GC available字段保持null，独立probe不替代该格读数。Java没有此C#预算上限。

C# Gen0/1/2计数分别保留，不相加。EF GcPauseTicks单位是100ns的TimeSpan tick；Satori和stock暂停API语义不假定等价。既有Dapper回执没有pause字段，显示null。Java保留每collector及进程collection count/time；负数unsupported值先转null，不能将-1减-1伪造为0。collection time不是已验证的STW pause histogram。

PG整库steady CPU/RSS/PSS需要完整子进程枚举证明。02原始尾部观察只返回postmaster，当前exec也直接确认其自身已知父进程的task/children文件不存在；冻结observer依赖该接口且没有枚举覆盖证据。因此整库steady值保持null，不把单一postmaster的近零CPU或约20MiB RSS当成整库值。rssComplete/pssComplete只证明已经返回的记录可读，不能证明没有漏掉backend或后台进程。即使记录数量达到1+Concurrency，也只是必要下限，不是整库覆盖认证。

只作为**observed subset / partial**保留两个完整落在消费者稳态窗口内的原始端点，每个端点各自求own+already-reaped ticks，再作一次差。没有累加per-PID maxima、只加正增量或加上wait4。记录端点行号、PID/startTicks、进程数范围、采样缺口与负跳变，不插值成完整1800秒CPU。正常shutdown后的PG wait4单列为OS所报告的生命周期own/reaped-descendant用量，包含fixture/warmup/release/idle/shutdown等阶段；不能倒推出steady，也不证明observer枚举完整。部分进程RSS可能重复计共享页，partial PSS另存；owner wait4 maxRSS不等于并发树峰RSS。

pg_stat_database的before/after覆盖比客户端steady更广、并受统计发布时点影响；完整原始值及数值差保留，但不标成纯稳态执行成本。

## 02 idle偏差的精确分类

原冻结02 runner的cell-status保持failed，唯一原failure是released_idle。独立复核：RequestedSeconds=15、Stopwatch实测14.997119729秒、UTC经过14.9971417秒，严格少2.880271毫秒，不能舍入或改写为15。原Dapper只等待一次Task.Delay，没有按Stopwatch deadline补足；具体runtime/OS计时机制未测，保持未知。业务窗口1800.004439463秒、完整计数/直方图/35case/oracle/恢复等34项检查通过，idle在业务与CPU/分配边界之后。

`02-idle-deviation-review.json/md`记录root与baseline_recovery两个助手的独立证据复核；这不是新的用户人工批准。分析器仅为case02且result/status/review三份Hash精确匹配、严格错误恰为原failed状态与idle不足时，派生`business-valid/idle-deviation`。原`originalStrictStatus=failed`、`strictIdleRequirementMet=false`、严格错误和实际idle秒数全部保留。业务比较可使用该1800秒窗口，释放后内存按实际时长标注。

其他格不继承此分类；没有添加通用毫秒容差。未来若同类偏差出现，需另外逐条独立评审与精确绑定，不能自动放宽标准。原冻结runner/matrix、客户端及原始记录不改，不为该偏差重跑30分钟。

## 业务构成和解释限制

Dapper/EF `Workload.Index` 以及Java `Options.index` 都采用全局job index modulo冻结case order。计划总数已知且所有尝试完整，因此每类计划数可精确恢复。完整Sent=Started对账通过后，按类Planned−Started可派生拒绝数，并核对其总和；该值明确标为derived，未冒称直接采集逐次拒绝case事件。

`case-distribution.md`为每格保留35类计划、实际Started、Succeeded、Failed、派生拒绝、计划份额、成功份额及百分点差。拒绝可能改变实际成功业务组合，aggregate CPU/op不能无条件归因框架或GC。

每格只有同一观察host/boot上的一次串行长run。与同库Dapper只作描述性绝对值/比值/差值；不宣称重复测量统计显著、GC-only因果、持续吞吐上限、开始拒绝压力拐点或已对齐，也不把历史不同机器结果冒作本机前后对照。物理宿主排他性没有被证明。
