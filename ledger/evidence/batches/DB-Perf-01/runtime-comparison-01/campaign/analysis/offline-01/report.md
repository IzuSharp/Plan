# DB-Runtime-Compare-01：八格正式运行的离线分析

## 验收与解释范围

原始严格验收：**存在严格失败；原状态完整保留**。1800秒业务窗口比较资格：**全部有效（含表中精确Hash绑定的独立评审分类）**。PG整库steady成本缺测须另看覆盖说明，不能把业务资格解释为所有指标完整。本报告由冻结回执和原始observer采样生成，未经重复运行，不宣称统计显著、GC单因素因果或已对齐。

C#统一请求192 MiB GC预算，未施加cgroup或进程总内存硬限；Satori的本格实际GC available按RuntimeIdentity展示；既有越界探针是128 MiB，不能冒称已完成192 MiB边界探针。SQLite原生内存计入客户端，PG服务端单列，Java未施加该C#预算。

主吞吐为成功业务数除以消费者EffectiveSeconds（包含已准入任务drain）。延迟是直方图bin上界；拒绝不进入成功延迟样本。StartDelay包含到达调度迟滞和排队。

## 成功、拒绝与错误

| 实现 | 数据库 | 成功数 | 拒绝数 | 业务错误 | 成功/s | 拒绝率 | Effective秒 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Dapper.AOT | sqlite | 5,395,182 | 4,818 | 0 | 2,997.32 | 0.09% | 1,800.000992 |
| Dapper.AOT | postgresql | 6,470,481 | 9,519 | 0 | 3,594.70 | 0.15% | 1,800.004439 |
| EF Core JIT Workstation | sqlite | 5,383,490 | 16,510 | 0 | 2,990.81 | 0.31% | 1,800.009096 |
| EF Core JIT Workstation | postgresql | 6,461,859 | 18,141 | 0 | 3,589.91 | 0.28% | 1,800.003922 |
| EF Core JIT Satori | sqlite | 5,378,653 | 21,347 | 0 | 2,988.13 | 0.40% | 1,800.006379 |
| EF Core JIT Satori | postgresql | 6,459,584 | 20,416 | 0 | 3,588.64 | 0.32% | 1,800.008386 |
| Java 25 GraalVM Native | sqlite | 5,385,710 | 14,290 | 0 | 2,992.05 | 0.26% | 1,800.005803 |
| Java 25 GraalVM Native | postgresql | 6,460,984 | 19,016 | 0 | 3,589.43 | 0.29% | 1,800.005105 |

## 原始严格状态与业务分类

| 格 | 原始严格状态 | 业务分类 | strict idle ≥15s | 实际idle秒 |
| --- | --- | --- | --- | ---: |
| 01-dapper-sqlite | passed | strictly-accepted | True | 15.000324515 |
| 02-dapper-postgresql | failed | business-valid/idle-deviation | False | 14.997119729 |
| 03-ef-workstation-sqlite | passed | strictly-accepted | True | 15.001755535 |
| 04-ef-workstation-postgresql | passed | strictly-accepted | True | 15.004982157 |
| 05-ef-satori-sqlite | passed | strictly-accepted | True | 15.006726641 |
| 06-ef-satori-postgresql | passed | strictly-accepted | True | 15.002004243 |
| 07-java-native-sqlite | passed | strictly-accepted | True | 15.000287529 |
| 08-java-native-postgresql | passed | strictly-accepted | True | 15.000613458 |

business-valid/idle-deviation只用于已列入精确case名、result/status/review Hash绑定的单条独立评审。原strict failed与严格错误保留，实际idle不改成15秒，也没有为其他格增加通用毫秒容差。


## 客户端成本与释放后内存

