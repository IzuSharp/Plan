# Codex并行执行政策 v0.1（proposed）

本政策管理研究、文档并行执行和未来Codex实施的技术规则。当前用户阶段边界见[CURRENT-PHASE.md](CURRENT-PHASE.md)：允许深入研究、详细设计及Design内真实实验，**当前不授权正式产品实施**，普通技术任务不需要逐步询问。全部48个Delivery节点仍为`planned_candidate`。未来进入产品实施阶段后，才按实际契约与依赖细化接口、更新packet/hash和明确范围；研究原型通过不能代替阶段授权或正式验收。

## 工作单元与文件所有权

一个任务一个稳定ID、一个主要owner、一个隔离worktree/目录、一个独立PR。允许多个Windows/Linux会话同时工作。可修改范围以`write_scopes`为准；目录范围是下属文件，文件范围仅该文件；不能声称拥有父目录。禁止在其他模块里复制公共契约来绕过依赖。

worker提交自己的模块和测试、证据目录。根solution、集中Cargo workspace、共享registry/图和版本索引由整合者处理小范围change-request；领域worker不同时改这些文件。这是明确文件责任，不是所有任务轮流执行。

同一任务被重复领取时在合并前解决ownership，不让两个作者无标记写同一scope。基准机器、端口、共享数据库和真机可以使用限定资源租约，租约只约束正在占用资源的验证；普通研究、文档、编译不受全局锁限制。

## 真正的依赖

`start_dependencies`只包含当前packet需要的实际实现产物。契约输入是精确ID+版本+accepted；可在依赖实现未完成前写mock的情形须另建明确的契约/fixture任务，不能把mock测试当集成验收。研究和文档接受依赖与产品编译依赖不是同一张表。

Database底层必需Rust；不存在产品纯C#Data/Query fallback。Kestrel、独立研究/fixture和无数据库应用不等待全部Interop实现。正式native产品功能只依赖所需accepted契约/实现，不制造全局等待，也不把研究探针当阶段A生产验收。

## 可选路线及发布范围

B04是必需Rust Database Host，B02/B03是Rust providers。B17原生Server、B18 gRPC、B19 MCP才是独立可选路线。选择状态进入对应B21–B24验收快照；新增组合必须复验，不能复用旧组合报告。

B24包含精确revision的release_scope。总accepted只能描述scope内已验收组件，不能外推到未选择协议包、架构或平台。每个engine/crate/adapter独立版本发布；新engine增加独立task/fragment，不重排无关任务。

## Windows、Linux与Native AOT

初始正式目标候选为win-x64和linux-x64。任务证据按OS+arch+RID匹配；win-arm64不能代替win-x64。A14只负责Linux包、A15只负责Windows包，组合任务汇总两侧。A19模型本身提供模型工具验证，不伪称模型是AOT应用；公共运行时能力仍必须通过真实消费端AOT验证。

每次运行保留工具链、目标、源码/制品hash、命令、stdout/stderr、起止时间、checks和失败/超时。AOT同时要求publish与目标二进制实际执行，记录执行制品hash。工具不可用时blocked，不用JIT测试替代。

## 完成、审查与失败

accepted/complete/delivered等终结态均使用相同严格证据门禁。源码与packet/spec hash匹配；独立Review绑定当前内容和证据；依赖版本匹配；无blocking发现。身份不独立、manifest只是模板、测试失败/超时、AOT未执行、目标RID不符都会拒绝。

部分交付记partially_verified；失败记failed并保留可复放seed/日志。修复后只复验实际影响范围与required gate，不能通过删失败证据、全局抑制警告或修改验收值冒充通过。发布包/合并/权限变更遵从任务与用户已有授权；本研究启动包不会执行产品发布。


## Source-driven amendment (2026-11-12)

NativeWeave独立于ArcForges，ArcForges只参考格式。C#是应用开发层，正式消费必须Native AOT。Database底层必须Rust，managed驱动只作源码/基准对照；Rust Server可选且需证据。优先源码驱动深度复用；普通新实体使用预编译native能力，不默认Cargo/CI。自然typed Fluent优先，不要求完整IQueryable/EF，不在C#重写SQL AST/方言。SG可选生成static metadata/DTO，不是唯一查询路径。Core只提供可组合ABI/lifetime/buffer/error/async，无巨型runtime。保留严格安全和生产验收，实施授权以当前用户请求和精确任务门禁为准；不得把候选任务直接标为已验收。

读取source-driven-baseline.json、同ID新packet和Design ADR-0002。独立Review检查新hash、backend拒绝、fallible binder、无逐实体Cargo、Server body/retirement、三图和未完成验证。旧Review不接受新内容；不增加规划层。


## 本轮文档合并例外与后续执行

Design PR5/Plan PR2曾获准在真实独立Reviewer不可用时，经严格自审、可执行检查和无未解决文档阻断项后合并；其self-review和独立复审缺口继续如实保留。当前用户允许符合条件的Design／Plan研究文档变更合并，应使用实际可用子代理开展独立核查并区分其审查与GitHub required review。此授权不绕过GitHub强制规则，不将作者冒充独立Reviewer，不自动接受技术契约或Delivery终结态。

合并后直接从R/D的ready/continuable开始源码、详细设计和编译研究。可执行fixture作为已有研究任务输出统一保存在Design，规模按研究需要确定；不得伪装成已满足A01/B01等全部产品前置。本轮禁止正式产品实施，即使一个设计或fixture已经通过。未来Codex实施另行进入产品阶段后仍须精确accepted契约、依赖与实际授权记录。
