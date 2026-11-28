# 固定到达率 harness：CPU 与延迟口径静态复核

## 结论

**双方核心到达、容量拒绝、接受任务排空和每业务延迟契约一致；producer 的高层等待策略也一致。等待原语和消费者执行机制存在明确差异，源码不能证明机器开销相同。报告中的客户端 CPU 包含压测调度。**

本次只在 CPU 8 读取小型源码并核对 SHA-256，没有运行客户端、empty-driver、校准、构建或数据库请求，没有读取正式结果或大型资源日志，没有改动任何冻结实现。这里记录源码事实与边界，不对实际性能差距作归因。原 C# Shared/OfferedLoad 与 EF 客户端副本的完整文件 SHA-256 相同。[CS-HARNESS、EF-HARNESS]

## 等待与调度逐项对照

| 项目 | C# | Java | 源码支持的结论 |
| --- | --- | --- | --- |
| 计划到达 | `ceil(seconds*rate)`；`Start + i*(Frequency/rate)` | 相同计划数；`began + i*(1e9/rate)` | 都按绝对计划时刻，不用上一业务完成时间安排下一到达。迟到时继续尝试每个原计划索引，不跳过积压计划。 |
| Producer 长等待 | 剩余时间大于 `Stopwatch.Frequency/500` 时 `Thread.Sleep(1)` | 剩余时间大于 2,000,000 ns 时 `Thread.sleep(1)` | 名义阈值都是 2 ms，均请求睡眠 1 ms；实际睡眠与唤醒时机不由这段源码给出。 |
| Producer 短等待 | 静态 `Thread.SpinWait(32)` | 32 次 `Thread.onSpinWait()` | 高层短自旋策略相同；32 这个参数不能转换成相同指令数、时间或 CPU 消耗。 |
| 显式 yield/park | producer 没有 `Thread.Yield`、`Task.Yield` 或 `SpinWait.SpinOnce` | producer 没有 `Thread.yield` 或 `LockSupport.park` | 不能声称每次到达显式 yield/park，也不能据此声称底层没有 OS 等待。 |
| 启动 | producer 用 `ManualResetEventSlim`；消费者先建立 async Task 等待 channel | producer 与固定 worker Thread 用 `CountDownLatch` 就绪/启动门 | 初始化在主要测量边界之前完成，释放门后的执行仍进入进程 CPU。 |
| 容量录入 | bounded `Channel<Job>`；只调用 `TryWrite`，满队列计 rejected | 预分配 primitive ring；`synchronized offer`，满队列返回 false | 都不等待空容量。Java 仍需进入 monitor；本次未读 .NET Channel 内部，不能把容量非等待说成 lock-free。 |
| 空队列 | `await WaitToReadAsync()`，随后 `TryRead` 排空可读项 | `Object.wait()`，录入 `notify()`，结束 `notifyAll()` | 消费者等待原语不同。 |
| 业务调用 | `await ValueTask<OperationResult>`，`ConfigureAwait(false)` | 固定平台线程同步调用 `scheduled` | C# await 不保证每次实际挂起或换线程；Java harness 没有相同的 async continuation 消费模型。 |
| 每秒统计 | `Interlocked.Add` | `AtomicLongArray.addAndGet` | 两边统计工作进入整个客户端 CPU，原子操作成本没有分段测量。 |

证据：CS-HARNESS 的 constructor、Start、WaitUntil、Produce、Consume、Record；JAVA-HARNESS 的 constructor、start、waitUntil、produce、consume、Queue.offer/take/complete、record。

C# channel 配置为 `FullMode=Wait`，但 producer 用的是 `TryWrite`，没有等待容量的 `WriteAsync`；`TryWrite` 失败直接计拒绝。`AllowSynchronousContinuations=false` 是明确配置，仍不能用它推导每次业务的 OS 上下文切换次数。[CS-HARNESS]

双方 producer 都在 `TryWrite/offer` 之前取得 `now`，再用该值记录 sent/rejected 的每秒桶。它是尝试录入前的时间戳，不能作为实际入队完成时刻；报告没有据此计算纯队列驻留。[CS-HARNESS.Produce、JAVA-HARNESS.produce]

本轮声明到达率 3,000/s 和 3,600/s 对应名义间隔约 333.33 µs 和 277.78 µs，都小于 2 ms 的长等待阈值。这个参数关系适用于双方；它是源码与参数的算术观察，不是测得的分支次数或 CPU 利用率。不能据此给任一方扣除“一个核”或固定 CPU 秒数。

## 每业务延迟边界

定义 `t_due` 为计划到达时刻，`t_begin` 为成功出队之后记录的时刻，`t_end` 为业务调用返回后记录的时刻。双方均记录：

- **StartDelay：**`t_begin - t_due`。
- **成功 Service：**`t_end - t_begin`。
- **成功 Scheduled：**`t_end - t_due`。
- **AllCompletedScheduled：**成功或失败的已开始业务，从计划时刻到返回/异常捕获时刻。

