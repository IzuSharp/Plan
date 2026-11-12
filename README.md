# NativeWeave Plan：并行研究、并行文档与候选实施图

## 首次启动输入定位

本次启动包位于以下研究分支与 Draft PR，不能假定默认分支已经包含这些文件：

- Design：[research/bootstrap-2026-11-12 分支](https://github.com/IzuSharp/NativeWeave-Design/tree/research/bootstrap-2026-11-12)；[Draft PR #1](https://github.com/IzuSharp/NativeWeave-Design/pull/1)。
- Plan：[research/bootstrap-2026-11-12 分支](https://github.com/IzuSharp/Plan/tree/research/bootstrap-2026-11-12)；[Draft PR #1](https://github.com/IzuSharp/Plan/pull/1)。

开始时分别解析两仓库该分支的**当前完整 commit SHA**，记录 `design_commit` 和 `plan_commit`，随后从这两个固定快照读取输入；仓库分支与 PR 只是导航入口，不能充当不可变源码证据。两个仓库的 SHA 各自记录，不能假定它们相同或原子更新；若跨仓库引用不一致，记录具体缺口并局部协调。

在固定的 Plan 快照中读取本任务对应图节点和提示词/packet，核对 Task ID、`revision` 和正文实际字节的 `packet_sha256`；不匹配时先定位正确版本，不得直接改 hash 掩盖不一致。记录选用的任务版本及 hash。需要写入哪个仓库，就从其已记录的对应快照创建独立 `task/<ID>-<short-topic>` 分支，再按本任务的文件范围工作；不要从仅含初始化文件的默认分支开始，也不要将不同快照的契约与任务混用。

产品仓库 https://github.com/IzuSharp/NativeWeave 本轮**不假定已有产品实现**。研究原型、规范草案和候选开发任务仍遵循下文的实际状态，不因找到发布入口而升级为已完成或已授权产品实施。

本批114份任务提示词/packet统一修订为0.1.1，任务状态及契约版本保持原状。

状态：**首次交付草案，2026-11-12**。本仓库中的计划从用户本次NativeWeave目标独立制定。ArcForges Design/Plan只参考文档格式与组织，内容、规则和验收政策不是本计划依据。

这是实质性的研究启动包：34个研究专题、32个独立文档编制任务，以及阶段A 24项和阶段B 24项候选实施任务。每项都附可独立复制到新窗口的说明、具体问题/接口、文件范围和验收方法。**候选实施任务不是已经研究完成或已授权开工的产品计划。** 当前21个契约均为proposed，所有产品delivery均被明确阻塞；研究及文档draft可并行开始。

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

阶段B完整分解数据库驱动、池/事务/未知commit、codec/批量/stream/migration、查询IR/LINQ捕获/SQL方言/static mapper/动态安全API/关系、Kestrel/可选Rust server、gRPC/MCP/诊断以及参考应用/故障/基准/领域发布。未来GUI/GPU/iOS/Android保留专项研究和接入验证，不在本轮实施完整GUI。

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