| 实现 | 数据库 | CPU µs/成功业务 | 释放idle后RSS MiB | 实际idle秒 | GC启动可用MiB | 全进程分配 B/成功业务 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Dapper.AOT | sqlite | 565.29 | 28.76 | 15.000324515 | 不可用 | 7,457.71 |
| Dapper.AOT | postgresql | 456.51 | 34.81 | 14.997119729 | 不可用 | 7,352.88 |
| EF Core JIT Workstation | sqlite | 591.32 | 107.33 | 15.001755535 | 192.00 | 22,967.24 |
| EF Core JIT Workstation | postgresql | 504.73 | 98.98 | 15.004982157 | 192.00 | 24,972.80 |
| EF Core JIT Satori | sqlite | 599.47 | 125.51 | 15.006726641 | 9,967.26 | 23,127.72 |
| EF Core JIT Satori | postgresql | 508.14 | 119.08 | 15.002004243 | 9,967.26 | 25,361.66 |
| Java 25 GraalVM Native | sqlite | 561.33 | 66.18 | 15.000287529 | 不可用 | 不可用 |
| Java 25 GraalVM Native | postgresql | 413.67 | 68.22 | 15.000613458 | 不可用 | 不可用 |

RSS为内存驻留量；分配来自全进程累计计数，含驱动、DTO、JSON与工具成本，不能反推框架单独分配。Native/Java不支持的计数保持null，未记为0。三种峰值来源及范围在下一表分别展示，不合并为一个max。idle没有强制GC；请求15秒，各格实测时长见表。实际idle观察后的RSS不能单独证明泄漏或无泄漏。GC启动可用值来自本格RuntimeIdentity；未记录的Dapper字段保持不可用，不用独立探针代填。

## 客户端RSS/PSS的三个观测来源

| 实现 | 数据库 | OS wait4 生命周期 maxRSS MiB | 消费者ProcessAfter自报峰 MiB | observer稳态采样RSS峰 MiB | observer稳态采样PSS峰 MiB |
| --- | --- | ---: | ---: | ---: | ---: |
| Dapper.AOT | sqlite | 33.07421875 | 31.35937500 | 31.43359375 | 29.84570312 |
| Dapper.AOT | postgresql | 42.22265625 | 38.05468750 | 38.35156250 | 37.43066406 |
| EF Core JIT Workstation | sqlite | 130.85546875 | 130.85546875 | 131.39453125 | 125.73144531 |
| EF Core JIT Workstation | postgresql | 132.93359375 | 132.93359375 | 133.56250000 | 126.90917969 |
| EF Core JIT Satori | sqlite | 194.60937500 | 194.60937500 | 194.70312500 | 192.75683594 |
| EF Core JIT Satori | postgresql | 219.34765625 | 219.34765625 | 219.90234375 | 213.92773438 |
| Java 25 GraalVM Native | sqlite | 100.43750000 | 100.43750000 | 99.89453125 | 98.24902344 |
| Java 25 GraalVM Native | postgresql | 104.05468750 | 104.05468750 | 103.32421875 | 102.41113281 |

OS wait4列保留操作系统在进程退出回收时报告的生命周期maxRSS。消费者列来自业务结束后的ProcessAfter快照所见高水位，可能包含此前暖机，不能冒称退出后的全生命周期值。observer列分别取同一PID/startTicks、且采集全程落在steady窗口内的离散RSS/PSS样本最大值，不能保证捕获瞬时峰。

三种数值的差异原样保留，不强制wait4或消费者自报峰大于等于smaps样本，不跨来源取max，不把差异列为业务错误。具体Linux/API计数差异原因没有在本轮证实；各列原始bytes、有效采样数和scope保留在summary.json。 Java结果另保留Runtime.totalMemory()/maxMemory()的API原值：历史字段JavaHeapCommittedBytes实际来自totalMemory()，不能将其解释为物理RSS或真实OS已提交内存。

## 服务及含调度/排队延迟

