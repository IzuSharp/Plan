# PostgreSQL进程枚举缺口：本轮保留口径

## 实际观察

Root在02-dapper-postgresql正式运行期间授权只读资源文件尾部两条。2026-11-28T09:11:13.997438Z和09:11:14.253973Z两条只包含postmaster PID31/startTicks723009；其serverTotals.processCount=1，RSS=20144128B，own CPU=0 user/6 system ticks，already-reaped=46 user/24 system ticks，serverCpuGroup=null。`pgdata/postmaster.pid`首行也是31，设置文件锁定PG18.0，C8/persistent由冻结plan及Worker源码共同确认。

Dapper Worker在暖机前为每worker打开独立DbConnection，persistent路径保留连接直到drain，因此仅postmaster不能代表8个持久连接对应的backend工作。pre-run pg_stat_database.sessions=25是累计统计，不用它证明当前活跃backend数量。

证据：`server-observation-review-01.json`。只读取最后两条完整记录，记录各条原始SHA-256、读取时文件大小与末端offset；没有修改原记录、扫描PGdata、发起数据库请求或运行分析器。

## namespace与接口限定

当前exec的boot ID与campaign记录相同，但/proc/31不存在。因此没有在当前namespace借用裸PID31，未查看其他不匹配对象的children或CPU，也未nsenter或修改权限。

另对当前exec自身的父子关系作只读观察：python PID5/start778208、父bash PID2/start778207前后均稳定，stat已证实父子关系；父唯一task下`/proc/2/task/2/children`不存在。这确认**至少当前exec的proc接口没有提供observer所依赖的children文件**。它与正式资源只有postmaster的现象一致，但没有把当前PID2假装成正式runner的PID2，也未声称直接读到了PG所在namespace的相应路径。证据：`proc-children-interface-observation-01.json`。

冻结observer.tree只沿`/proc/<pid>/task/*/children`递归；空glob静默返回根进程。tree_totals的rssComplete只遍历已返回对象，不检测后代枚举完整性。这就是原始true值不能转成整库覆盖信用的原因。

## 本轮分析政策

- **整库steady CPU、RSS、PSS保持null。** 不把postmaster的0/近0 CPU或约20MiB RSS当成整库成本。
- 显式保留observedSubset/partial端点CPU、部分进程峰RSS/PSS、PID/startTicks、进程数范围、采样缺口与非原子负向跳变。已观察到0只可属于该子集，不能传播成整库0。
- 1+Concurrency只是必要进程数下限，不足以证明所有backend和后台均已覆盖；当前原始schema没有独立枚举覆盖认证。
- PG正常shutdown后的wait4保留其OS生命周期own/reaped-descendant计数。它可能仍覆盖已回收子进程，但不具有steady阶段隔离，不能用来补造steady数据或与partial采样相加。最终需结合正常退出及完整owner回执核对。
- 客户端计数、延迟和CPU可独立完成原有验收；PG整库steady缺测作为明确的指标限制，不伪造客户端业务错误，也不将“运行通过”写成“所有资源指标完整”。
- 不修改本轮冻结runner、matrix、客户端或原始记录。后续若修观察器，必须另立身份与覆盖验证，不能倒填本轮缺失的历史backend采样。
