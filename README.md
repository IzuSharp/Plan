> **Current phase:** research and detailed design only; see [CURRENT-PHASE.md](CURRENT-PHASE.md). Research experiments and current evidence belong in NativeWeave-Design. No product write or A/B Delivery execution is authorized.

# NativeWeave Plan：并行研究、并行文档与候选实施图

## 当前输入与继续规则

启动PR #1已合并，不再从旧bootstrap分支重启。历史main：Design `baa953772d2a771bb4da3aff0cf4b4be6fc811a1`，Plan `da9e4a6337a5af0ec3d5e40a4695a2760d6ac5f5`。读取source-driven-baseline.json中的精确Design修订和当前Plan snapshot，分别记录design_commit/plan_commit；两个仓库不是原子更新，不能混用旧packet与新spec。

核对Task ID/revision/packet_sha256，从该snapshot建独立task/<ID>-<topic>分支。只补缺失研究，先读已提交report/evidence/follow-up；不要重复已有成果。技术决定、实现验证、生产接受分开。缺少真实subagent工具时不得模拟委派或独立Review。

NativeWeave独立于ArcForges，ArcForges只参考格式。C#是应用开发层，正式消费必须Native AOT。Database底层必须Rust，managed驱动只作源码/基准对照；Rust Server可选且需证据。优先源码驱动深度复用；普通新实体使用预编译native能力，不默认Cargo/CI。自然typed Fluent优先，不要求完整IQueryable/EF，不在C#重写SQL AST/方言。SG可选生成static metadata/DTO，不是唯一查询路径。Core只提供可组合ABI/lifetime/buffer/error/async，无巨型runtime。保留严格安全和生产验收，不授权大规模产品实现。

修订proposed；34R/32D/48Delivery保留，21契约仍未接受，产品未授权。R25/R27部分源码/实验进入follow-up；其他任务沿既有证据继续。

## 三张图的职责

| 图 | 回答的问题 | 初始节点 | 启动条件 | 接受条件 |
| --- | --- | --- | --- | --- |
| [research-graph.json](research-graph.json) | 谁查证什么实现、反例与成本 | R01–R34 | 独立问题可立即研究 | 固定源码、适当实验、异常路径及独立Review |
| [documentation-graph.json](documentation-graph.json) | 谁写哪些规范、契约及领域任务 | D01–D32 | 可带明确假设立即draft | 本领域必要证据和精确接口接受；外延专题不能成为普遍等待 |
| [delivery-graph.json](delivery-graph.json) | Codex未来实现什么、怎样验证 | A01–A24、B01–B24 | 本节点变为planned、被接受的精确契约和必要局部依赖 | 真实平台证据、哈希绑定、独立Review、选定发布组合 |

`start_dependencies`约束开始；`acceptance_dependencies`约束最后接受。`research_refs`和`documentation_refs`提供追溯，不自动制造等待。`contract_inputs`总是精确版本，并显式要求accepted。`conditional_dependencies`只在路线selected时按gate=start/acceptance约束局部开始或接受。B15/B17均是未选择的产品host；相关`required_selection_groups`要求所有选择已决定且至少一个host selected，允许两个都选而不指定默认。Kestrel研究对照不自动成为产品选择。

## 立即开始

1. 按[任务索引](task-index.md)选择相互独立的研究或文档任务，复制该文件到新GPT-6 Pro窗口。窗口不需继承聊天历史。
2. 每个窗口只写自己的`write_scopes`。研究报告进入正式Design仓库的`docs/research/topics/Rxx/`；文档作者分别写独占规范文件或Plan fragment。
3. 独立分支/Draft PR提交实际证据或草案。整合者按[文档政策](documentation-policy.md)合并fragment、更新索引和三图；不要求全部研究结束才开始写文档。
4. 用下面的校验命令核验图与局部证据，独立审查者再检查内容真实性。任何校验错误使工具返回的可执行ready集合为空。

```bash
python3 tools/validate_graphs.py --root . --output verification/graph-validation.json
python3 tools/mutation_checks.py
python3 tools/host_selection_checks.py
```

Windows可使用`py -3`代替`python3`。两仓库本地位置应为同级`Plan/`和`NativeWeave-Design/`；第三个`NativeWeave/`只在正式实施/证据需要时存在。独立检出时使用受控同级目录，不把另一个仓库的内容复制成新权威。

当前实际结果见[graph-validation.json](verification/graph-validation.json)、[mutation-checks.json](verification/mutation-checks.json)及[host-selection-checks.json](verification/host-selection-checks.json)。这些只验证图和证据门禁工具，**不是NativeWeave产品的Windows/Linux或AOT验收**。

## 两阶段范围

阶段A覆盖C ABI/布局/版本、导入导出、生成器与分析器、句柄/所有权、callback/async/cancel、buffer/error/runtime、Cargo/MSBuild、Windows/Linux AOT、打包/来源/兼容、两类真实engine和接入脚手架。

