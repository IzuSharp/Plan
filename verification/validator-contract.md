# 当前验证器的保证与限制

工具验证现有三图/114packet/21契约结构、路径范围、版本/字节hash、无环依赖和接受manifest绑定。它不能认证审查者真实身份或证明日志命令确实执行；真实源码/实验/独立审查另留证据。任何结构错误使ready/continuable fail closed。

accepted任务需要完整source Commit、当前node/packet digest、依赖revision/content/source/evidence快照、真实evidence和不同作者的独立review。accepted契约需要非空spec、精确version/content hash及独立review和受影响依赖。设计分析/evidence可以接受研究与规范；不能满足产品要求的actual native_aot_run等平台行。

当前Rust使命作为结构政策验证：B04必需原生DB、B15只应用层、B17唯一原生Server、B18/B19 host=B17、Kestrel仅比较。B24发布scope有全部必需domain组件；当前没有B15/B17择一条件组。旧泛用条件选择schema只属于历史/未来其他明确可选能力，不可使已确定使命退回undecided。

fragment是实现细节镜像而非新图；工具核对任务集合和关键实现字段。file ownership按仓库+规范化路径比较，根manifest整合锁只覆盖A13小文件集。References不自动成为执行依赖。

历史source-lifecycle/logical-admission检查在固定旧Commit对运行，保留当时未接受状态和旧host政策作为历史事实；当前完成检查独立验证新研究/规范/审查，不删除门禁，也不把旧状态断言强加到新版本。
