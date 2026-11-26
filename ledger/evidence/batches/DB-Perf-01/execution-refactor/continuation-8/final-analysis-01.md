# DB-Exec-02 执行路径测量分析

本报告只重算原始证据，不运行测量，不设置性能接受阈值。历史八段验收保持独立。

## 证据状态

| 观察 | 库 / cohort | 类型 | 状态 | timing credit |
|---|---|---|---|---|
| sqlite-final-01/candidate-c4 | sqlite / candidate | load | observed | True |
| sqlite-final-01/dapper-c4 | sqlite / dapper | load | observed | True |
| postgresql-final-01/candidate-c8 | postgresql / candidate | load | observed | True |
| postgresql-final-01/dapper-c8 | postgresql / dapper | load | observed | True |

Phase 未具备有效 timing 的格子：sqlite/before/1, sqlite/before/100, sqlite/before/1000, sqlite/candidate/1, sqlite/candidate/100, sqlite/candidate/1000, sqlite/dapper/1, sqlite/dapper/100, sqlite/dapper/1000, postgresql/before/1, postgresql/before/100, postgresql/before/1000, postgresql/candidate/1, postgresql/candidate/100, postgresql/candidate/1000, postgresql/dapper/1, postgresql/dapper/100, postgresql/dapper/1000

## 查询阶段

分位为原始样本的 nearest-rank，单位 μs；first execution 单独保存在 JSON。Dapper 可在 ReadComplete 内完成上游迭代器清理，Release 不能脱离 read+release 与总时间单独比较。

| 观察 / route | 行数 | 次数 | 构造 p50/p95/p99 | 首行 p50/p95/p99 | 余行 p50/p95/p99 | 释放 p50/p95/p99 | 总 B/op | GC0/1/2 | CPU μs/op | 峰值 RSS B |
|---|---:|---:|---|---|---|---|---:|---|---:|---:|

## 混合负载

吞吐覆盖已接受请求至 drain；offered 分位与 service 分位使用不同边界。失败和拒绝原样保留；start delay 包含生产者调度与排队，不能称为纯队列驻留时间。

| 观察 | 成功 / 失败 / 拒绝 | offered 目标 rate | 实际 attempted rate | 成功 op/s | 总 B/成功 | GC0/1/2 | CPU s | 峰值 RSS B | idle RSS B |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|
| sqlite-final-01/candidate-c4 | 4872560 / 0 / 527440 | 3000 | 3,000.000 | 2,706.936 | 24,790.092 | 42245/12822/20 | 4,859.354 | 45772800 | 38989824 |
| sqlite-final-01/dapper-c4 | 5389886 / 0 / 10114 | 3000 | 3,000.000 | 2,994.376 | 7,431.767 | 19390/180/18 | 3,142.248 | 33923072 | 31293440 |
| postgresql-final-01/candidate-c8 | 6120073 / 0 / 359927 | 3600 | 3,600.000 | 3,400.012 | 25,490.045 | 51230/17717/19 | 5,141.226 | 52674560 | 43261952 |
| postgresql-final-01/dapper-c8 | 6465624 / 0 / 14376 | 3600 | 3,600.000 | 3,591.997 | 7,316.433 | 10949/6996/122 | 2,995.325 | 43024384 | 34226176 |

