# DB-Exec-02 执行路径测量分析

本报告只重算原始证据，不运行测量，不设置性能接受阈值。历史八段验收保持独立。

## 证据状态

| 观察 | 库 / cohort | 类型 | 状态 | timing credit |
|---|---|---|---|---|
| sqlite-offered-01/before-c4 | sqlite / before | load | observed | True |
| sqlite-offered-01/candidate-c4 | sqlite / candidate | load | observed | True |
| sqlite-offered-01/dapper-c4 | sqlite / dapper | load | observed | True |
| postgresql-offered-01/before-c8 | postgresql / before | load | observed | True |
| postgresql-offered-01/candidate-c8 | postgresql / candidate | load | observed | True |
| postgresql-offered-01/dapper-c8 | postgresql / dapper | load | observed | True |

Phase 未具备有效 timing 的格子：sqlite/before/1, sqlite/before/100, sqlite/before/1000, sqlite/candidate/1, sqlite/candidate/100, sqlite/candidate/1000, sqlite/dapper/1, sqlite/dapper/100, sqlite/dapper/1000, postgresql/before/1, postgresql/before/100, postgresql/before/1000, postgresql/candidate/1, postgresql/candidate/100, postgresql/candidate/1000, postgresql/dapper/1, postgresql/dapper/100, postgresql/dapper/1000

## 查询阶段

分位为原始样本的 nearest-rank，单位 μs；first execution 单独保存在 JSON。Dapper 可在 ReadComplete 内完成上游迭代器清理，Release 不能脱离 read+release 与总时间单独比较。

| 观察 / route | 行数 | 次数 | 构造 p50/p95/p99 | 首行 p50/p95/p99 | 余行 p50/p95/p99 | 释放 p50/p95/p99 | 总 B/op | GC0/1/2 | CPU μs/op | 峰值 RSS B |
|---|---:|---:|---|---|---|---|---:|---|---:|---:|

## 混合负载

吞吐覆盖已接受请求至 drain；offered 分位与 service 分位使用不同边界。失败和拒绝原样保留；start delay 包含生产者调度与排队，不能称为纯队列驻留时间。

| 观察 | 成功 / 失败 / 拒绝 | offered 目标 rate | 实际 attempted rate | 成功 op/s | 总 B/成功 | GC0/1/2 | CPU s | 峰值 RSS B | idle RSS B |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|
| sqlite-offered-01/before-c4 | 17465 / 0 / 72535 | 3000 | 3,000.000 | 580.156 | 32,593.875 | 214/23/2 | 48.195 | 46948352 | 未记录 |
| sqlite-offered-01/candidate-c4 | 84665 / 0 / 5335 | 3000 | 3,000.000 | 2,820.323 | 24,630.796 | 726/205/2 | 81.436 | 46673920 | 未记录 |
| sqlite-offered-01/dapper-c4 | 89930 / 0 / 70 | 3000 | 3,000.000 | 2,997.569 | 7,433.766 | 321/3/1 | 52.192 | 32100352 | 未记录 |
| postgresql-offered-01/before-c8 | 37394 / 0 / 70606 | 3600 | 3,600.000 | 1,240.894 | 35,520.074 | 419/123/2 | 64.855 | 51429376 | 未记录 |
| postgresql-offered-01/candidate-c8 | 100208 / 0 / 7792 | 3600 | 3,600.000 | 3,338.452 | 25,622.074 | 842/274/2 | 86.004 | 53538816 | 未记录 |
| postgresql-offered-01/dapper-c8 | 107590 / 0 / 410 | 3600 | 3,599.999 | 3,586.218 | 7,288.423 | 187/93/2 | 50.024 | 40579072 | 未记录 |

| 观察 | population / boundary | 样本数 | p50 μs upper | p95 μs upper | p99 μs upper |
|---|---|---:|---:|---:|---:|
| sqlite-offered-01/before-c4 | offered | 17465 | 109,051.904 | 205,520.896 | 255,852.544 |
| sqlite-offered-01/before-c4 | service | 17465 | 1,204.224 | 27,394.048 | 82,837.504 |
| sqlite-offered-01/before-c4 | all_terminal_offered | 17465 | 109,051.904 | 205,520.896 | 255,852.544 |
| sqlite-offered-01/before-c4 | start_delay | 17465 | 102,236.160 | 195,035.136 | 240,123.904 |
| sqlite-offered-01/candidate-c4 | offered | 84665 | 19,136.512 | 29,229.056 | 41,943.040 |
| sqlite-offered-01/candidate-c4 | service | 84665 | 536.576 | 4,784.128 | 12,582.912 |
| sqlite-offered-01/candidate-c4 | all_terminal_offered | 84665 | 19,136.512 | 29,229.056 | 41,943.040 |
| sqlite-offered-01/candidate-c4 | start_delay | 84665 | 17,956.864 | 26,738.688 | 35,651.584 |
| sqlite-offered-01/dapper-c4 | offered | 89930 | 202.752 | 3,375.104 | 8,978.432 |
| sqlite-offered-01/dapper-c4 | service | 89930 | 112.640 | 1,810.432 | 4,292.608 |
| sqlite-offered-01/dapper-c4 | all_terminal_offered | 89930 | 202.752 | 3,375.104 | 8,978.432 |
| sqlite-offered-01/dapper-c4 | start_delay | 89930 | 32.128 | 1,449.984 | 5,832.704 |
| postgresql-offered-01/before-c8 | offered | 37394 | 52,690.944 | 101,711.872 | 133,693.440 |
| postgresql-offered-01/before-c8 | service | 37394 | 2,342.912 | 24,903.680 | 47,710.208 |
| postgresql-offered-01/before-c8 | all_terminal_offered | 37394 | 52,690.944 | 101,711.872 | 133,693.440 |
| postgresql-offered-01/before-c8 | start_delay | 37394 | 47,185.920 | 89,653.248 | 116,391.936 |
| postgresql-offered-01/candidate-c8 | offered | 100208 | 15,859.712 | 28,311.552 | 41,943.040 |
| postgresql-offered-01/candidate-c8 | service | 100208 | 946.176 | 10,616.832 | 16,515.072 |
| postgresql-offered-01/candidate-c8 | all_terminal_offered | 100208 | 15,859.712 | 28,311.552 | 41,943.040 |
| postgresql-offered-01/candidate-c8 | start_delay | 100208 | 13,959.168 | 23,330.816 | 36,175.872 |
| postgresql-offered-01/dapper-c8 | offered | 107590 | 405.504 | 4,227.072 | 13,959.168 |
| postgresql-offered-01/dapper-c8 | service | 107590 | 362.496 | 2,981.888 | 5,275.648 |
| postgresql-offered-01/dapper-c8 | all_terminal_offered | 107590 | 405.504 | 4,227.072 | 13,959.168 |
| postgresql-offered-01/dapper-c8 | start_delay | 107590 | 16.320 | 1,523.712 | 11,403.264 |

