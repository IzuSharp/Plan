# NativeWeave Plan — 现有研究、规范与未来实施图

当前处于研究、详细设计和未来 Codex 开发规划阶段；**NativeWeave 产品仓库不写入，A/B Delivery 不执行**。恢复入口是 [source-driven-baseline.json](source-driven-baseline.json)，实际状态以现有三图、精确证据和审查为准。

**本轮最终接受：34 Research / 32 Documentation / 21 技术契约全部 accepted。** Design PR #10 已合并为 `08e3aaee73aad174620dcff18ed21b3b14c5e632`；66 项任务绑定固定 Plan 输入 `c3947b378e0a251f8dfeaf7fd7d4acc636631974`、该 Design Commit、实际独立报告与对应执行者的精确确认。[接受索引](ledger/completion-acceptance.json)、[最终检查点](ledger/checkpoints/rd-acceptance-2026-11-13.json)及[完整校验结果](verification/completion.json)提供可复核记录。48 项 Delivery 的说明已完成审查，产品实施与产品验收均未开始。

NativeWeave 采用 Source-Driven Deep Native Integration。C# 是应用开发语言，提供强类型 Fluent、静态元数据/DTO 和业务 Handler；数据库驱动、查询/方言/ORM 关系执行及 Server 网络/协议/运行时必须复用成熟 Rust 引擎。Kestrel、Npgsql 等只作对照。普通应用不手写 Rust/FFI，不因新增 Entity/DTO/Handler 重编译 native。保持正常 dotnet build/run 与真实 Native AOT 发布，不构造 C# SQL AST/完整 LINQ Provider 或巨型 Core runtime。

## 三图与职责

| 图 | 既有范围 | 当前完成要求 |
| --- | --- | --- |
| research-graph.json | R01–R34，34项 | 真实固定源码、适当实验、正常/异常/边界结论与独立技术审查 |
| documentation-graph.json | D01–D32，32项 | 21规范、10实施细化fragment、1最终审查，足以指导实现 |
| delivery-graph.json | A01–A24 / B01–B24，48项 | 本次只完善接口、步骤、所有权、局部依赖、并行与验收；实施未授权 |

[114份独立说明](task-index.md)各有0.3.0 revision和packet hash。`fragments/`细化已有Delivery，不是第四张任务图。`start_dependencies`限制开始，`acceptance_dependencies`限制最后接受；研究/规范引用只提供追溯，不自动形成等待。契约是精确版本与内容hash；研究、设计接受和产品验证分别登记。

## 确定的职责分工

Database 主路径是维护者预编译 SeaQuery+SQLx 与动态业务元数据。SeaORM 的成熟动态投影/静态关系能力按源码边界复用；可选专用静态Entity包不能成为普通实体前置。B01独占共享Data接口，B07独占fallible codec，B09只定义查询操作绑定，B11负责原生查询与方言，B12负责C# DTO物化，B13负责自然强类型Fluent，B14负责原生显式关系。

B15 是 **C# Server.Application / Handler 界面**，B17 是 **必需 Rust Server Host**，二者互补。B16提供Body/Bytes与预算组件，B17复用Tokio/Hyper/Tower/Axum的实际引擎能力；B18的Tonic和B19的rmcp可由应用独立选用，但都只使用B17的Rust Host。旧Kestrel/Rust二选一组已经退役，不是未决定的产品架构。

## 工作方式

先核验GitHub实际HEAD及baseline配对，读对应packet和Design规范。完整成果只复核，不重复成功实验。一个任务一个独立Worktree，只改自己的scope；根solution/Cargo workspace由A13整合小补丁，不能形成全局worker锁。异步/数据库/服务器各有可独立测试的局部组件及最终组合验收，不让未来参考应用成为所有组件接受的循环前置。

```bash
python3 tools/validate_graphs.py --root . --output verification/graph-validation.json
python3 tools/mutation_checks.py
python3 tools/host_selection_checks.py
python3 tools/verify_completion.py
python3 tools/verify_completion.py --require-complete
```

两仓库应为同级`Plan/`和`NativeWeave-Design/`。当前证明工具检查结构、hash和门禁；它不能认证真实人员身份或把研究实验转成产品运行。历史冻结验证对原始Commit执行，当前接受验证对本轮确切输入执行，二者不能混淆。

先检出 baseline 指定的完整 Design SHA。`--require-complete` 要求 34R / 32D / 21 契约全部接受，并验证 840 个输入条目、114 份说明、10 个 fragment 和真实独立绑定；不会执行原生实验或启动 Delivery。

## 继续与实现入口

精确进度和独立审查见 [D32](ledger/reviews/D32.md)、[当前阶段](CURRENT-PHASE.md)、[接受登记](acceptance-register.md)。未来明确授权产品阶段后，先可并行实施A01、A19、A21和B01；其余按实际局部依赖推进。实现阶段仍需独立NuGet/clean no-Rust消费、Windows/Linux实际AOT、真实数据库/网络、错误/取消/资源与长期负载/性能验证。

源码选择不依赖ArcForges业务或架构。研究合并不自动发布包、不改变权限/许可证、不绕过Required Checks。独立子代理技术审查不是另一个GitHub账号的审批。
