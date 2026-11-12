# NativeWeave Plan工作规则

本仓库是NativeWeave研究、文档与执行计划权威；Design契约在IzuSharp/NativeWeave-Design，产品在IzuSharp/NativeWeave。ArcForges文档只参考格式，不能继承其内容规则。

1. 先读README、对应独立packet及精确版本输入；用户本会话的明确要求优先。
2. 三图不得合并成一条串行清单。研究/文档draft可以并行；产品任务必须有相关已接受契约和局部依赖。
3. 不把planned_candidate提升为accepted，也不把未执行的代码/模型/AOT声明为通过。
4. 只写自己的scope；图、registry、共享索引通过整合者小范围修改，不加全局单worker锁。
5. 修改graph/packet后运行`python3 tools/validate_graphs.py`。packet字节变更须更新明确hash并使旧review失效；禁止改hash来掩盖内容与Review不符。
6. 接受态必须绑定当前内容、实际证据、精确依赖与独立审查。命令日志/制品/源码状态分别记录，Windows与Linux证据不能互代。
7. 研究和文档任务可以创建独立分支与Draft PR；不擅自更改许可证、仓库权限、保护规则，或发布/合并产品。
8. 新engine使用独立fragment/任务/包；C#应用不得因为通用框架而无条件引入native runtime。

本文件不要求为已获授权的研究、文档和可逆验证再向用户逐项确认。
