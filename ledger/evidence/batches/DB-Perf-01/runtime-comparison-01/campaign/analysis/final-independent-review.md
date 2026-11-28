# DB-Runtime-Compare-01：正式八格独立复核

**结论：业务窗口、运行身份和离线派生值复核通过；保留原始严格失败与计量边界。** 八格均完成至少1800秒，35类业务、独立manifest结果摘要、准入/完成/拒绝、逐秒和逐类计数、四组直方图人口均对齐；业务和Oracle错误为0，fixture完整恢复，逻辑连接清零。02仍为原始failed/released_idle，不能写成八格严格验收全通过。

- 复核人：/root/satori_research；复核时间：2026-11-28T12:49:36.573156+00:00。
- 矩阵SHA-256：450d0e8762db63dd5dada402c1c1b59797f3cb4207ef655375b6b63ba7e715ae。
- 分析器SHA-256：27fb73e8c33d8a4b027e8aa7acdea198650c1cde3423a9c28058ce8297bba595。
- 派生summary SHA-256：68ae224f3768f44d880007413f3844f8bd41078a376226c81f1754ac1b4d7d2e。
- 独立核对项：486项；未发现待修复算术、身份或业务结论错误。

## 复核方法

只在CPU8读取已经完成的原始result、command、status、plan、fixture和PG owner回执，以及offline-01输出。没有导入或执行分析器；用独立Python算术复算吞吐、CPU/成功、分配/成功、全部p50/p95/p99、相对差值和35类计划/成功/派生拒绝。重新核对实际ELF、EF DLL/coreclr/clrjit与冻结SHA，核对实际启动参数和客户端0–3/PG4–7亲和性，以及八格单调时钟串行顺序。

另外以只读单次流式扫描复算既有observer JSONL的SHA、同PID/startTicks稳态样本人口与RSS/PSS最大值、PG子集首末端点。没有取得新资源样本，没有执行客户端、数据库、构建或压力负载；没有修改原始证据或其他代理产物。

## 独立复算的主要数值

| 格 | Effective秒 | 成功数 | 拒绝数 | CPU µs/成功 | 全进程分配 B/成功 | OS wait4 maxRSS MiB | observer稳态RSS采样峰 MiB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 01-dapper-sqlite | 1800.000991777 | 5,395,182 | 4,818 | 565.286531 | 7,457.71 | 33.07421875 | 31.43359375 |
| 02-dapper-postgresql | 1800.004439463 | 6,470,481 | 9,519 | 456.513456 | 7,352.88 | 42.22265625 | 38.35156250 |
| 03-ef-workstation-sqlite | 1800.009096153 | 5,383,490 | 16,510 | 591.321238 | 22,967.24 | 130.85546875 | 131.39453125 |
| 04-ef-workstation-postgresql | 1800.003921989 | 6,461,859 | 18,141 | 504.730027 | 24,972.80 | 132.93359375 | 133.56250000 |
| 05-ef-satori-sqlite | 1800.006379435 | 5,378,653 | 21,347 | 599.471778 | 23,127.72 | 194.60937500 | 194.70312500 |
| 06-ef-satori-postgresql | 1800.008385578 | 6,459,584 | 20,416 | 508.141061 | 25,361.66 | 219.34765625 | 219.90234375 |
| 07-java-native-sqlite | 1800.005802815 | 5,385,710 | 14,290 | 561.326176 | 不可用 | 100.43750000 | 99.89453125 |
| 08-java-native-postgresql | 1800.005104904 | 6,460,984 | 19,016 | 413.672283 | 不可用 | 104.05468750 | 103.32421875 |

## 身份和内存政策

两个Dapper ELF与冻结的Release、linux-x64、net11.0 Native AOT构建绑定。正式Dapper回执未记录GC配置/可用堆值，不能用独立128MiB探针补成正式192MiB运行实测。

四格EF的实际托管DLL与已加载coreclr/clrjit哈希均匹配冻结输入。Workstation为.NET11.0.0、IsServerGc=false；Satori为.NET11.0.2-ci、SatoriGc=true、IsServerGc=true。四格均记录runtime-async=on及19个runtime-async方法。正式启动前持久性独立核验计数为每worker4项，即SQLite16项、PG32项。

四格EF均记录201326592 B（192MiB）配置。Workstation启动可用堆记录192MiB；Satori为10451427328 B（9967.2578125MiB）。Satori两格OS wait4 maxRSS分别194.609375和219.34765625MiB，observer稳态RSS采样峰分别194.703125和219.90234375MiB。它们与用户接受的“请求192MiB、无需cgroup、如实报告超额”政策相符，不能改写为192MiB强制上限。

Java两格使用同一个冻结Native Image ELF，版本25.0.5.1+2-jvmci-25.6-b29，正式admission SHA、manifest与实际ELF一致；Java没有C#预算上限。JavaHeapCommittedBytes历史字段来自Runtime.totalMemory()，API返回的8360820736 B不是物理RSS或已证实的OS已提交内存。

## 02严格状态与业务分类

02 result SHA保持61f45dae1a6a687298e87e81bdae689fa26a9aae88cd25a60d62e8368de6a50c，status SHA保持9576fc157dbcc8acae8b4515f78ec1f5fe901be8e7379f9d7203d73da32e82c4。原始唯一失败仍为released_idle，实际idle为14.997119729秒；业务窗口为1800.004439463秒。summary仍保留allCellsAccepted=false，只允许精确hash评审后businessMeasurementAccepted=true；其他格没有通用容差。

## 能支持与不能支持的结论

证据足以支持这一台已记录主机、这一固定到达率、这一次连续30分钟窗口内的描述性业务成本比较。各项成功吞吐、CPU/成功、C#全进程分配、成功服务/含调度排队延迟、三来源内存观测与原始记录一致。Java PG在本轮记录的客户端CPU/成功低于Dapper，EF两GC的CPU/成功和分配高于Dapper，均只能作为本轮观察。

所有格都有非零拒绝，成功吞吐接近固定到达率不能证明吞吐上限、零拒绝成本或压力拐点；只有一次串行运行，不能宣称统计显著、GC单因素因果或已对齐。不同准入业务构成已在35类分布中保留。

四格PG observer稳态只枚举到一个服务端进程，因此整库steady CPU/RSS/PSS未知。子集own+reaped首末端点差与正常停止后的OS wait4生命周期成本分别保留，不能拼成完整1800秒服务端成本。

Java GC collection time只报告MXBean累计计数差，不称为已验证的STW暂停分布。C#GC代数分别保留、不同GC的累计pause API不视为等价。C#全进程分配不能归为框架独立分配；native和Java分配未知保持null。

消费者ProcessAfter自报峰、wait4生命周期maxRSS与observer离散采样峰分别报告；不跨来源取max、不强制数值排序。释放后实际idle均未强制GC，RSS不能单独证明泄漏或无泄漏。

## 文件

- final-independent-review.json：逐格原始与派生检查、实际文件SHA、重算指标、峰值样本行号和限制。
- offline-01/summary.json、offline-01/report.md、offline-01/case-distribution.md、offline-01/analysis-receipt.json：被复核的正式离线输出，哈希见JSON。