| 实现 | 数据库 | 成功service p50/p95/p99 µs | 成功scheduled p50/p95/p99 µs | start-delay p50/p95/p99 µs |
| --- | --- | --- | --- | --- |
| Dapper.AOT | sqlite | 97.28 / 1,343.49 / 3,964.93 | 165.89 / 1,916.93 / 4,456.45 | 31.10 / 557.06 / 2,129.92 |
| Dapper.AOT | postgresql | 317.44 / 2,359.30 / 3,850.24 | 342.02 / 2,686.98 / 5,210.11 | 13.82 / 78.34 / 2,818.05 |
| EF Core JIT Workstation | sqlite | 139.26 / 1,449.98 / 3,620.86 | 209.92 / 2,064.38 / 5,144.58 | 28.29 / 667.65 / 3,309.57 |
| EF Core JIT Workstation | postgresql | 397.31 / 3,178.50 / 5,111.81 | 434.18 / 3,735.55 / 7,995.39 | 15.68 / 577.54 / 4,816.90 |
| EF Core JIT Satori | sqlite | 148.48 / 1,409.02 / 3,538.94 | 217.09 / 1,990.66 / 5,079.04 | 26.75 / 585.73 / 3,129.34 |
| EF Core JIT Satori | postgresql | 382.98 / 2,932.74 / 4,489.22 | 409.60 / 3,276.80 / 6,193.15 | 15.17 / 144.38 / 3,211.26 |
| Java 25 GraalVM Native | sqlite | 155.65 / 1,384.45 / 2,752.51 | 208.90 / 1,695.74 / 3,932.16 | 28.54 / 323.58 / 1,900.54 |
| Java 25 GraalVM Native | postgresql | 329.73 / 2,424.83 / 3,801.09 | 364.54 / 2,637.82 / 4,718.59 | 24.45 / 104.45 / 1,916.93 |

## PostgreSQL服务端成本

| 实现 | 整库steady CPU秒 | 观测子集CPU秒 | 子集进程数min/max | 生命周期wait4 CPU秒 | 整库steady峰PSS MiB |
| --- | ---: | ---: | --- | ---: | ---: |
| Dapper.AOT | 不可用 | 1.19 | 1/1 | 2,129.51 | 不可用 |
| EF Core JIT Workstation | 不可用 | 1.37 | 1/1 | 1,930.51 | 不可用 |
| EF Core JIT Satori | 不可用 | 1.36 | 1/1 | 1,939.92 | 不可用 |
| Java 25 GraalVM Native | 不可用 | 1.26 | 1/1 | 1,878.44 | 不可用 |

整库steady CPU/RSS/PSS未获得完整进程枚举证明，保持不可用；只看到postmaster时，其CPU或RSS不能当成整库值，rssComplete=true也只证明已返回记录可读。表中观测子集是原始端点own+already-reaped差，可能遗漏全部活跃backend，绝不是整库成本。树快照非原子，边缘缺口和负向跳变保留，不插值成精确1800秒；没有累加per-PID最大值、重复计parent reaped或加上wait4。正常shutdown后的wait4保留OS生命周期计数口径，不能据此倒推steady；PG统计查询的前后差也覆盖更宽窗口。

## GC口径

| 实现 | 数据库 | 进程计数 | 计时时长与限制 |
| --- | --- | --- | --- |
| Dapper.AOT | sqlite | {"gen0":19471,"gen1":180,"gen2":18} | 不可用秒；Pause duration is absent in the historical Dapper consumer; null is not zero. |
| Dapper.AOT | postgresql | {"gen0":11648,"gen1":6735,"gen2":101} | 不可用秒；Pause duration is absent in the historical Dapper consumer; null is not zero. |
| EF Core JIT Workstation | sqlite | {"gen0":59734,"gen1":196,"gen2":18} | 25.790931秒；Process GC API cumulative duration; Satori thread-local accounting may differ from stock stop-the-world accounting. |
| EF Core JIT Workstation | postgresql | {"gen0":78003,"gen1":198,"gen2":19} | 41.018925秒；Process GC API cumulative duration; Satori thread-local accounting may differ from stock stop-the-world accounting. |
| EF Core JIT Satori | sqlite | {"gen0":15229,"gen1":15224,"gen2":118} | 7.754826秒；Process GC API cumulative duration; Satori thread-local accounting may differ from stock stop-the-world accounting. |
| EF Core JIT Satori | postgresql | {"gen0":18080,"gen1":18080,"gen2":140} | 7.202840秒；Process GC API cumulative duration; Satori thread-local accounting may differ from stock stop-the-world accounting. |
| Java 25 GraalVM Native | sqlite | 8,327 | 9,304.000毫秒collection time；不是已验证的STW暂停分布 |
| Java 25 GraalVM Native | postgresql | 13,135 | 26,951.000毫秒collection time；不是已验证的STW暂停分布 |

## 相对同库Dapper的描述性差距

