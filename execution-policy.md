# Codex并行执行政策 v0.1（proposed）

本政策规定未来 Codex 的正式并行实施。当前用户已明确纠正为研究、详细设计和开发规划阶段：不执行任何正式 A/B Delivery，不向 NativeWeave 产品仓库写代码；真实实验仅写入 NativeWeave-Design。研究、实验、文档修订与符合条件的 Design/Plan 合并无需逐项确认。未来产品实施须用户另行进入实施阶段，并满足精确 accepted 契约、任务依赖和实施授权记录。

## 工作单元与文件所有权

一个任务一个稳定ID、一个主要owner、一个隔离worktree/目录、一个独立PR。允许多个Windows/Linux会话同时工作。可修改范围以`write_scopes`为准；目录范围是下属文件，文件范围仅该文件；不能声称拥有父目录。禁止在其他模块里复制公共契约来绕过依赖。

worker提交自己的模块和测试、证据目录。根solution、集中Cargo workspace、共享registry/图和版本索引由整合者处理小范围change-request；领域worker不同时改这些文件。这是明确文件责任，不是所有任务轮流执行。

同一任务被重复领取时在合并前解决ownership，不让两个作者无标记写同一scope。基准机器、端口、共享数据库和真机可以使用限定资源租约，租约只约束正在占用资源的验证；普通研究、文档、编译不受全局锁限制。

## 真正的依赖

`start_dependencies`只包含当前packet需要的实际实现产物。契约输入是精确ID+版本+accepted；可在依赖实现未完成前写mock的情形须另建明确的契约/fixture任务，不能把mock测试当集成验收。研究和文档接受依赖与产品编译依赖不是同一张表。

Database底层必需Rust；不存在产品纯C#Data/Query fallback。Kestrel、独立研究/fixture和无数据库应用不等待全部Interop实现。正式native产品功能只依赖所需accepted契约/实现，不制造全局等待，也不把研究探针当阶段A生产验收。

## 可选路线及发布范围

B04是必需Rust Database Host，B02/B03是Rust providers。B15 Kestrel与B17 Rust Server均为未决定的产品host候选；R26/R17必须研究Kestrel对照，但不据此指定产品默认。B18 gRPC、B19 MCP分别选择。选择状态进入所有相关共享任务及B21–B24验收快照；新增组合必须复验，不能复用旧组合报告。

`conditional_dependencies.gate`可为`start`或`acceptance`：selected start边需要所选host的真实实现才能开始，并在终结接受时复查；selected acceptance边允许先开始局部工作，但最后接受必须有被选依赖的真实证据。B16/B18/B19/B20/B21按选中host建立start边，B22–B24按选中host建立acceptance边。未选中Kestrel时不制造B15产品等待，未选中Rust Server时不制造B17等待。

`required_selection_groups`的server-host组列出B15/B17，minimum_selected=1。相关节点的selection_inputs必须全部明确selected/excluded，且组内至少一项selected，才能ready或终结接受；两项都excluded、都undecided或一项selected另一项未定都不放行。允许两个host都selected，但形成各有证据的明确profile，不自动设置全局默认。组规则和两host的revision/content/selection一起绑定验收subject。这是候选依赖设计，不是产品阶段授权。

B18/B19额外使用`protocol_host_profiles`明确协议在哪个host启用；该矩阵复用现有精确`contract_inputs`与accepted契约检查，不接受自由填写的approved布尔。当前D19接缝仅为Kestrel候选设计，Rust条目contract_input=null。协议包selected时，所有selected host的协议启用/排除须决定且至少一个profile启用；启用条目缺适用accepted设计即blocked。双host可显式只支持Kestrel协议，Rust对应profile excluded；条件start边的`protocol_profile_selected=true`避免等待未启用的协议host。Rust-only + selected协议必须先补该host设计/adapter能力、精确契约和真实AOT/transport验收，不能暗装Kestrel或把Unsupported标为成功。矩阵与选择变更使旧任务/组合审查失效。

协议spec中的唯一`json nativeweave-protocol-host-profiles-v1`代码块声明`host_task_ids`，作为原有spec字节纳入content_sha256和独立Review；validator只从已接受且当前hash匹配的spec读取。Kestrel-only声明不能用于B17，无声明亦不放行。扩大host范围必然改变spec hash，原有接受机制必须重新核验；registry外的自由approved标志、Plan里换个映射或旧Review均不能扩权。

B24包含精确revision的release_scope。B04 when=always；B15/B17以及可选协议只在selected时进入组合。proposed scope也检查组件revision与选择引用；总accepted只能描述scope内已验收组件，不能外推到未选择协议包、架构或平台。每个engine/crate/adapter独立版本发布；新engine增加独立task/fragment，不重排无关任务。

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

用户当前明确授权Design PR5/Plan PR2在真实独立Reviewer不可用时，严格自审、可执行检查通过、无未解决文档阻断项后合并；如实标记self-review并保留D32独立复审。此例外不绕过GitHub强制规则，不将作者冒充独立Reviewer，不自动接受技术契约或Delivery终结态。

合并后直接从ready/continuable开始实际源码/编译工作。Research/Documentation下的小型可执行fixture可以作为已有研究任务输出，不伪装成已满足A01/B01等全部产品前置。这些只允许在 Design 中执行研究 fixture。当前不执行产品任务；未来 Codex 实施另按阶段授权、精确 accepted 契约、依赖与验收记录推进。
