# DB-Exec-02 执行路径测量分析

本报告只重算原始证据，不运行测量，不设置性能接受阈值。历史八段验收保持独立。

## 证据状态

| 观察 | 库 / cohort | 类型 | 状态 | timing credit |
|---|---|---|---|---|
| sqlite-baseline-01/before-c4 | sqlite / before | load | observed | True |
| sqlite-baseline-01/candidate-c4 | sqlite / candidate | load | observed | True |
| postgresql-baseline-01/before-c8 | postgresql / before | load | observed | True |
| postgresql-baseline-01/candidate-c8 | postgresql / candidate | load | observed | True |

Phase 未具备有效 timing 的格子：sqlite/before/1, sqlite/before/100, sqlite/before/1000, sqlite/candidate/1, sqlite/candidate/100, sqlite/candidate/1000, sqlite/dapper/1, sqlite/dapper/100, sqlite/dapper/1000, postgresql/before/1, postgresql/before/100, postgresql/before/1000, postgresql/candidate/1, postgresql/candidate/100, postgresql/candidate/1000, postgresql/dapper/1, postgresql/dapper/100, postgresql/dapper/1000

## 查询阶段

分位为原始样本的 nearest-rank，单位 μs；first execution 单独保存在 JSON。Dapper 可在 ReadComplete 内完成上游迭代器清理，Release 不能脱离 read+release 与总时间单独比较。

| 观察 / route | 行数 | 次数 | 构造 p50/p95/p99 | 首行 p50/p95/p99 | 余行 p50/p95/p99 | 释放 p50/p95/p99 | 总 B/op | GC0/1/2 | CPU μs/op | 峰值 RSS B |
|---|---:|---:|---|---|---|---|---:|---|---:|---:|

## 混合负载

吞吐覆盖已接受请求至 drain；offered 分位与 service 分位使用不同边界。失败和拒绝原样保留；start delay 包含生产者调度与排队，不能称为纯队列驻留时间。

| 观察 | 成功 / 失败 / 拒绝 | offered 目标 rate | 实际 attempted rate | 成功 op/s | 总 B/成功 | GC0/1/2 | CPU s | 峰值 RSS B | idle RSS B |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|
| sqlite-baseline-01/before-c4 | 65213 / 0 / 294787 | 3000 | 3,000.000 | 542.872 | 34,006.138 | 808/162/3 | 191.963 | 47321088 | 未记录 |
| sqlite-baseline-01/candidate-c4 | 320305 / 0 / 39695 | 3000 | 3,000.000 | 2,668.577 | 24,845.945 | 2783/816/3 | 324.833 | 45891584 | 未记录 |
| postgresql-baseline-01/before-c8 | 149007 / 0 / 282993 | 3600 | 3,600.000 | 1,241.453 | 34,856.686 | 1674/501/3 | 259.101 | 56135680 | 未记录 |
| postgresql-baseline-01/candidate-c8 | 415044 / 0 / 16956 | 3600 | 3,600.000 | 3,458.224 | 25,542.453 | 3496/1200/3 | 344.150 | 54632448 | 未记录 |