`StartDelay` 包含 producer 迟发、录入过程、实际队列等待、消费者唤醒/调度以及出队到 `t_begin` 的边界工作。Job 只保存计划时刻，没有保存实际入队时刻，因此它无法单独给出纯队列驻留时间。[CS-HARNESS.Consume、JAVA-HARNESS.consume]

`Service` 的起点在出队之后、started 每秒计数及 start-delay histogram 更新之前；因此这些起点后的统计工作也在 service 区间。业务调用内的 case 选择、业务/驱动/DTO 工作和结果校验，以及返回前更新的 **per-case 成功/行数计数**都在区间内；C# 还在返回前更新 per-case suspension 计数。失败路径的 per-case 计数落在对应 `AllCompletedScheduled` 边界内；失败没有成功 `Service` 样本。终点在业务调用返回后、**OfferedLoad 外层**成功计数与完成直方图更新之前。只有这些外层后续完成统计不在该业务的 service 样本内，它们仍在整个进程的 CPU 测量窗口内。[CS-HARNESS.Consume、JAVA-HARNESS.consume、DAPPER-MEASURE.Worker.ExecuteScheduled/Execute/Validate、EF-MEASURE 同名方法、JAVA-WORKLOAD.scheduled/executeValidated]

拒绝业务没有 `t_begin/t_end`，不进入这些已开始业务的延迟样本；录入和拒绝计数消耗仍在进程 CPU 中。`AllCompleted` 包括成功与失败的已开始业务，不包括拒绝。四类 histogram 都是 8,192 bins、每指数 128 个子区间；时钟单位、转换及具体算术并非逐字相同。[CS-HARNESS.Produce/Consume/Add/Snapshot、JAVA-HARNESS.produce/consume/add/receipt]

## CPU 计数范围

C# 的 `ProcessReading.Read` 读取当前进程的 user/kernel CPU；Java 的 `ProcessStats.read` 读取 `/proc/self/stat` 的进程 `utime/stime` 并按 `CLK_TCK` 换算。两边计算的都是：

```text
CPU/成功业务 = 客户端进程(user CPU差值 + system CPU差值) / 成功业务数
```

harness 对象和主要暖机在 before snapshot 之前建立。before/after snapshot 包住 producer 启动、全部 offering 与 accepted-work drain，以及相邻的计数器/观察工作。这个分子涵盖窗口内的 producer 等时/自旋、队列及消费者调度、统计、业务/驱动/DTO 与校验、进程内 SQLite、运行时和 GC 工作；若 JIT 等后台线程在窗口内工作，也属于进程计数。外置 PostgreSQL 服务端 CPU 不在客户端进程计数中。[DAPPER-MEASURE.ProcessReading.Read/Measurement.Run、EF-MEASURE 同名方法、JAVA-MAIN.run、JAVA-STATS.read]

C# 的大型 `OfferedLoad.Snapshot`、per-case 报告聚合，以及 Java 的 `receipt`、per-case 报告聚合在 process-after 读数之后执行；不能把全部报告构造都算进主要 CPU 窗口。窗口内包括的是每业务计数/直方图及相邻观察工作。

进程 CPU 累计线程实际获得 CPU 的执行时间；Sleep/monitor 等阻塞的墙钟等待应与 CPU 秒数区分，调用和唤醒处理消耗的 CPU 工作仍会计入。

没有单独读取 producer 或 consumer 的线程 CPU，也没有记录 Sleep/Spin/monitor/channel 的分段 CPU。成功数这个分母不包含拒绝和失败，而分子仍包含对应已发生的录入/执行/错误处理工作。报告应保留这个进程级定义，不把它改称经过工具成本扣除的数据访问 CPU。

## 排空与总区间采样点差异

两边都尝试所有计划索引，至少等到 offering deadline，并排空全部已接受任务，随后检查 `attempted=planned=sent+rejected` 与 `started=sent=succeeded+failed`。[CS-HARNESS.Produce/Snapshot、JAVA-HARNESS.produce/join/receipt]

C# 的 `Completion` 是消费者 Tasks 和 `producerDone` 的 `Task.WhenAll`；它不等于 producer Thread 已被 join，后者在 `Dispose` 才执行。`Measurement.Run` 在 `await completed` 返回后读取 `endedAt`，用它给出 `SteadyEndMonotonicNs/EffectiveSeconds`；随后读取 after counters/CPU，再调用 `OfferedLoad.Snapshot()`。后者此时才读取自己的 `end`，作为嵌套 `OfferedLoad.DrainedTicks`。所以 C# 这两个结束时刻并非同一次读钟。[DAPPER-MEASURE.Measurement.Run、EF-MEASURE.Measurement.Run、CS-HARNESS.Snapshot]

Java `join()` 在 producer 与所有 worker Thread 结束后保存 `drained`；`SteadyEndMonotonicNs`、`EffectiveSeconds` 与嵌套 `DrainedTicks` 共用该值。after counters/CPU 随后读取，receipt 汇总再后。[JAVA-HARNESS.join/receipt、JAVA-MAIN.run]

