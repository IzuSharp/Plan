# 独立技术审查输入

先读当前阶段、三图、对应114packet和Design registry确切版本/hash；读取实际源码定位、输入快照、原始实验/失败日志，而不是只看作者摘要。NativeWeave 采用 Source-Driven Deep Native Integration。C# 是应用开发语言，提供强类型 Fluent、静态元数据/DTO 和业务 Handler；数据库驱动、查询/方言/ORM 关系执行及 Server 网络/协议/运行时必须复用成熟 Rust 引擎。Kestrel、Npgsql 等只作对照。普通应用不手写 Rust/FFI，不因新增 Entity/DTO/Handler 重编译 native。保持正常 dotnet build/run 与真实 Native AOT 发布，不构造 C# SQL AST/完整 LINQ Provider 或巨型 Core runtime。

## 审查清单

1. 是否真正解决本任务的问题；哪些原有成果只是状态落后，哪些新增证据弥补了什么风险。
2. C#和Rust职责、公开API/专用Adapter/上游扩展/受控fork是否有来源；不得私有布局穿透或重复引擎。
3. 指针/长度/状态/ErrorRecord容量、逻辑准入/物理lease、取消/terminal/take/回调双退休和allocator是否一致。
4. SQLx真实事务/协议恢复/Unknown、SeaORM动态shape、SeaQuery后端能力和参数binder是否保持真实语义。
5. Server的Handler/Body/Bytes/permit/队列/截止时间/协议验证，Tonic/rmcp实际公开API限制是否覆盖；B17是唯一正式Host。
6. 当前34R/32D/21契约是否足以指导48Delivery；114packet/三图/fragment所有权与局部依赖是否无环且不过度等待。
7. 源码已读、上游测试已读、真实运行、有限模型与产品验收是否严格区分；不能要求未来产品先实现才接受设计。

输出真实reviewer/author、精确输入SHA与来源、每项结论、finding严重性/修复复读、未消除阻断及未来产品义务。接受前全部阻断关闭。相同GitHub账号的子代理审查不是平台独立审批身份。
