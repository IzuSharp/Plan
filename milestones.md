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