阶段B完整分解数据库驱动、池/事务/未知commit、codec/批量/stream/migration、薄绑定metadata/可选static生成/Rust builder与binder/static DTO/runtime Fluent/显式关系、Kestrel/可选Rust server、gRPC/MCP/诊断以及参考应用/故障/基准/领域发布。未来GUI/GPU/iOS/Android保留专项研究和接入验证，不在本轮实施完整GUI。

## 重要索引

- [执行与并行政策](execution-policy.md)、[研究政策](research-policy.md)、[文档政策](documentation-policy.md)。
- [milestones.md](milestones.md)：里程碑按能力与真实依赖定义，不构成全局串行锁。
- [acceptance-register.md](acceptance-register.md)：已验证、未验证和候选状态的区别。
- Design侧28条需求映射见`NativeWeave-Design:docs/traceability/requirements-map.json`，与114个节点ID保持追溯。
- [schemas/graph-v1.schema.json](schemas/graph-v1.schema.json)、[schemas/evidence-manifest-v1.schema.json](schemas/evidence-manifest-v1.schema.json)。
- [verification/validator-contract.md](verification/validator-contract.md)：接受证据、内容hash、身份边界与工具限制。
- [prompts/independent-review.md](prompts/independent-review.md)：独立交叉审查入口。

## 没有被声称完成的事项

研究任务尚未全部执行；Design契约仍待逐专题证据和独立审查；产品任务仍是候选；没有把仅运行Python脚本、源码阅读或有限模型的结果标记为产品AOT测试。没有自动发布任何包、合并产品代码或更改许可证/权限。


## Source-driven amendment (2026-11-12)

NativeWeave独立于ArcForges，ArcForges只参考格式。C#是应用开发层，正式消费必须Native AOT。Database底层必须Rust，managed驱动只作源码/基准对照；Rust Server可选且需证据。优先源码驱动深度复用；普通新实体使用预编译native能力，不默认Cargo/CI。自然typed Fluent优先，不要求完整IQueryable/EF，不在C#重写SQL AST/方言。SG可选生成static metadata/DTO，不是唯一查询路径。Core只提供可组合ABI/lifetime/buffer/error/async，无巨型runtime。保留严格安全和生产验收，不授权大规模产品实现。

读取source-driven-baseline.json、同ID新packet和Design ADR-0002。独立Review检查新hash、backend拒绝、fallible binder、无逐实体Cargo、Server body/retirement、三图和未完成验证。旧Review不接受新内容；不增加规划层。


## 2026-11-12 Rust1.100连续执行授权

Rust/Cargo1.100研究与真实两OS测试见Design R01；这是固定研究基线，升级工具链另需当时的真实证据。Design PR5/Plan PR2的历史self-review合并例外不绕过GitHub门禁或伪造accepted契约。当前按CURRENT-PHASE.md仅推进已有R/D的源码、Design内实验和详细设计；所有Delivery保持候选，未获正式产品实施授权。普通已授权研究不逐项询问。

## 生命周期研究输入与候选任务细化

本轮在原114个ID内细化A03/A07、B05、B11/B13及Server任务的API边界、状态/owner、失败路径和可执行oracle，保持全部status、acceptance/review记录和产品实施授权状态。C-TX/C-SERVER精确消费0.2.1-draft，C-LIFETIME仍0.1.0-draft并绑定PR8的新增同步准入证据。输入与证据边界见[source-driven-baseline.json](source-driven-baseline.json)及其source-lifecycle checkpoint。

本次增量的实际基线是已合并Plan PR6 `886fec7e6c702372e3b5f8dee2c85f039844b462`。PR6的R07/D04证据、六个packet增量和独立checkpoint均保留；D04的partially_evidenced状态继承自该主线，不是本次提升或回退。相对该基线，本批53个packet修订、61个原样；当前Research为10 partial/24 planned，Documentation为4 partial/28 draft_ready，Delivery仍48个planned_candidate，接受的契约为0。

历史迁移checkpoint保持原字节；`tools/verify_research_assets.py`在已合并Plan 04c2快照验证33/81个packet和当时Delivery未变，同时单独验证当前pair与114个packet。不能把合法后续任务修订伪装成迁移时的33个修改，也不能把旧raw logs记作新的实验执行。

`tools/verify_logical_admission_history.py`另按Plan 886fec7 / Design 3767f3c的固定历史核验6/108个packet、64份既有raw files和当时Delivery未变。原record脚本、历史检查记录与checkpoint原字节保留；当前CI不再用该一次性脚本的“只有六个packet变化”断言约束后续合法研究修订。

## Detailed logical-admission research input

See [future Codex acceptance supplement](verification/logical-admission-obligations.md) for existing A03/A20/A06/A07/B11/B16/B17/B20 steps and missing verification, based on executed R07/D04 research. This is planning detail, not permission to implement product code. The current Design pin and historical migration pin remain separate in `source-driven-baseline.json`.