两边的主要 effective 终点与 process-after 读数均在 worker/session/source 关闭之前；这里的 full drain 指已准入业务全部完成，不能理解为连接释放也在主要计时内。两边 producer 都先记录 offered-end 时刻，再读取 allocation/GC 计数，随后关闭队列；这段观察成本仍可能进入进程 CPU 和 drain 区间，字段相同不能证明成本相同。[CS-HARNESS.Produce/Dispose、JAVA-HARNESS.produce、DAPPER-MEASURE、EF-MEASURE、JAVA-MAIN]

这些属于已证实的采样点差异。本次没有测量其大小。主进程 CPU 的 before/after 读数还包括各自边界附近的计数和观察调用，不能假设与 wall-clock start/end 在同一指令上取样。

请求 15 秒的释放后 idle 在主要 CPU/end 读数及连接释放之后单独记录，实际时长按各格回执：C# 用 `await Task.Delay`，Java 用 `Thread.sleep`。外部生命周期采样若覆盖启动、暖机或 idle，需要使用各自记录的区间解释，不能默认等于主 receipt 的 CPU 差值。[DAPPER-MEASURE、EF-MEASURE、JAVA-MAIN]

## 本次未证明的事项

本次没有采集以下数据，因此不提供对应比例或性能解释：

- Producer、队列、业务/驱动、DTO/校验、JIT/GC 各自 CPU 秒数或占比。
- `Thread.SpinWait(32)` 与 32 次 `Thread.onSpinWait()` 的真实机器指令及成本。
- 实际 sleep 时间、park/futex/yield 次数、上下文切换、抢占和核迁移。
- C# await 同步完成/异步恢复比例，Java monitor 的竞争和唤醒延迟。
- 实际入队时刻、纯队列驻留时间、迟发与追赶突发的出现次数。
- 上述任何源码差异对正式吞吐、拒绝、延迟或 CPU 差距的贡献。

本轮不运行 empty-driver，不做校准，不从总 CPU 中减去猜测的调度常数，也不改变冻结客户端。

## 建议最终报告口径

> 客户端 CPU/成功操作包含固定到达率 producer、队列与消费者调度、业务与驱动执行及进程内运行时工作。两套 harness 采用相同的核心到达/拒绝/排空契约和高层短等待策略；C# 与 Java 的等待原语及消费模型不同。本轮未测量调度器分段 CPU，报告保留原始进程口径，不据源码扣减或归因性能差距。

## 源码身份

以下 SHA-256 均由本次只读复核取得，并在更新报告前重读确认未变。`/root/baseline_recovery` 另行在 CPU 8 对小型源码做了只读交叉复核；主要结论一致，service 内外统计、completion/join、连接释放和报告聚合的边界补充已纳入。完整绝对路径、字节数、函数证据和机器可读结论见同名 JSON。

| ID | 源码路径（任务根目录下） | SHA-256 |
| --- | --- | --- |
| CS-HARNESS | `worktree-Korda/benchmarks/db-perf/managed/Shared/OfferedLoad.cs` | `2adb14584476da8b8a49bb2e5db6bd85b136f3823aee5e2f004bc263eb2bc92b` |
| EF-HARNESS | `worktree-Plan/ledger/evidence/batches/DB-Perf-01/runtime-comparison-01/clients/efcore/OfferedLoad.cs` | `2adb14584476da8b8a49bb2e5db6bd85b136f3823aee5e2f004bc263eb2bc92b` |
| JAVA-HARNESS | `worktree-Plan/ledger/evidence/batches/DB-Perf-01/runtime-comparison-01/clients/java/src/main/java/org/korda/compare/OfferedLoad.java` | `b43abb84ae61d1806d5b46c6b1666609e4ee5338919c9b1f71133e4b46e33b05` |
| DAPPER-MEASURE | `worktree-Korda/benchmarks/db-perf/managed/Dapper/Measurement.cs` | `fdf8f6354f3eb33bb9a77030ee050cb846d1d3eca6bcc08512df8b0d6b837952` |
| EF-MEASURE | `worktree-Plan/ledger/evidence/batches/DB-Perf-01/runtime-comparison-01/clients/efcore/Measurement.cs` | `43e242265cff53689786cc4612c06ff4097075cf6f5349a044c664343fb1b6b5` |
| JAVA-MAIN | `worktree-Plan/ledger/evidence/batches/DB-Perf-01/runtime-comparison-01/clients/java/src/main/java/org/korda/compare/Main.java` | `c43c7ed7892b286862561b7fafc08a53b1ab002a341507410c2e791f518d2ec7` |
| JAVA-STATS | `worktree-Plan/ledger/evidence/batches/DB-Perf-01/runtime-comparison-01/clients/java/src/main/java/org/korda/compare/ProcessStats.java` | `aaa498291700c4751af8431852a74fe9d2f5027d41f2d7c38ee13a56bbabadb7` |
| JAVA-WORKLOAD | `worktree-Plan/ledger/evidence/batches/DB-Perf-01/runtime-comparison-01/clients/java/src/main/java/org/korda/compare/Workload.java` | `b5e33a50d1e5e0b0cb4c8a79035eba5c64c023ffe2d866adee64f955b2fd9e74` |
