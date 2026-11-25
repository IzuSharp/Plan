# DB-Perf-01 数字证据提取方法（待最终测量输入）

此目录仅包含本地归档工具与验证产物。它不修改 Plan/Design/product，不启动 consumer、构建或测试负载，不授予性能验收。最终输入预期来自 `/tmp/DB-Perf-01-measurements-v4`，资源诊断来自 `/workspace/scratch/787156d4dd76/DB-Perf-01-resource-results-v4`。由 root 在输入冻结后选择归档并发布。

## 允许进入公开证据的内容

`extract.py` 对键和类型逐项选取；不使用递归“全部数字都复制”的通用过滤器。允许的内容包括：

- 每份原始 JSON/JSONL 的 SHA-256 与字节数，提取工具自身 SHA，公开 producer commit/tree/PR head/workflow run；每个 consumer 的 ELF 类型、架构、可执行文件 SHA、nupkg ID/版本/SHA、native image SHA，以及 SDK 版本。完整 build/source/restore 集合只保留原始冻结文件 SHA；不复制其内容。Dapper SQLite 的外部 libsqlite3 仅选取冻结记录中准确的 `dapper-sqlite-native` 角色。
- Phase schema 2 的全部原始数字 samples，首次三路的固定顺序、每个 window 的构造/首行/读完/释放 ticks、分配起止值、GC 次数、CPU 起止值、原生计数、实际 100 行结果数。SQL/模板/语义说明只保留内容指纹。Stopwatch ticks 使用原 receipt 的频率；`CpuBeforeTicks/CpuAfterTicks` 为 .NET TimeSpan ticks，固定每秒 10,000,000。
- Korda 与 Dapper 的 closed-loop mixed schema 1：完整 8192 项直方图、每秒 Completed/Rows/Failed、每 case 成败/行数、sticky oracle 计数、分配起止/总量、GC 次数、CPU 起止/总量、RSS/PSS/peak、owner/application-connection 计数、实际版本。所有原始计数保留，包括失败；`Completed` 在这两个 managed producer 中指成功次数。
- Resource probe 的命名窗口、分配及 GC 起止值、首次/稳态/concurrency/pool-pressure 数字、显式 forced-GC 的内存观察、owner settlement、取消与资源上限结果数。预期的 pool-exhaustion 失败保留为失败计数，不改为成功操作。这些是分开的资源诊断，不是 30 分钟 mixed 段，也没有证明 whole-framework 零分配。
- Observer 的退出码、timeout/success、单调时钟、wait4 生命周期 CPU/peak、PID/startTicks 身份；资源 JSONL 中每次 acquisition 的时间边界、进程树计数、RSS/PSS、host CPU ticks 与已知数值 quota 字段。原始 stdout/server-owner 等只保留 SHA/字节数，不复制日志正文。

不进入输出：源码、生成文件、restore 图、环境、命令 argv、连接串、数据库路径、native 路径、SQL 正文、任意异常 Message/Data/StackTrace 正文。诊断文本以数量、位置和 SHA 指纹保留；公开结构化 Provider kind、SQLSTATE、HResult、CorrelationId、IsTransient 则允许保留。异常文本是有损变换，无法仅凭数字包重现文本或重新判断未解释错误原因。原始文件完整保留在本地。

未知字段不会透传；提取后记录未知字段名集合的 SHA/数量并令 schema 校验失败。当前 `OfferedLoad` 或 `NativeAllocationProfile` 非 null 会保留存在性指纹并使校验失败，要求单独审查新 schema；不会把 offered-load 数据误按 closed-loop 解释。当前 v4 计划使用 closed-loop。

## 能独立重新计算什么

吞吐为 `Completed / EffectiveSeconds`；错误率为 `Failed / Started`。每 case、每秒计数必须与总数守恒，Started 必须等于 Completed + Failed。分配总量必须等于 `AllocatedAfter - AllocatedBefore`，B/op 以成功次数为分母。CPU 使用同一进程的 user/system 起止差。GC 保留各 generation 的实际 delta；phase/resource 还保留相应边界。工具同时核对成功 latency 直方图总数、逐秒连续性、分配及 CPU 恒等式，校验失败也保留来源 SHA 和条目状态。

直方图 p99 是成功操作的上界估计。令 `N=sum(bins)`，rank 为 `ceil(99*N/100)`，找到累计计数首次达到 rank 的 bin `i`；其上界微秒为：

```text
2^(i // 128) * (129 + i % 128) / 128000
```

