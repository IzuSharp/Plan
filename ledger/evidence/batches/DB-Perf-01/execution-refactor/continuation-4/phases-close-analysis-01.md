# DB-Exec-02 执行路径测量分析

本报告只重算原始证据，不运行测量，不设置性能接受阈值。历史八段验收保持独立。

## 证据状态

| 观察 | 库 / cohort | 类型 | 状态 | timing credit |
|---|---|---|---|---|
| sqlite-before-rows1 | sqlite / before | phase | missing | False |
| sqlite-before-rows100 | sqlite / before | phase | missing | False |
| sqlite-before-rows1000 | sqlite / before | phase | missing | False |
| sqlite-candidate-rows1 | sqlite / candidate | phase | missing | False |
| sqlite-candidate-rows100 | sqlite / candidate | phase | missing | False |
| sqlite-candidate-rows1000 | sqlite / candidate | phase | missing | False |
| sqlite-dapper-rows1 | sqlite / dapper | phase | missing | False |
| sqlite-dapper-rows100 | sqlite / dapper | phase | missing | False |
| sqlite-dapper-rows1000 | sqlite / dapper | phase | missing | False |
| postgresql-before-rows1 | postgresql / before | phase | missing | False |
| postgresql-before-rows100 | postgresql / before | phase | missing | False |
| postgresql-before-rows1000 | postgresql / before | phase | missing | False |
| postgresql-candidate-rows1 | postgresql / candidate | phase | missing | False |
| postgresql-candidate-rows100 | postgresql / candidate | phase | missing | False |
| postgresql-candidate-rows1000 | postgresql / candidate | phase | missing | False |
| postgresql-dapper-rows1 | postgresql / dapper | phase | missing | False |
| postgresql-dapper-rows100 | postgresql / dapper | phase | missing | False |
| postgresql-dapper-rows1000 | postgresql / dapper | phase | missing | False |

Phase 未具备有效 timing 的格子：sqlite/before/1, sqlite/before/100, sqlite/before/1000, sqlite/candidate/1, sqlite/candidate/100, sqlite/candidate/1000, sqlite/dapper/1, sqlite/dapper/100, sqlite/dapper/1000, postgresql/before/1, postgresql/before/100, postgresql/before/1000, postgresql/candidate/1, postgresql/candidate/100, postgresql/candidate/1000, postgresql/dapper/1, postgresql/dapper/100, postgresql/dapper/1000

## 查询阶段

分位为原始样本的 nearest-rank，单位 μs；first execution 单独保存在 JSON。Dapper 可在 ReadComplete 内完成上游迭代器清理，Release 不能脱离 read+release 与总时间单独比较。

| 观察 / route | 行数 | 次数 | 构造 p50/p95/p99 | 首行 p50/p95/p99 | 余行 p50/p95/p99 | 释放 p50/p95/p99 | 总 B/op | GC0/1/2 | CPU μs/op | 峰值 RSS B |
|---|---:|---:|---|---|---|---|---:|---|---:|---:|

## 混合负载

吞吐覆盖已接受请求至 drain；offered 分位与 service 分位使用不同边界。失败和拒绝原样保留；start delay 包含生产者调度与排队，不能称为纯队列驻留时间。

| 观察 | 成功 / 失败 / 拒绝 | offered 目标 rate | 实际 attempted rate | 成功 op/s | 总 B/成功 | GC0/1/2 | CPU s | 峰值 RSS B | idle RSS B |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|

| 观察 | population / boundary | 样本数 | p50 μs upper | p95 μs upper | p99 μs upper |
|---|---|---:|---:|---:|---:|

## SQL 与业务结果等同性


混合负载 SQL 的历史文本差异不会因业务结果 digest 相同而被抹去。FFI 次数和必须等待的协议回复未在这些 receipts 中序列化；SQL 执行与 protocol submission 的实测计数在 JSON 单独保留，不推算 RTT。

## 当前四段 1800 秒记录

四个原始证据完整：False；同机且含已记录 idle 无重叠：False。

- sqlite / candidate：missing；观察=[]。
- sqlite / dapper：missing；观察=[]。
- postgresql / candidate：missing；观察=[]。
- postgresql / dapper：missing；观察=[]。

## 缺项、失败与限制

- sqlite-before-rows1 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-sqlite-01/before-rows1.command.json'
- sqlite-before-rows1 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-sqlite-01/before-rows1.json'
- sqlite-before-rows100 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-sqlite-01/before-rows100.command.json'
- sqlite-before-rows100 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-sqlite-01/before-rows100.json'
- sqlite-before-rows1000 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-sqlite-01/before-rows1000.command.json'
- sqlite-before-rows1000 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-sqlite-01/before-rows1000.json'
- sqlite-candidate-rows1 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-sqlite-01/candidate-rows1.command.json'
- sqlite-candidate-rows1 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-sqlite-01/candidate-rows1.json'
- sqlite-candidate-rows100 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-sqlite-01/candidate-rows100.command.json'
- sqlite-candidate-rows100 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-sqlite-01/candidate-rows100.json'
- sqlite-candidate-rows1000 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-sqlite-01/candidate-rows1000.command.json'
- sqlite-candidate-rows1000 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-sqlite-01/candidate-rows1000.json'
- sqlite-dapper-rows1 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-sqlite-01/dapper-rows1.command.json'
- sqlite-dapper-rows1 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-sqlite-01/dapper-rows1.json'
- sqlite-dapper-rows100 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-sqlite-01/dapper-rows100.command.json'
- sqlite-dapper-rows100 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-sqlite-01/dapper-rows100.json'
- sqlite-dapper-rows1000 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-sqlite-01/dapper-rows1000.command.json'
- sqlite-dapper-rows1000 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-sqlite-01/dapper-rows1000.json'
- postgresql-before-rows1 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-postgresql-01/before-rows1.command.json'
- postgresql-before-rows1 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-postgresql-01/before-rows1.json'
- postgresql-before-rows100 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-postgresql-01/before-rows100.command.json'
- postgresql-before-rows100 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-postgresql-01/before-rows100.json'
- postgresql-before-rows1000 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-postgresql-01/before-rows1000.command.json'
- postgresql-before-rows1000 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-postgresql-01/before-rows1000.json'
- postgresql-candidate-rows1 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-postgresql-01/candidate-rows1.command.json'
- postgresql-candidate-rows1 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-postgresql-01/candidate-rows1.json'
- postgresql-candidate-rows100 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-postgresql-01/candidate-rows100.command.json'
- postgresql-candidate-rows100 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-postgresql-01/candidate-rows100.json'
- postgresql-candidate-rows1000 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-postgresql-01/candidate-rows1000.command.json'
- postgresql-candidate-rows1000 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-postgresql-01/candidate-rows1000.json'
- postgresql-dapper-rows1 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-postgresql-01/dapper-rows1.command.json'
- postgresql-dapper-rows1 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-postgresql-01/dapper-rows1.json'
- postgresql-dapper-rows100 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-postgresql-01/dapper-rows100.command.json'
- postgresql-dapper-rows100 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-postgresql-01/dapper-rows100.json'
- postgresql-dapper-rows1000 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-postgresql-01/dapper-rows1000.command.json'
- postgresql-dapper-rows1000 [missing/missing_file]：[Errno 2] No such file or directory: '/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-plan/phases-close-postgresql-01/dapper-rows1000.json'

总 B/op 包括业务对象、字符串/JSON、harness、框架与驱动；GC 按进程计数。该报告不扣除业务结果或 empty-driver，不据此声明框架 0 B。峰值 RSS 是进程生命周期 high-water，idle RSS 是实际 post-drain 观测。