| 实现 | 数据库 | 成功吞吐变化 | CPU/成功变化 | service p99变化 | scheduled p99变化 |
| --- | --- | ---: | ---: | ---: | ---: |
| EF Core JIT Workstation | sqlite | -0.22% | 4.61% | -8.68% | 15.44% |
| EF Core JIT Satori | sqlite | -0.31% | 6.05% | -10.74% | 13.97% |
| Java 25 GraalVM Native | sqlite | -0.18% | -0.70% | -30.58% | -11.76% |
| EF Core JIT Workstation | postgresql | -0.13% | 10.56% | 32.77% | 53.46% |
| EF Core JIT Satori | postgresql | -0.17% | 11.31% | 16.60% | 18.87% |
| Java 25 GraalVM Native | postgresql | -0.15% | -9.38% | -1.28% | -9.43% |

各格只有一次长run，CPU/内存预算、ORM/驱动、SQL翻译、调度与GC可能同时不同；不能把差距全部归因GC。出现拒绝时，应结合case-distribution.md及summary.json中的35类计划与实际成功占比，避免把不同准入业务构成当成单查询加速。固定到达率的八格不能推出持续吞吐上限或开始拒绝的压力拐点。

## 核验问题与保留限制

### 01-dapper-sqlite

- Rejection changes the admitted case population; compare per-case success shares. No rejection latency is inserted into successful-operation histograms.

### 02-dapper-postgresql

- runner cell-status is not passed
- 15-second released idle incomplete
- Rejection changes the admitted case population; compare per-case success shares. No rejection latency is inserted into successful-operation histograms.
- Whole-server steady PostgreSQL CPU/RSS/PSS unavailable because descendant enumeration is incomplete or unproven. Explicit observed-subset values and OS lifetime wait4 remain separate; unknown whole-server cost is not zero.
- Exact SHA-bound two-assistant review accepts this 1800-second business window only. Original strict status remains failed; idle is 14.997119729 seconds, not a full 15 seconds.

### 03-ef-workstation-sqlite

- Rejection changes the admitted case population; compare per-case success shares. No rejection latency is inserted into successful-operation histograms.

### 04-ef-workstation-postgresql

- Rejection changes the admitted case population; compare per-case success shares. No rejection latency is inserted into successful-operation histograms.
- Whole-server steady PostgreSQL CPU/RSS/PSS unavailable because descendant enumeration is incomplete or unproven. Explicit observed-subset values and OS lifetime wait4 remain separate; unknown whole-server cost is not zero.

### 05-ef-satori-sqlite

- Rejection changes the admitted case population; compare per-case success shares. No rejection latency is inserted into successful-operation histograms.
- 192 MiB is requested GC configuration only. A prior 128 MiB Satori probe crossed its requested heap budget; no equivalent enforcement probe was performed at 192 MiB. This run preserves the observed GC available-memory value and makes no enforced-cap or GC-only causal claim.

### 06-ef-satori-postgresql

- Rejection changes the admitted case population; compare per-case success shares. No rejection latency is inserted into successful-operation histograms.
- 192 MiB is requested GC configuration only. A prior 128 MiB Satori probe crossed its requested heap budget; no equivalent enforcement probe was performed at 192 MiB. This run preserves the observed GC available-memory value and makes no enforced-cap or GC-only causal claim.
- Whole-server steady PostgreSQL CPU/RSS/PSS unavailable because descendant enumeration is incomplete or unproven. Explicit observed-subset values and OS lifetime wait4 remain separate; unknown whole-server cost is not zero.

### 07-java-native-sqlite

- Rejection changes the admitted case population; compare per-case success shares. No rejection latency is inserted into successful-operation histograms.

### 08-java-native-postgresql

- Rejection changes the admitted case population; compare per-case success shares. No rejection latency is inserted into successful-operation histograms.
- Whole-server steady PostgreSQL CPU/RSS/PSS unavailable because descendant enumeration is incomplete or unproven. Explicit observed-subset values and OS lifetime wait4 remain separate; unknown whole-server cost is not zero.

## 证据定位

summary.json保留输入文件SHA-256、原始回执路径、时间边界、采样覆盖与完整35类计数；所有数字可回到原始JSON/JSONL。原始记录没有被修改。本轮不与历史另一机器的数值直接拼接作同机前后对照。