| 观察 | population / boundary | 样本数 | p50 μs upper | p95 μs upper | p99 μs upper |
|---|---|---:|---:|---:|---:|
| sqlite-final-01/candidate-c4 | offered | 4872560 | 20,185.088 | 33,423.360 | 49,545.216 |
| sqlite-final-01/candidate-c4 | service | 4872560 | 544.768 | 4,882.432 | 12,976.128 |
| sqlite-final-01/candidate-c4 | all_terminal_offered | 4872560 | 20,185.088 | 33,423.360 | 49,545.216 |
| sqlite-final-01/candidate-c4 | start_delay | 4872560 | 19,136.512 | 30,801.920 | 43,778.048 |
| sqlite-final-01/dapper-c4 | offered | 5389886 | 207.872 | 3,031.040 | 8,585.216 |
| sqlite-final-01/dapper-c4 | service | 5389886 | 110.592 | 1,597.440 | 4,325.376 |
| sqlite-final-01/dapper-c4 | all_terminal_offered | 5389886 | 207.872 | 3,031.040 | 8,585.216 |
| sqlite-final-01/dapper-c4 | start_delay | 5389886 | 34.816 | 942.080 | 4,784.128 |
| postgresql-final-01/candidate-c8 | offered | 6120073 | 14,876.672 | 27,131.904 | 38,273.024 |
| postgresql-final-01/candidate-c8 | service | 6120073 | 888.832 | 10,551.296 | 16,580.608 |
| postgresql-final-01/candidate-c8 | all_terminal_offered | 6120073 | 14,876.672 | 27,131.904 | 38,273.024 |
| postgresql-final-01/candidate-c8 | start_delay | 6120073 | 12,976.128 | 22,282.240 | 32,243.712 |
| postgresql-final-01/dapper-c8 | offered | 6465624 | 370.688 | 3,325.952 | 8,519.680 |
| postgresql-final-01/dapper-c8 | service | 6465624 | 342.016 | 2,752.512 | 4,587.520 |
| postgresql-final-01/dapper-c8 | all_terminal_offered | 6465624 | 370.688 | 3,325.952 | 8,519.680 |
| postgresql-final-01/dapper-c8 | start_delay | 6465624 | 15.040 | 391.168 | 5,799.936 |

## SQL 与业务结果等同性

- Load sqlite-final-01/candidate-c4 ↔ sqlite-final-01/dapper-c4：相同业务契约=True；SQL 逐字相同=False；不同文本 35 项；可比较业务负载=True。完整 SQL 差异与配置差异保留在 JSON。
- Load postgresql-final-01/candidate-c8 ↔ postgresql-final-01/dapper-c8：相同业务契约=True；SQL 逐字相同=False；不同文本 35 项；可比较业务负载=True。完整 SQL 差异与配置差异保留在 JSON。

混合负载 SQL 的历史文本差异不会因业务结果 digest 相同而被抹去。FFI 次数和必须等待的协议回复未在这些 receipts 中序列化；SQL 执行与 protocol submission 的实测计数在 JSON 单独保留，不推算 RTT。

## 当前四段 1800 秒记录

四个原始证据完整：True；同机且含已记录 idle 无重叠：True。

- sqlite / candidate：complete-raw-evidence；观察=['sqlite-final-01/candidate-c4']。
- sqlite / dapper：complete-raw-evidence；观察=['sqlite-final-01/dapper-c4']。
- postgresql / candidate：complete-raw-evidence；观察=['postgresql-final-01/candidate-c8']。
- postgresql / dapper：complete-raw-evidence；观察=['postgresql-final-01/dapper-c8']。
- sqlite-final-01/candidate-c4：缺失秒=[]；无成功业务进展秒=[]；无消费行秒=[]；实际 case=35/35。
- sqlite-final-01/dapper-c4：缺失秒=[]；无成功业务进展秒=[]；无消费行秒=[]；实际 case=35/35。
- postgresql-final-01/candidate-c8：缺失秒=[]；无成功业务进展秒=[]；无消费行秒=[]；实际 case=35/35。
- postgresql-final-01/dapper-c8：缺失秒=[]；无成功业务进展秒=[]；无消费行秒=[]；实际 case=35/35。

## 缺项、失败与限制

- sqlite-final-01/candidate-c4 [note/observed_failures_or_rejections]：Raw ledger retains 0 failed operations and 527440 rejected arrivals; no SLO is invented.
- sqlite-final-01/dapper-c4 [note/observed_failures_or_rejections]：Raw ledger retains 0 failed operations and 10114 rejected arrivals; no SLO is invented.
- postgresql-final-01/candidate-c8 [note/observed_failures_or_rejections]：Raw ledger retains 0 failed operations and 359927 rejected arrivals; no SLO is invented.
- postgresql-final-01/dapper-c8 [note/observed_failures_or_rejections]：Raw ledger retains 0 failed operations and 14376 rejected arrivals; no SLO is invented.

总 B/op 包括业务对象、字符串/JSON、harness、框架与驱动；GC 按进程计数。该报告不扣除业务结果或 empty-driver，不据此声明框架 0 B。峰值 RSS 是进程生命周期 high-water，idle RSS 是实际 post-drain 观测。
