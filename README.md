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

`start_dependencies`约束开始；`acceptance_dependencies`约束最后接受。`research_refs`和`documentation_refs`提供追溯，不自动制造等待。`contract_inputs`总是精确版本，并显式要求accepted。`conditional_dependencies`只在可选路线被选中时进入本地验收，避免“所有人等待整个阶段A”。

## 立即开始

1. 按[任务索引](task-index.md)选择相互独立的研究或文档任务，复制该文件到新GPT-6 Pro窗口。窗口不需继承聊天历史。
2. 每个窗口只写自己的`write_scopes`。研究报告进入正式Design仓库的`docs/research/topics/Rxx/`；文档作者分别写独占规范文件或Plan fragment。
3. 独立分支/Draft PR提交实际证据或草案。整合者按[文档政策](documentation-policy.md)合并fragment、更新索引和三图；不要求全部研究结束才开始写文档。
4. 用下面的校验命令核验图与局部证据，独立审查者再检查内容真实性。任何校验错误使工具返回的可执行ready集合为空。

```bash
python3 tools/validate_graphs.py --root . --output verification/graph-validation.json
python3 tools/mutation_checks.py
```

Windows可使用`py -3`代替`python3`。两仓库本地位置应为同级`Plan/`和`NativeWeave-Design/`；第三个`NativeWeave/`只在正式实施/证据需要时存在。独立检出时使用受控同级目录，不把另一个仓库的内容复制成新权威。

当前实际结果见[graph-validation.json](verification/graph-validation.json)及[mutation-checks.json](verification/mutation-checks.json)。这些只验证图和证据门禁工具，**不是NativeWeave产品的Windows/Linux或AOT验收**。

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

当前稳定Rust/Cargo1.100研究与真实两OS测试见Design R01。Design PR5/Plan PR2可按用户明确例外经严格self-review和真实检查合并，独立审查未完成必须保留D32复审；不绕过GitHub门禁或伪造accepted契约。普通技术任务不再逐个询问。按图ready/continuable实际执行；没有accepted前置的Delivery保持候选，先执行已有R/D的真实源码/编译fixture。旧“仅规划、当前全面不授权执行”指的是历史启动轮，不覆盖此次授权。
