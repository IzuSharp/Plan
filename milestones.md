# 能力里程碑 v0.1（proposed）

里程碑是验收范围，不是全局串行开工规则。阶段A和B现在同时研究、同时编制Design/Plan；未来代码按精确契约与局部依赖推进。

| 里程碑 | 具体产物 | 真正接受门禁 | 可同时推进 |
| --- | --- | --- | --- |
| M0 研究与文档体系启动 | 三图、独立prompt、模板、初始证据、validator | 图一致性与独立初步Review；明确所有未证实项 | 全部R与D草案 |
| M1 局部契约可实现 | ABI/lifetime/callback/async/buffer/error、generator、DB/Query/Server候选逐项收敛 | 每个契约自己所需源码/模型/编译实验与独立Review | 不相关契约、Plan fragment、基准方法 |
| M2 通用Interop能力验收 | A01–A24实际需要的profile、两个真实不同engine、双平台AOT与兼容 | 安全不变量、真实Windows/Linux制品、失败注入和独立验收 | 已有契约下的纯C#数据库、Query和Server |
| M3 Database/ORM/Server能力验收 | B01–B20所选provider/query/server/protocol包 | SQL正确性、事务恢复、AOT、背压和释放；原生路径接受相关A能力 | 各provider、query生成、server/protocol独立PR |
| M4 组合与发布准备 | B21–B24的明确release_scope与参考应用 | 同语义负载、长期资源、故障恢复、升级兼容和独立Review | 未选新engine继续独立研究/接入 |

没有人为日期或吞吐目标。先获得现实工作量、工具链、硬件和基准数据，再给可验证的SLO与计划估计。M2未全部结束不禁止已具备局部输入的B任务；M4不能只凭部分包通过就宣布所有包可发布。


## Source-driven amendment (2026-11-12)

NativeWeave独立于ArcForges，ArcForges只参考格式。C#是应用开发层，正式消费必须Native AOT。Database底层必须Rust，managed驱动只作源码/基准对照；Rust Server可选且需证据。优先源码驱动深度复用；普通新实体使用预编译native能力，不默认Cargo/CI。自然typed Fluent优先，不要求完整IQueryable/EF，不在C#重写SQL AST/方言。SG可选生成static metadata/DTO，不是唯一查询路径。Core只提供可组合ABI/lifetime/buffer/error/async，无巨型runtime。保留严格安全和生产验收，不授权大规模产品实现。

读取source-driven-baseline.json、同ID新packet和Design ADR-0002。独立Review检查新hash、backend拒绝、fallible binder、无逐实体Cargo、Server body/retirement、三图和未完成验证。旧Review不接受新内容；不增加规划层。
