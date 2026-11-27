# 既有差距来源澄清 07

本说明追加在已冻结 README 之后，不修改原报告、原 receipt 或其 SHA。原 README SHA256 为 `9b5e8059baf96b8d09b39d75fbac7976e53d0d39834f7a334b28c6448747e532`。

原报告开头 text1000 CPU 的 SQLite 6.35–6.88 倍、PostgreSQL 8.53–9.76 倍，来自 `worktrees/Plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/DB-Exec-Parity-01/phase-2/recovery-04/combined-screen-05.md` 的两轮 integrated05 组合筛查。它们不是之后 ordinary-screen-01 的同一批进程。

**今后表述保留 integrated05 当前短测差距，统一引用 `experiments/recovery/retained05-gap-summary-01/README.md` 与同目录 summary.json。** 该汇总只重读 tail06 阶段 ordinary-screen-01 的 24 个既有进程，取 integrated05 baseline 和同轮 Dapper，排除已放弃的 tail06 candidate；prepared/persistent、C1、batch32、每格 2048 业务、暖机 128。其 text1000 CPU 比率为 SQLite **5.1476–6.5897 倍**、PostgreSQL **8.1619–9.9623 倍**。

两组属于不同时间及样本长度的既有筛查，不混合平均、不拼成同一轮、不据此计算新的改进幅度。差异不改变只读判断的边界：仍有显著 CPU/资源差距，尚未证明全部差距可回收，也未证明全部为契约必然成本。没有新测量。
