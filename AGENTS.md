# NativeWeave Plan 工作规则

NativeWeave 采用 Source-Driven Deep Native Integration。C# 是应用开发语言，提供强类型 Fluent、静态元数据/DTO 和业务 Handler；数据库驱动、查询/方言/ORM 关系执行及 Server 网络/协议/运行时必须复用成熟 Rust 引擎。Kestrel、Npgsql 等只作对照。普通应用不手写 Rust/FFI，不因新增 Entity/DTO/Handler 重编译 native。保持正常 dotnet build/run 与真实 Native AOT 发布，不构造 C# SQL AST/完整 LINQ Provider 或巨型 Core runtime。

1. 当前只研究、设计和完善未来实施计划。用户已授权必要Design/Plan提交、PR及符合仓库规则的合并；不重复询问。NativeWeave产品不写入。
2. 保留34R/32D/48Delivery和三图；`fragments/`仅细化既有任务。先读已存在成果和真实审查，再补缺口。
3. 每项packet/graph有精确revision/hash；接受绑定实际来源、依赖和独立审查，不能只改status或补假证据。
4. 技术设计可以在产品实现前接受；产品AOT/真实服务/长负载/发布义务单列。源码已读、上游测试已读、实际运行和产品验收严格区分。
5. 只写自己的scope。独立Worktree并行；共享根构建manifest走A13整合小补丁，不设置全局锁。
6. 修改当前图/packet/registry后运行结构、当前完成度和负例门禁；旧冻结检查在旧Commit执行，不能把旧proposed快照当永远禁止接受的规则。
7. 保留失败记录、原始字节和独立Windows/Linux身份；二进制省略时明确其archive/内容hash及再现方式。
8. 子代理可做真实独立技术审查，但同GitHub身份不能冒充另一个审批账号。不得绕过Required Checks或修改权限/许可证以使合并通过。