| 观察 | population / boundary | 样本数 | p50 μs upper | p95 μs upper | p99 μs upper |
|---|---|---:|---:|---:|---:|
| sqlite-baseline-01/before-c4 | offered | 65213 | 118,489.088 | 213,909.504 | 276,824.064 |
| sqlite-baseline-01/before-c4 | service | 65213 | 1,376.256 | 28,573.696 | 82,313.216 |
| sqlite-baseline-01/before-c4 | all_terminal_offered | 65213 | 118,489.088 | 213,909.504 | 276,824.064 |
| sqlite-baseline-01/before-c4 | start_delay | 65213 | 110,624.768 | 201,326.592 | 258,998.272 |
| sqlite-baseline-01/candidate-c4 | offered | 320305 | 21,102.592 | 34,340.864 | 50,855.936 |
| sqlite-baseline-01/candidate-c4 | service | 320305 | 548.864 | 5,013.504 | 13,238.272 |
| sqlite-baseline-01/candidate-c4 | all_terminal_offered | 320305 | 21,102.592 | 34,340.864 | 50,855.936 |
| sqlite-baseline-01/candidate-c4 | start_delay | 320305 | 20,054.016 | 31,588.352 | 44,040.192 |
| postgresql-baseline-01/before-c8 | offered | 149007 | 52,953.088 | 100,663.296 | 133,693.440 |
| postgresql-baseline-01/before-c8 | service | 149007 | 2,441.216 | 24,903.680 | 48,234.496 |
| postgresql-baseline-01/before-c8 | all_terminal_offered | 149007 | 52,953.088 | 100,663.296 | 133,693.440 |
| postgresql-baseline-01/before-c8 | start_delay | 149007 | 47,448.064 | 89,128.960 | 117,964.800 |
| postgresql-baseline-01/candidate-c8 | offered | 415044 | 13,762.560 | 25,296.896 | 34,340.864 |
| postgresql-baseline-01/candidate-c8 | service | 415044 | 897.024 | 10,158.080 | 15,859.712 |
| postgresql-baseline-01/candidate-c8 | all_terminal_offered | 415044 | 13,762.560 | 25,296.896 | 34,340.864 |
| postgresql-baseline-01/candidate-c8 | start_delay | 415044 | 11,796.480 | 20,840.448 | 28,442.624 |

## SQL 与业务结果等同性

- Load sqlite-baseline-01/before-c4 ↔ sqlite-baseline-01/candidate-c4：相同业务契约=True；SQL 逐字相同=True；不同文本 0 项；可比较业务负载=True。完整 SQL 差异与配置差异保留在 JSON。
- Load postgresql-baseline-01/before-c8 ↔ postgresql-baseline-01/candidate-c8：相同业务契约=True；SQL 逐字相同=True；不同文本 0 项；可比较业务负载=True。完整 SQL 差异与配置差异保留在 JSON。

混合负载 SQL 的历史文本差异不会因业务结果 digest 相同而被抹去。FFI 次数和必须等待的协议回复未在这些 receipts 中序列化；SQL 执行与 protocol submission 的实测计数在 JSON 单独保留，不推算 RTT。

## 当前四段 1800 秒记录

四个原始证据完整：False；同机且含已记录 idle 无重叠：False。

- sqlite / candidate：missing；观察=[]。
- sqlite / dapper：missing；观察=[]。
- postgresql / candidate：missing；观察=[]。
- postgresql / dapper：missing；观察=[]。

## 缺项、失败与限制

- sqlite-baseline-01/before-c4 [note/idle_rss_unrecorded]：This receipt does not record post-drain idle RSS
- sqlite-baseline-01/before-c4 [note/observed_failures_or_rejections]：Raw ledger retains 0 failed operations and 294787 rejected arrivals; no SLO is invented.
- sqlite-baseline-01/candidate-c4 [note/idle_rss_unrecorded]：This receipt does not record post-drain idle RSS
- sqlite-baseline-01/candidate-c4 [note/observed_failures_or_rejections]：Raw ledger retains 0 failed operations and 39695 rejected arrivals; no SLO is invented.
- postgresql-baseline-01/before-c8 [note/idle_rss_unrecorded]：This receipt does not record post-drain idle RSS
- postgresql-baseline-01/before-c8 [note/observed_failures_or_rejections]：Raw ledger retains 0 failed operations and 282993 rejected arrivals; no SLO is invented.
- postgresql-baseline-01/candidate-c8 [note/idle_rss_unrecorded]：This receipt does not record post-drain idle RSS
- postgresql-baseline-01/candidate-c8 [note/observed_failures_or_rejections]：Raw ledger retains 0 failed operations and 16956 rejected arrivals; no SLO is invented.

总 B/op 包括业务对象、字符串/JSON、harness、框架与驱动；GC 按进程计数。该报告不扣除业务结果或 empty-driver，不据此声明框架 0 B。峰值 RSS 是进程生命周期 high-water，idle RSS 是实际 post-drain 观测。
