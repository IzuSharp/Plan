# Codex并行执行政策 v0.1（proposed）

本政策规划未来实施，不授权本次研究会话开始完整产品开发。初始delivery节点全部`planned_candidate`。它们要在相关技术选择被接受后细化接口、更新packet/hash、明确实施范围，再提升为planned。这里的实施授权记录表示用户已要求的审查门禁通过，不制造额外的逐任务用户确认流程。

## 工作单元与文件所有权

一个任务一个稳定ID、一个主要owner、一个隔离worktree/目录、一个独立PR。允许多个Windows/Linux会话同时工作。可修改范围以`write_scopes`为准；目录范围是下属文件，文件范围仅该文件；不能声称拥有父目录。禁止在其他模块里复制公共契约来绕过依赖。

worker提交自己的模块和测试、证据目录。根solution、集中Cargo workspace、共享registry/图和版本索引由整合者处理小范围change-request；领域worker不同时改这些文件。这是明确文件责任，不是所有任务轮流执行。

同一任务被重复领取时在合并前解决ownership，不让两个作者无标记写同一scope。基准机器、端口、共享数据库和真机可以使用限定资源租约，租约只约束正在占用资源的验证；普通研究、文档、编译不受全局锁限制。

## 真正的依赖

`start_dependencies`只包含当前packet需要的实际实现产物。契约输入是精确ID+版本+accepted；可在依赖实现未完成前写mock的情形须另建明确的契约/fixture任务，不能把mock测试当集成验收。研究和文档接受依赖与产品编译依赖不是同一张表。

纯C# Data/Query/Kestrel不需要等待全部Interop Core实现。原生数据库/Server只依赖所需handle/buffer/async/绑定能力。模型和基准工具可在accepted规范下独立实现。正式阶段B的native功能依赖已验收的相关阶段A机制；纯C#路径没有虚构native runtime依赖。

## 可选路线及发布范围

B04原生PostgreSQL、B17原生Server、B18 gRPC、B19 MCP是独立可选包/路线；selection_status未决时不代表已采用。选择后将该节点加入相关B21–B24局部验收，不选则显式excluded且不阻塞纯C#组合。选择状态和版本进入验收subject快照；后选新引擎必须重验相关组合，不能复用旧纯C#报告冒充。

B24包含精确revision的release_scope。总accepted只能描述scope内已验收组件，不能外推到未选择协议包、架构或平台。每个engine/crate/adapter独立版本发布；新engine增加独立task/fragment，不重排无关任务。

## Windows、Linux与Native AOT

初始正式目标候选为win-x64和linux-x64。任务证据按OS+arch+RID匹配；win-arm64不能代替win-x64。A14只负责Linux包、A15只负责Windows包，组合任务汇总两侧。A19模型本身提供模型工具验证，不伪称模型是AOT应用；公共运行时能力仍必须通过真实消费端AOT验证。

每次运行保留工具链、目标、源码/制品hash、命令、stdout/stderr、起止时间、checks和失败/超时。AOT同时要求publish与目标二进制实际执行，记录执行制品hash。工具不可用时blocked，不用JIT测试替代。

## 完成、审查与失败

accepted/complete/delivered等终结态均使用相同严格证据门禁。源码与packet/spec hash匹配；独立Review绑定当前内容和证据；依赖版本匹配；无blocking发现。身份不独立、manifest只是模板、测试失败/超时、AOT未执行、目标RID不符都会拒绝。

部分交付记partially_verified；失败记failed并保留可复放seed/日志。修复后只复验实际影响范围与required gate，不能通过删失败证据、全局抑制警告或修改验收值冒充通过。发布包/合并/权限变更遵从任务与用户已有授权；本研究启动包不会执行产品发布。


## Source-driven amendment (2026-11-12)

NativeWeave独立于ArcForges，ArcForges只参考格式。C#是应用开发层，正式消费必须Native AOT。Database底层必须Rust，managed驱动只作源码/基准对照；Rust Server可选且需证据。优先源码驱动深度复用；普通新实体使用预编译native能力，不默认Cargo/CI。自然typed Fluent优先，不要求完整IQueryable/EF，不在C#重写SQL AST/方言。SG可选生成static metadata/DTO，不是唯一查询路径。Core只提供可组合ABI/lifetime/buffer/error/async，无巨型runtime。保留严格安全和生产验收，不授权大规模产品实现。

读取source-driven-baseline.json、同ID新packet和Design ADR-0002。独立Review检查新hash、backend拒绝、fallible binder、无逐实体Cargo、Server body/retirement、三图和未完成验证。旧Review不接受新内容；不增加规划层。
