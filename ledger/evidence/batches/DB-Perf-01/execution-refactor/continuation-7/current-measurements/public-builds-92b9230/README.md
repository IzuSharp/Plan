# Exact 92b9230 public-build closure

**92b9230 正确性与产物身份核验通过，但事前规则下的 paired 性能选择已拒绝它。正式候选保持公开 17da，PR #37 不改变。** 本记录绑定 commit `92b923075952bac347619ee7817c372ee6e415cb`、tree `f22333b98bf80fc539d819d642a9c692d2af7002`，只保留该隔离候选的正确性与身份凭据。此前 0aa 从未进入计时，不赋予它任何性能信用。

主线程按已在测量前提交的 `9d1d072` 规则选择，原 selection 为 `/workspace/scratch/fd78534029f7/measurements/close-paired-selection-01.json`，原算术报告是 `close-paired-analysis-r1`、`close-paired-analysis-r2`（没有 `.json` 后缀）。36/36 observations 可用于这次普通短对照，结果契约及八项 owner 通过；但 PostgreSQL 第 1 轮 prepared 单行 ReadComplete p50 从 34.972 增至 50.580 µs，不满足每库每轮至少改善 10%；SQLite 1000 行两轮合并的 prepared 每操作总时长 p50 从 1755.582 增至 1874.589 µs，+6.7788%，超过预先 5% 回退上限。两项已足以拒绝，没有改阈值、挑最好窗口或新增重试。

## 独立选择重算

[audit_close_selection.py](audit_close_selection.py) 于 `2026-11-26T08:05:46.679771Z` 完成一次有限离线复算，exit 0、进程耗时 0.42 秒；结果见 [close-selection-independent-01.json](close-selection-independent-01.json)，SHA-256 `d904454126c8033a897c167dee866dd86a582f6b069b1339f159bfaa714321f4`。脚本 SHA-256 为 `8b0f96b43d26501f1eba95ffce0d91ff4985c39e3d6664d9aa2b62d833e362ea`。它读取两份算术报告和 24 份 before/candidate 原样本 JSON，先后核验所有输入哈希不变，逐项核对真实 package commit、八项 owner 归零和结果行数。以有理数将原 tick 转成微秒，先逐样本相加四个阶段，再独立取 nearest-rank p50/p95/p99；每轮 768 个 prepared 样本、两轮合并 1536 个样本的统计均与原选择文件一致。未把各阶段百分位相加，也未合并不同 route。

完整事前提交是 `9d1d0726f1048d9b1903b624d5549b860f142238`，提交时间为 `2026-11-26T07:51:35Z`，先于最早测量 `2026-11-26T07:53:22.802910Z`。独立结论同为 `selected=false`、`selectedCommit=17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`。没有执行产品、数据库、测试、负载或二进制哈希扫描；本次普通短对照不获得最终四段的信用。`0aa` 未计时是主线程接续记录，此复算仅独立证实本次 pair 的输入中没有该版本，不倒推其他历史目录。

可复算入口（输出必须是尚不存在的新文件）：

```bash
python3 ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/current-measurements/public-builds-92b9230/audit_close_selection.py \
  --measurements /workspace/scratch/fd78534029f7/measurements \
  --plan-repository /workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-plan \
  --output /tmp/DB-Exec-10-close-selection-independent-next.json
```

## 已完成的产物闭合

完整记录为 [completed-public-builds-92b9230-02.json](completed-public-builds-92b9230-02.json)，SHA-256 `5b8f060fe588d09e478f19b07b89b25199aa08acbb694bda5fae184f4c2f0385`。采用与 17da 审查相同的既有 helper：`audit_final_identity.py` SHA `99f45803…`、`analyze_command_single_v2.py` SHA `0cec15c4…`；完整 helper 哈希及路径在 JSON 内。没有改动冻结工具。

## 实际复核

