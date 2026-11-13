# NativeWeave Plan工作规则

本仓库是NativeWeave研究、文档与执行计划权威；Design契约在IzuSharp/NativeWeave-Design，产品在IzuSharp/NativeWeave。ArcForges文档只参考格式，不能继承其内容规则。

## 当前用户阶段约束

先读`CURRENT-PHASE.md`。当前只允许研究、详细设计、Design内实验及Plan完善，不允许任何正式产品实施。`NativeWeave:src/...`等Delivery输出是未来Codex任务路径，不是本轮写入授权。NativeWeave产品仓库保持只读；唯一例外是研究资产在Design／Plan验证并合并后关闭PR #1，不合并、不删除历史分支。本文或旧packet中的历史授权措辞不能覆盖当前用户要求。

1. 先读README、对应独立packet及精确版本输入；用户本会话的明确要求优先。
2. 三图不得合并成一条串行清单。研究/文档draft可以并行；产品任务必须有相关已接受契约和局部依赖。
3. 不把planned_candidate提升为accepted，也不把未执行的代码/模型/AOT声明为通过。
4. 只写自己的scope；图、registry、共享索引通过整合者小范围修改，不加全局单worker锁。
5. 修改graph/packet后运行`python3 tools/validate_graphs.py`。packet字节变更须更新明确hash并使旧review失效；禁止改hash来掩盖内容与Review不符。
6. 接受态必须绑定当前内容、实际证据、精确依赖与独立审查。命令日志/制品/源码状态分别记录，Windows与Linux证据不能互代。
7. 研究和文档任务可以创建独立分支与Draft PR；不擅自更改许可证、仓库权限、保护规则，或发布/合并产品。
8. 新engine使用独立fragment/任务/包；C#应用不得因为通用框架而无条件引入native runtime。

本文件不要求为已获授权的研究、文档和可逆验证再向用户逐项确认。


## Source-driven amendment (2026-11-12)

NativeWeave独立于ArcForges，ArcForges只参考格式。C#是应用开发层，正式消费必须Native AOT。Database底层必须Rust，managed驱动只作源码/基准对照；Rust Server可选且需证据。优先源码驱动深度复用；普通新实体使用预编译native能力，不默认Cargo/CI。自然typed Fluent优先，不要求完整IQueryable/EF，不在C#重写SQL AST/方言。SG可选生成static metadata/DTO，不是唯一查询路径。Core只提供可组合ABI/lifetime/buffer/error/async，无巨型runtime。保留严格安全和生产验收，不授权大规模产品实现。

读取source-driven-baseline.json、同ID新packet和Design ADR-0002。独立Review检查新hash、backend拒绝、fallible binder、无逐实体Cargo、Server body/retirement、三图和未完成验证。旧Review不接受新内容；不增加规划层。


## 2026-11-12 Rust1.100连续执行授权

历史Rust/Cargo1.100研究与真实两OS测试见Design R01。Design PR5/Plan PR2当时允许严格self-review和真实检查后合并；独立审查未完成的事实保留D32复审。现在从R/D的ready/continuable集合继续源码、设计及Design内fixture，不执行正式A/B Delivery。普通技术任务不再逐个询问；合并Design／Plan仍遵守实际GitHub门禁，不伪造独立审查或accepted契约。
