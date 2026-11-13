> **Current phase:** research and detailed design only; see [CURRENT-PHASE.md](CURRENT-PHASE.md). Research experiments and current evidence belong in NativeWeave-Design. No product write or A/B Delivery execution is authorized.

# 研究政策 v0.1（proposed）

研究以问题与证据为单位。`Rxx`不是一个需要等其他专题结束才开始的串行阶段；交叉Review通常是接口，不是研究启动依赖。任务提示词包含具体问题、候选源码、正常/异常路径、成本比较、验证方法与独占输出。

## 证据与覆盖

固定真实完整commit SHA，记录repo/path/symbol/定位/测试，沿API→适配→FFI→状态→错误→释放→测试追踪。源码目标标`target_not_yet_read`直到实际阅读。tag可辅助显示，不代替SHA。README和官方说明可以给意图，不能替代核心实现链。对巨大项目只声称读过的机制范围。

每项核心结论区分source_confirmed、test_confirmed、official_doc_confirmed、inferred、pending、refuted。实际测试保存输入、工具链/目标、命令、退出码、stdout/stderr哈希、制品哈希和起止时间。AOT结果与JIT结果分开；模型结论保留公平性、状态界限、内存模型和未覆盖FFI/OS行为。

每个topic默认输出`report.md`、`evidence.json`、`coverage.json`，均在`NativeWeave-Design:docs/research/topics/Rxx/`。研究者可在其目录内新增必要最小实验，禁止把研究原型移入产品实现并冒充正式模块。

## 比较与自主发现

每项选择必须比较合理的纯C# Native AOT方案、混合方案与适当纯Rust方案。Rust可选，不能以理论性能替代完整负载证据。候选目录可以扩展，新增来源注明它解决的具体问题、读哪些实现与测试、为什么比已有来源有用，以及许可证/维护状态。

当前初始发现如union装箱、Npgsql动态能力、DapperAOT skip、SQLx rollback排队、hyper不稳定C API，应追到固定版本源码并尝试反例，不从局部观察推断整个生态不能使用。

## 完成、失败与重新验证

有足够证据支持该topic范围、比较和失败路径才进入review_ready。未能运行的平台保留blocked；结论缺证据则partially_evidenced，列准确缺口。独立审查接受的只是已声明范围，不能用“专家同意”代替证据。

源版本、契约或假设改变后做影响分析：局部复验受影响结论，旧证据保留可追溯历史。无关研究继续，不设置全局暂停。源证据不因时间流逝自动失真，但“最新版本/当前支持”这类陈述必须重新核验。


## Source-driven amendment (2026-11-12)

NativeWeave独立于ArcForges，ArcForges只参考格式。C#是应用开发层，正式消费必须Native AOT。Database底层必须Rust，managed驱动只作源码/基准对照；Rust Server可选且需证据。优先源码驱动深度复用；普通新实体使用预编译native能力，不默认Cargo/CI。自然typed Fluent优先，不要求完整IQueryable/EF，不在C#重写SQL AST/方言。SG可选生成static metadata/DTO，不是唯一查询路径。Core只提供可组合ABI/lifetime/buffer/error/async，无巨型runtime。保留严格安全和生产验收，不授权大规模产品实现。

读取source-driven-baseline.json、同ID新packet和Design ADR-0002。独立Review检查新hash、backend拒绝、fallible binder、无逐实体Cargo、Server body/retirement、三图和未完成验证。旧Review不接受新内容；不增加规划层。