- 两个全新 producer worktree 都是准确 92b9230/tree f22333、tracked source 干净；每库 120 项原生输入哈希一致，compiler/installed/output 三处 native 字节一致。
- 八阶段必须按顺序存在且全部 exit 0、sourceUnchanged=true；逐一重哈希阶段日志与准确构建器。阶段是 impact、native、native-correctness、bundle、public-consume-aot、public-validate、consumer-query-phases、consumer-workload。
- 每库只产生一个独立顶层 nupkg，NuGet dependencies 为空；source/tree、release/nuspec、完整 unsigned 成员清单和成员字节全部闭合。SQLite 40 个成员，PostgreSQL 41 个成员。
- 包内 native 与实际 phase/workload 输出 native 完全相同；外部消费者直接引用准确公开包，没有 ProjectReference，命令为 Release Native AOT / linux-x64。
- workload 的全部复制源、项目、SQL/manifest、资产图、日志、ELF 和每库 65 个生成源已核验；phase 的 Program.cs、项目、目录属性、配置、资产图、日志、ELF 和每库 25 个实际生成源已核验。
- 两份实际 impact 的 SHA 均为 `b91a21002302197441b7a640e06fa7491484f1ab008889959a1d47b5b23c1f3e`，与各 build receipt 对应。这里没有重跑检查或构建。
- 审计进程耗时 0.70 秒、exit 0，结束后立即通知主线程可以开始 paired 短测。没有启动构建、数据库、测试、消费者或性能负载。

| 身份 | SQLite | PostgreSQL |
| --- | --- | --- |
| build-receipt.json SHA-256 | `bdcd22add24e7b657592ce55904382091f4ce3d179056345d0b2066d055dd95d` | `f8366e3d6acd27107bc44afb9f844904f6eb2df64be03ad7cfca232a688bffd9` |
| nupkg SHA-256 | `6c7fcc5a4f03998dc2f893b7223e5ff325fe05c49e393194417de68639f0b731` | `ca71944f47805d239401667b7d4dd6fd209a6a2923f9814f1414e18e5b4fb295` |
| native ELF SHA-256 | `05e9c972cac6b3d9897208b34bedbf74a7d4f67fbfd37b4c35781b6170767b14` | `14a7b18ae0f960b122f9fd9b50e39d9fbf4a416621d010b21a86c39aa0172e61` |
| query-phases ELF SHA-256 | `cba6d7a559e4a2642629c0c077eeaacc3417132d15bcee7d070866dac74ce5e3` | `4b50ce8c406e5de5c46fa194c63902070501f6b00a17c8b1dfdc81cf2f70b1c6` |
| workload ELF SHA-256 | `f12773b4de9d6e8187306d5275e6c1dfbc435e58bf533439d370e6df52a49276` | `2d3b769353c28b8c662328a9976e17e2a14935c8129244ef0fd36dcec18959f6` |

## 原件与清理边界

[receipts/](receipts/) 原样保存 28 个小回执、计划、native/release manifest 和全部八阶段日志，共 523226 B。完整 JSON 的 `retainedSmallFiles` 列出原路径、复制路径、字节数和 SHA。未复制大包、ELF 或整个消费者目录；这些保持原实际路径，不能声称本目录单独包含可直接重跑的全部二进制。

本次 consumer 证明使用根 `project.assets.json`、根源/项目/配置、`generated/`、`out/`、`packages/`、build receipt 和 publish.log，不绑定 consumer 的 `bin/` 或 `obj/`。原生 producer 的编译、安装输出仍由 native manifest 绑定，不能把它们混同为消费者中间目录。

另一个既有 17da allocation 审计确实绑定两份 `candidate-{provider}-02/consumer-query-phases/obj/project.assets.json`，清理前已经明确通知主线程保留这些原路径。主线程随后只清理消费者 bin，未动 obj；本次没有执行任何清理。

## 后续最终证据

见 [final-review-notes.md](final-review-notes.md)。这些是对既有冻结/分析工具的只读审查要点，不是新门、性能阈值或新的负载入口。17da 的通过结果、旧分配结果与本次 92b9230 产物保持各自身份；不互相赋予后续候选的测量或 CI 信用。
