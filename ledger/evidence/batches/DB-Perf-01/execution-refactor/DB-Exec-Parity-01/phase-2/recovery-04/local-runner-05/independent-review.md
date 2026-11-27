# Verified mixed wrapper / series：独立只读审查 05

审查者：`/root/worker_boundary_review`。本报告与作者封存的 `verified-wrapper-review-01` 分开保存。此次审查没有修改 wrapper、freeze helper、observer、consumer、SQL、运行条件或 CI，也没有启动新的 workload。最终两处 series 修正是在 root 的 quiet 窗口内仅阅读小文本确认的。

## 结论与源身份

当前没有发现阻断正常串行普通测量的命令、fixture、结果计数或已知生命周期缺陷。准许继续既定短测与后续冻结评审；这不是最终四段 30 分钟验收已经通过的结论。各 cell 的 wrapper 验证结果仍是权威，series 只串行调度和绑定其身份。

| 源 | 审查身份 |
| --- | --- |
| `experiments/recovery/run_verified_mixed_cell.py` v1 | `804fe0bfcd659c4d410a5c80f2adefb11f5f9fee863c3ea7b3bc9e25906fc2a2` |
| 同文件 v2 | `c0478eb0eb6b444e1923a4e694052b335933ae05aa98f4f403840e2b99c1007d` |
| `experiments/recovery/freeze_verified_mixed_inputs.py` | `61a7c94995dd257d3079a663019054aab1a9a1f91108ec6ae4f2abdb8ad86b66` |
| `experiments/recovery/run_proc_tree_observer.py` | `d7db0a60fd171e6124aecec078ee1bdd3331a9b534df340b2155f509ede4d8ff` |

上表身份沿用本轮实际源审查及作者回执；最后静默窗口没有重新遍历/散列所有大输入。v1 两个源文件副本在作者目录 `source-v1`，不能把第一条实际 cell 改标成 v2。v2 的有限差异是异常退出与持久 lease 防护、测量范围文字；没有改变消费者或测量计划。

## 正常路径审查

已读 wrapper 完整 v1、v2 有限 diff、freeze helper 和现有 helper/observer 的相关边界。输入快照重新核实际文件字节，绑定真实 PackageReference 消费者、生成代码、NuGet 依赖、ELF/符号 Build ID、native payload、构建回执以及基础设施。结果再核实际 PackageVersion、ELF 与 LoadedNativePath/SHA。默认 runtime 策略拒绝未允许的 runtime 压力/GC 参数及 loader 注入；普通消费者、诊断和 allocation lane 保持各自身份。

计划使用同一 35 类 manifest，prepared/persistent，batch32，tenant8/orders1024，client CPU0–3、PG4–7、observer8。每 worker 的 35 类 Verify 和 warmup64 均在正式计量外。SQLite 使用每 cell 的新 fixture；PG 使用每 cell 的新集群。长测只能显式 freeze 后以 1800 秒请求，`before-long` 与 `final-long` 的 variant 范围分开。`finalCredit` 不会因 wrapper 单独通过自动变为 true。

结果门禁核对 offered、queue、成功/错误/拒绝、35 类全部覆盖、逐秒 ledger、每类结果 digest、ownership、直方图与三个延迟口径。客户端 CPU 与 managed allocation 使用 steady 前后计数，进程 GC/暂停保持进程范围，不声称是框架独占分配。idle/release RSS 与 wait4 lifetime 另列。

实际 harness 在 `SteadyEndMonotonicNs` 记录后才调用 offered-load `Snapshot()` 并取得 drained timestamp。因此 wrapper 的 `steadyEnd <= drained + tolerance` 符合实际顺序；不能误读成这两个时间戳应相等到 1 微秒。

PG CPU 采用已独立审查的 PPid 观察器。当前成员各自 own + waited/reaped CPU 只相加一次，差分端点不再另加 wait4 lifetime。稳定身份集合不是原子 stat/wait4 转移证明；非原子传递、未被看见的短命/改父进程仍是明确边界。详细证据在 `experiments/relations-recovery-04/runner-review/independent-proc-observer-review-01`。

## v2 失败与退休边界

v2 在持有 cooperating wrapper flock 时先拒绝遗留 blocker，在启动 observer 前持久化 launch-intent，启动后登记 observer PID/startTicks。这样 SIGKILL 导致普通锁释放也不会默认为上一条已退休。

SIGTERM 转成可记录的失败路径，向 observer 发 SIGINT 等待其清理，最多 45 秒；未证明退休时保留持久 blocker。正常移除 blocker 前必须看见 observer 成功退休回执、初始化及客户端成功退出，以及 PG owner 的正面退出/清理证据。失败门禁后的未知状态不允许下一条自动开始。`clean_retirement` 证明成立之后的业务验证失败则不被误标为仍存在孤儿进程。

这提供 cooperating wrappers 之间的失败闭锁，不是对主机所有未知进程的全局排他证明。运行期间 quiet 是同机已知参与者的协作承诺。

## 现有验证回执的准确范围

作者 `static-01/validation.json` 共 **23 项**：6 条实际 prepare-only 输入路径、1 条匹配静态 freeze 正控、16 条请求/计划/freeze/runtime/覆盖保护负控。它不是“6 路外再加 23 项”，没有真实 SQL 或 PG endpoint 运行。

作者 `abort-control-01/validation.json` 共 9 项定向控制，覆盖已有 blocker、正常退休、observer 非零、client/server 清理错误、超时保留未知、替换 preflight 期间的实际 SIGTERM 与持久失败记录。该控制没有启动真实 consumer、SQL 或 PG；不能将其表述为已验证活数据库被 SIGTERM 中断的所有分支。

第一条真实 cell：`experiments/recovery/zero-cost-05/round-01/sqlite-candidate`，使用 v1，30 秒、rate500、queue64、idle5。已独立阅读其实际 result、validation 与生命周期回执：15,000 成功，0 拒绝/失败/retry/oracle，35 类全部正确，366,067 结果行；112 项输入前后身份一致，native owner 最终归零。client steady CPU 44.223518 秒，即 0.002948234533 秒/成功；managed 311,074,688 B，即 20,738.312533 B/成功。以上仅是此 cell 的过程与门禁核验，不单凭一条结果声明性能收益或 Dapper parity。

## Series 两处补丁的最终小文本复核

`run_verified_series.py` 已确认：

1. 在每条新 cell 或复用 cell 验收前，都再次核 plan、controller、wrapper 三个 SHA；该代码位于循环体内最后验收段，因此最后一格也覆盖。
2. 每条新/复用结果都绑定 `snapshot-before.json` 实际文件 SHA 到 validation，再检查 snapshot 的 provider、variant 与该格一致，并重算 canonical identity SHA，同步匹配 snapshot 与 validation。此前“只用 validation 的 provider/kind 可能将候选结果误复用为 before”的缺口已封闭。

已完成 cell 只有提供 exact validation SHA 才可复用；全新 cell 拒绝旧输出目录。series 任一失败停止并保存恢复状态，不进入下一条；SIGTERM 转发给当前 wrapper，让 wrapper 的持久 lease 处理未知退休。series 没有替代 wrapper 的完整业务/身份门禁，也不会自动授予最终验收信用。

## 剩余验证与审查范围

本审查不把短测代替四段 30 分钟正式测试，不把 non-atomic PG 观测说成全局精确服务器 CPU，不把整个进程的 GC/分配说成框架开销，也没有审查当前尚未实现的 tail-completion06 候选。任何后续消费者、wrapper 或 freeze 输入变化都需要新身份和相应新 cell，不能覆写这些已完成回执。
