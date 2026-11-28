# 最终报告结构

1. 八格实际完成状态、时间、版本与身份；任何失败/未运行项逐项列明。
2. 历史条件沿用范围及本轮变化：同一35业务/数据库/到达率/队列/时长；C#192MiB请求配置无cgroup；Java25 Native。
3. 成功数、拒绝、业务及oracle错误、有效吞吐；计划1800秒与实际producer/drain区分。
4. 成功service和scheduled p50/p95/p99、StartDelay；拒绝样本范围。
5. 客户端steady CPU/success、lifetime CPU分列；全进程分配和可见归因限制。
6. 独立内存表：OS wait4生命周期maxRSS、消费者ProcessAfter自报峰、同身份完整steady窗口内observer离散采样RSS/PSS峰；三种来源不合并或强制排序。另列实际idle时长与释放后RSS、Satori实际GC available；无硬限、峰值差异原因或泄漏推断。
7. C#各generation计数与API pause duration、Java每collector collection time；未采集/unsupported为null。
8. PG内部采样树CPU和边界缺口、lifetime wait4与宽窗口pg_stat_database单列。
9. 35类计划与实际成功构成、派生拒绝；与Dapper差距的描述性比较及组合偏差。
10. 单次长run的限制、无GC单因素因果/统计显著/上限拐点或已对齐承诺；原始证据及恢复位置。

此模板不包含任何提前填入的性能结果。
