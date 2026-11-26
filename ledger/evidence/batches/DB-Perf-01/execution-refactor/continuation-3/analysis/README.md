# DB-Exec-02 本地证据分析

这里仅包含离线分析器。脚本不会启动产品、数据库、编译器、采样器或负载；唯一子进程是读取 helper 仓库当前提交的 `git rev-parse`。等一个证据目录的 runner 完全退出后再读取它。输入文件的 SHA-256 会保存在输出中，分析结束时重新检查字节是否改变；输出使用新文件，保留所有旧记录。

## 当前 18 份 phase receipt

`prepare_phase_index.py` 登记固定目录和文件名，不读取测量结果，也不挑选重复运行中更快的一份。它预期 `phases-sqlite-01` 和 `phases-postgresql-01` 中各有 `before-rows1/100/1000`、`candidate-rows1/100/1000`、`dapper-rows1/100/1000`，每个名字对应 `.json`、`.command.json`、`.resources.jsonl`，另有实际 runner 复制的 `plan.json` 和 `runner.json`。当前请求是每 route 256 次 × 3 windows；这两个值是显式实验输入，可以通过参数改变，不是性能阈值。

在此目录执行：

```bash
python3 -B prepare_phase_index.py \
  --measurements-root /workspace/scratch/4a65d70f0fe1/measurements \
  --output phases-index-01.json

python3 -B analyze_execution.py \
  --index phases-index-01.json \
  --korda-root /workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-continuation \
  --output phases-analysis-01.json
```

第二条命令还写出同名 `.md`。当前 host record 默认是 `measurements/host-before-phases.json`；同机身份比较使用记录里的 `/uname/node`、`/uname/machine`、`/uname/release`。这证明的是显式索引绑定的相同本地环境记录，没有声称独占物理宿主、可见 cgroup quota 或跨重启身份。其他环境可用 `--host-record` 和重复 `--host-pointer` 选择实际保存的稳定字段。不要把变化的 CPU 瞬时频率、时间戳或内存快照当身份字段。

`instrumented=false` 是索引对普通调用的显式声明；分析器同时检查实际 command argv、producer 的 timing flags 与 allocator profile。`--instrumented` 用于登记诊断数据。所有失败、缺失、仪器化或契约不符记录都保留，但不进入 Markdown 的 timing 表和比较比值；JSON 中即使能复算其计数，也明确标为诊断用途。环境变量和源/二进制来源仍应由冻结输入清单证明，不从文件名推断。

## 混合负载索引

分析器也接受同一个 index 的 `observations` 中追加 `kind="load"` 记录。示例（路径和 rate 按实际调用填写）：

```json
{
  "id": "postgresql-candidate-mixed-final-01",
  "kind": "load",
  "cohort": "candidate",
  "provider": "postgresql",
  "comparisonGroup": "mixed-final-01",
  "host": "recorded-local-linux-x64",
  "instrumented": false,
  "final": true,
  "receipt": "/absolute/completed-directory/candidate.json",
  "commandReceipt": "/absolute/completed-directory/candidate.command.json",
  "resources": "/absolute/completed-directory/candidate.resources.jsonl",
  "runnerReceipt": "/absolute/completed-directory/runner.json",
  "planReceipt": "/absolute/completed-directory/plan.json",
  "workloadManifest": "/absolute/frozen-source/benchmarks/db-perf/workload/queries-v3.json",
  "requested": {
    "seconds": 1800,
    "rate": 200,
    "concurrency": 4,
    "queueCapacity": 128,
    "rows": 32,
    "batchRows": 32
  }
}
```

示例中的 `200`、`4`、`128` 只是字段示范，不能代替校准或原始命令。闭环记录的 `requested.rate` 用 `null` 或省略；固定到达率必须填写实际请求。适配器根据真实 `OfferedLoad` 选择原 helper 的 offered 分支，再核对索引参数，避免旧 helper 在缺少 specification.rate 时错误地将有效 offered payload 当闭环拒绝。`final=false` 用于短测、校准和 baseline；当前四段最终记录才填 `final=true`。补测的同机 before 可以包含在同一索引中，但不被变成第五个最终格子。

## 保留的计算与边界

- Korda phase 直接调用被锁定工作树的 `query-phases/summarize.py`；Dapper phase 复用相同 quantiles 函数和窗口累计量定义。样本分位为 nearest-rank，不裁剪、不扣除空驱动、不选最好窗口。每 route 的各 window 分位、首次执行、准备、四阶段总和以及 read+release 的逐样本和都保存在 JSON。
- Phase 比较逐字核对 Korda `Sql`/`RawTemplate`。Dapper `Contract.KordaReceiptSha256` 必须对应索引中实际 Korda receipt 字节，并核对 executable hash、SQL、参数模板、provider 和行数。Dapper 输入 SQL 等于 RawTemplate；驱动参数重写后的线上 SQL 未被序列化，不冒称已抓到相同 wire bytes。
- Phase 的两个字段 DTO 与 mixed 的完整业务 DTO 不混用。Phase producer 每次检查全部 Id/Note/null 值，但 receipt 只保存行数与声明契约；分析器明确标注没有独立返回值 digest。Mixed 则复用 `analysis/raw_metrics.py` 的 sticky oracle、expected digest、逐 case 行数和全局计数一致性检查，比较 manifest 中的类型、参数、列、结果、物化方式与数据集。实际 `ActualDiagnosticSql` 的历史文本差异逐项保留，业务语义相等不代表 SQL 逐字相同。
- Mixed service、scheduled response、all-terminal response 和 start delay 分别重算原始 8192-bin histogram；分位保持原 helper 的 bucket upper 定义。start delay 包含生产者调度和队列等待，不代表独立 queue residence。Rejected 不获得虚构的完成延迟。offered 目标 rate、实际 attempted/producer elapsed、through-drain 成功吞吐分别输出。
- 托管 B/op 与 GC 都是整个进程的操作窗口累计量，包含业务结果和 harness。没有逐层分配归因，也不声明框架 0 B。RSS 保留 process-lifetime peak、实际 drain 后 idle 以及外部 JSONL 的完整样本峰值三个不同定义。没有 cgroup 时保留原始 server PID CPU 证据，不把非原子进程树差值伪装成完整服务端 CPU。
- SQL execution 和 protocol submission 是各自原始诊断计数；FFI 次数和物理协议等待没有在这些 receipts 中序列化，标为缺项，不推算 RTT。
- 所有最终记录检查 1800 秒请求、原始完整时长、0..1799 每秒成功业务进展、原始和 per-case/per-second/histogram 计数守恒以及全部 35 cases。四段的实际单调时钟和已记录 idle 区间必须同机不重叠。这个检查只覆盖本轮用户要求，不加载旧 eight-cell acceptance，也不据此授予环境或性能接受资格。

## 输入失败

输入缺失、异常退出、timeout、observer error、producer failure sidecar、重复 JSON key、非有限值、hash 不符、计数不守恒和有疑义的边界都会明确进入问题列表。原始文件不改写。`receipt + ".failure.json"` 自动发现；其他命名的失败记录可以通过 entry 的 `failureReceipts` 数组显式附加。

分析命令返回成功仅表示报告已生成；它不表示所有观察通过，也不表示任务可合并。分析期间输入变化时返回非零。缺失数据保持缺失，不能用历史记录或另一次更快结果无声替换。