相同公式用于 p50/p95，N=0 时分位数不可定义。该公式与仓库现有 `analysis/raw_metrics.py` 一致。合并独立进程时应先合并 bins 再重算 pooled p99；不要平均 p99。成功 service-time p99 不能转换成外部到达率下排队延迟。Phase 每条操作可由四段原始 ticks 相加再求经验分位数；其构造、首行、读完、释放分别可重新分析。

内存资源统计仅选完整 acquisition 区间位于对应稳态起止时间内的 samples，不外推边界。保留全部 samples 以便改变分析窗口时重算。进程树快照是非原子的；server child/reaped ticks 不是可靠的每 cell PostgreSQL CPU 差，且原 observer 未序列化远端 SC_CLK_TCK。没有 task-owned cumulative CPU group 证明时，不把这些 ticks 换算成声称准确的 server CPU。wait4 的 server owner 生命周期也不能分摊成某个 cell 的 CPU。全进程 allocation/RSS 不等于框架独占分配/native malloc 计数。

## 失败、缺失与历史边界

`make_manifest.py` 按已冻结的六份 phase/short/long plan 枚举全部 commands，包括 setup；不从“成功结果文件”反推清单。资源诊断另外枚举 before/candidate × 两库 × 三进程。没有 observer/result 的项记为 `not_observed`；这只表示归档时未观察到，不能擅自解释为已运行、已失败或已通过。非零退出码记为 `process_failed`，timeout 单独标识。成功 observer 缺少有效 result 会使连续性校验失败。失败无 result 仍保留 observer、resource、stdout SHA，若有新的 phase failure sidecar 则提取其有界结构化字段。

原 PG 故障单独通过 `failureReview` 保存，输入为已审查的：

- `review.json`，SHA `ecaf8812d1e5a08f197914c2264e563ebc8c1aa438634d81463414b059467452`。
- 同目录 `review.md`，SHA `9de8283e140cbe031affad0f468315e594806d9a0e944f99ce0f62bed1f32a3d`，可作为 digest-only 引用。

原 `r1-recovered` prepared 路径异常退出 -6、没有成功结果，原因仍未解释，也未宣称修复。3 次有界诊断未复现，不能替换原失败或证明修复。另 1 次故意缺表只验证 AOT handler 实际输出 Provider / 42P01（first/fluent）、consumer -6/runner 1；它不是原失败复现或成功比较 cell。其实际执行 ELF 不包含随后独立 stderr guard commit；原 receipt 中的这个身份边界保留。数字包不改变旧 acceptance、历史数据或 rejected spin 记录。

## 最终冻结后的调用

以下命令只读取文件并写新提取目录，不执行测量：

```bash
python3 /tmp/DB-Perf-01-evidence-tools/make_manifest.py \
  --campaign /tmp/DB-Perf-01-measurements-v4 \
  --resource-root /workspace/scratch/787156d4dd76/DB-Perf-01-resource-results-v4 \
  --failure-review /tmp/DB-Perf-01-phase-diagnostic-recovered-pg/review.json \
  --output /tmp/DB-Perf-01-evidence-tools/v4-input-manifest.json

python3 /tmp/DB-Perf-01-evidence-tools/extract.py \
  --manifest /tmp/DB-Perf-01-evidence-tools/v4-input-manifest.json \
  --output /tmp/DB-Perf-01-evidence-v4-numeric
```

两步都拒绝覆盖已有输出，便于保持候选和失败记录不变。manifest 含本地路径，仅供本地驱动，**不发布 manifest**。发布候选仅为 numeric 输出目录中 index 明确列出的文件、index、工具和本说明；不归档本目录其他验证过程文件，也不打包 campaign/source/build 根目录。原始 SHA 不等于原始文件已公开可下载，报告应如实说明原始输入仍在本地。

`index.numericAndSchemaChecksPassed` 只表示这份提取的类型/数值守恒通过。未观察到的项和观察到的真实失败可以是有效归档记录。所有输出的 `performanceAcceptance` 始终为 false；它不代替常规 CI、真实长段的执行完备性、样本准入、错误 SLO 或最终停止依据。最终 four-cell candidate/Dapper × PostgreSQL/SQLite 的 30 分钟证据仍必须逐项检查真实结束状态与时长，不能因工具运行成功而记为完成。

## 工具验证范围

`validate.py` 读取既有 SQLite r0 的三份 phase、Korda/Dapper correctness、既有资源诊断、原 PG 失败与未观察到项。它比较逐 sample/全 histogram/秒桶保持性，并用仓库 `raw_metrics.histogram()` 独立核对 p50/p95/p99。负向输入仅在内存中篡改直方图、分配和秒桶，验证能被检出；canary 验证任意文本、路径和未知字段不会透传。校验不启动任何产品进程，不是新的性能证据。实际验证结果与脚本/输入 index SHA 保存在 `validation-report*.json`。