## SQL 与业务结果等同性

- Load sqlite-offered-01/before-c4 ↔ sqlite-offered-01/candidate-c4：相同业务契约=True；SQL 逐字相同=True；不同文本 0 项；可比较业务负载=True。完整 SQL 差异与配置差异保留在 JSON。
- Load sqlite-offered-01/before-c4 ↔ sqlite-offered-01/dapper-c4：相同业务契约=True；SQL 逐字相同=False；不同文本 35 项；可比较业务负载=True。完整 SQL 差异与配置差异保留在 JSON。
- Load sqlite-offered-01/candidate-c4 ↔ sqlite-offered-01/dapper-c4：相同业务契约=True；SQL 逐字相同=False；不同文本 35 项；可比较业务负载=True。完整 SQL 差异与配置差异保留在 JSON。
- Load postgresql-offered-01/before-c8 ↔ postgresql-offered-01/candidate-c8：相同业务契约=True；SQL 逐字相同=True；不同文本 0 项；可比较业务负载=True。完整 SQL 差异与配置差异保留在 JSON。
- Load postgresql-offered-01/before-c8 ↔ postgresql-offered-01/dapper-c8：相同业务契约=True；SQL 逐字相同=False；不同文本 35 项；可比较业务负载=True。完整 SQL 差异与配置差异保留在 JSON。
- Load postgresql-offered-01/candidate-c8 ↔ postgresql-offered-01/dapper-c8：相同业务契约=True；SQL 逐字相同=False；不同文本 35 项；可比较业务负载=True。完整 SQL 差异与配置差异保留在 JSON。

混合负载 SQL 的历史文本差异不会因业务结果 digest 相同而被抹去。FFI 次数和必须等待的协议回复未在这些 receipts 中序列化；SQL 执行与 protocol submission 的实测计数在 JSON 单独保留，不推算 RTT。

## 当前四段 1800 秒记录

四个原始证据完整：False；同机且含已记录 idle 无重叠：False。

- sqlite / candidate：missing；观察=[]。
- sqlite / dapper：missing；观察=[]。
- postgresql / candidate：missing；观察=[]。
- postgresql / dapper：missing；观察=[]。

## 缺项、失败与限制

- sqlite-offered-01/before-c4 [note/idle_rss_unrecorded]：This receipt does not record post-drain idle RSS
- sqlite-offered-01/before-c4 [note/observed_failures_or_rejections]：Raw ledger retains 0 failed operations and 72535 rejected arrivals; no SLO is invented.
- sqlite-offered-01/candidate-c4 [note/idle_rss_unrecorded]：This receipt does not record post-drain idle RSS
- sqlite-offered-01/candidate-c4 [note/observed_failures_or_rejections]：Raw ledger retains 0 failed operations and 5335 rejected arrivals; no SLO is invented.
- sqlite-offered-01/dapper-c4 [note/idle_rss_unrecorded]：This receipt does not record post-drain idle RSS
- sqlite-offered-01/dapper-c4 [note/observed_failures_or_rejections]：Raw ledger retains 0 failed operations and 70 rejected arrivals; no SLO is invented.
- postgresql-offered-01/before-c8 [note/idle_rss_unrecorded]：This receipt does not record post-drain idle RSS
- postgresql-offered-01/before-c8 [note/observed_failures_or_rejections]：Raw ledger retains 0 failed operations and 70606 rejected arrivals; no SLO is invented.
- postgresql-offered-01/candidate-c8 [note/idle_rss_unrecorded]：This receipt does not record post-drain idle RSS
- postgresql-offered-01/candidate-c8 [note/observed_failures_or_rejections]：Raw ledger retains 0 failed operations and 7792 rejected arrivals; no SLO is invented.
- postgresql-offered-01/dapper-c8 [note/idle_rss_unrecorded]：This receipt does not record post-drain idle RSS
- postgresql-offered-01/dapper-c8 [note/observed_failures_or_rejections]：Raw ledger retains 0 failed operations and 410 rejected arrivals; no SLO is invented.

总 B/op 包括业务对象、字符串/JSON、harness、框架与驱动；GC 按进程计数。该报告不扣除业务结果或 empty-driver，不据此声明框架 0 B。峰值 RSS 是进程生命周期 high-water，idle RSS 是实际 post-drain 观测。
