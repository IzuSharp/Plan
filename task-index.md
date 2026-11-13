# NativeWeave 任务索引

现有三图：34 Research、32 Documentation、48 未来 Delivery。修订0.3.0；状态/接受以图为准，产品实施当前未授权。

## research

| ID | 任务 | 独立说明 |
| --- | --- | --- |
| R01 | 稳定工具链与现代语言机制 | [R01](research-tasks/R01.md) |
| R02 | Native AOT、裁剪与平台支持 | [R02](research-tasks/R02.md) |
| R03 | C ABI、布局与版本协商 | [R03](research-tasks/R03.md) |
| R04 | P/Invoke、回调入口与FFI调用成本 | [R04](research-tasks/R04.md) |
| R05 | 绑定生成器与契约描述来源 | [R05](research-tasks/R05.md) |
| R06 | Roslyn增量生成与分析器 | [R06](research-tasks/R06.md) |
| R07 | 句柄、所有权、GC与父子资源 | [R07](research-tasks/R07.md) |
| R08 | Callback注销、重入与释放竞态 | [R08](research-tasks/R08.md) |
| R09 | 异步、取消与完成状态机 | [R09](research-tasks/R09.md) |
| R10 | Buffer、Pinning、批处理与数据传输 | [R10](research-tasks/R10.md) |
| R11 | Error、panic、异常与故障隔离 | [R11](research-tasks/R11.md) |
| R12 | 并发、执行器、线程亲和与关闭 | [R12](research-tasks/R12.md) |
| R13 | MSBuild/Cargo、链接与目标平台 | [R13](research-tasks/R13.md) |
| R14 | 打包、兼容性、独立发布与来源 | [R14](research-tasks/R14.md) |
| R15 | 形式化与并发证明义务 | [R15](research-tasks/R15.md) |
| R16 | 差分、属性、模糊与故障测试 | [R16](research-tasks/R16.md) |
| R17 | 端到端性能、内存与开发成本 | [R17](research-tasks/R17.md) |
| R18 | 按能力组合的Engine接入与通用性 | [R18](research-tasks/R18.md) |
| R19 | PostgreSQL驱动与纯C#对照 | [R19](research-tasks/R19.md) |
| R20 | SQLite适配、并发与线程限制 | [R20](research-tasks/R20.md) |
| R21 | 连接池、事务、取消与恢复 | [R21](research-tasks/R21.md) |
| R22 | 类型映射、批量流与Schema演进 | [R22](research-tasks/R22.md) |
| R23 | 强类型查询、Expression 边界与静态捕获 | [R23](research-tasks/R23.md) |
| R24 | SQL语义、关系代数与参数安全 | [R24](research-tasks/R24.md) |
| R25 | ORM特性、跟踪与现成方案比较 | [R25](research-tasks/R25.md) |
| R26 | Kestrel与纯C# AOT服务器基线 | [R26](research-tasks/R26.md) |
| R27 | Rust网络引擎与C# Handler边界 | [R27](research-tasks/R27.md) |
| R28 | gRPC、MCP、TLS与协议适配 | [R28](research-tasks/R28.md) |
| R29 | 请求流、背压、超时与优雅关闭 | [R29](research-tasks/R29.md) |
| R30 | 可观测性、诊断关联与成本 | [R30](research-tasks/R30.md) |
| R31 | 数据库+服务器参考应用与故障恢复 | [R31](research-tasks/R31.md) |
| R32 | 桌面GUI/GPU与线程亲和扩展 | [R32](research-tasks/R32.md) |
| R33 | iOS/Android、静态链接与平台生命周期 | [R33](research-tasks/R33.md) |
| R34 | 边界安全、输入验证与资源滥用 | [R34](research-tasks/R34.md) |

## documentation

| ID | 任务 | 独立说明 |
| --- | --- | --- |
| D01 | 工具链、AOT与平台规范 | [D01](documentation-tasks/D01.md) |
| D02 | ABI及类型布局契约 | [D02](documentation-tasks/D02.md) |
| D03 | 绑定IR、生成器与分析器规范 | [D03](documentation-tasks/D03.md) |
| D04 | 所有权与资源生命周期契约 | [D04](documentation-tasks/D04.md) |
| D05 | Callback注册撤销与静默契约 | [D05](documentation-tasks/D05.md) |
| D06 | 异步完成与取消契约 | [D06](documentation-tasks/D06.md) |
| D07 | Buffer、传输及内存契约 | [D07](documentation-tasks/D07.md) |
| D08 | Error、panic与异常边界契约 | [D08](documentation-tasks/D08.md) |
| D09 | 并发、Runtime与关闭规范 | [D09](documentation-tasks/D09.md) |
| D10 | 构建打包、版本与来源规范 | [D10](documentation-tasks/D10.md) |
| D11 | Engine接入规范与双模块验证 | [D11](documentation-tasks/D11.md) |
| D12 | 证明义务与真实验证规范 | [D12](documentation-tasks/D12.md) |
| D13 | 性能、内存与开发体验方法 | [D13](documentation-tasks/D13.md) |
| D14 | 数据库驱动能力与适配规范 | [D14](documentation-tasks/D14.md) |
| D15 | 连接池、事务与恢复契约 | [D15](documentation-tasks/D15.md) |
| D16 | 原生查询语义与 ORM 范围 | [D16](documentation-tasks/D16.md) |
| D17 | AOT查询捕获、生成与安全动态API | [D17](documentation-tasks/D17.md) |
| D18 | Server生命周期与适配规范 | [D18](documentation-tasks/D18.md) |
| D19 | 协议、可观测性与安全规范 | [D19](documentation-tasks/D19.md) |
| D20 | 生产级参考应用与验收设计 | [D20](documentation-tasks/D20.md) |
| D21 | 未来引擎和移动平台扩展边界 | [D21](documentation-tasks/D21.md) |
| D22 | ABI、内存与资源开发任务编制 | [D22](documentation-tasks/D22.md) |
| D23 | 生成器与分析器开发任务编制 | [D23](documentation-tasks/D23.md) |
| D24 | Callback、async与Runtime任务编制 | [D24](documentation-tasks/D24.md) |
| D25 | 构建、打包与独立发布任务编制 | [D25](documentation-tasks/D25.md) |
| D26 | Engine、证明、测试与基准任务编制 | [D26](documentation-tasks/D26.md) |
| D27 | Database完整实现任务编制 | [D27](documentation-tasks/D27.md) |
| D28 | 强类型 Fluent 与原生 ORM 实现任务编制 | [D28](documentation-tasks/D28.md) |
| D29 | Server与协议实现任务编制 | [D29](documentation-tasks/D29.md) |
| D30 | 端到端、长期负载与领域发布任务编制 | [D30](documentation-tasks/D30.md) |
| D31 | 全局追溯、版本兼容与后续Engine任务规范 | [D31](documentation-tasks/D31.md) |
| D32 | 独立交叉Review与交付准备审查 | [D32](documentation-tasks/D32.md) |

## delivery

| ID | 任务 | 独立说明 |
| --- | --- | --- |
| A01 | ABI描述、布局探针和版本读取 | [A01](tasks/A01.md) |
| A02 | 状态、能力及兼容性协商入口 | [A02](tasks/A02.md) |
| A03 | 同步句柄与资源lease | [A03](tasks/A03.md) |
| A04 | 拥有Buffer与异步租约 | [A04](tasks/A04.md) |
| A05 | 受控错误与panic转换边界 | [A05](tasks/A05.md) |
| A06 | Callback注册、撤销与排空 | [A06](tasks/A06.md) |
| A07 | Task异步桥与取消状态机 | [A07](tasks/A07.md) |
| A08 | 可选执行器、容量与关闭 | [A08](tasks/A08.md) |
| A09 | 绑定契约IR与输入验证 | [A09](tasks/A09.md) |
| A10 | C# LibraryImport绑定发射 | [A10](tasks/A10.md) |
| A11 | Rust导出与ABI一致性检查 | [A11](tasks/A11.md) |
| A12 | ABI、生命周期与AOT分析器 | [A12](tasks/A12.md) |
| A13 | MSBuild与Cargo可复现构建图 | [A13](tasks/A13.md) |
| A14 | Linux原生产物与AOT包验证 | [A14](tasks/A14.md) |
| A15 | Windows原生产物与AOT包验证 | [A15](tasks/A15.md) |
| A16 | 独立NuGet/crate发布与来源记录 | [A16](tasks/A16.md) |
| A17 | 真实同步Engine接入验证 | [A17](tasks/A17.md) |
| A18 | 真实异步Engine接入验证 | [A18](tasks/A18.md) |
| A19 | 生命周期与异步可执行模型 | [A19](tasks/A19.md) |
| A20 | ABI和资源跨语言性质与模糊测试 | [A20](tasks/A20.md) |
| A21 | 三路线基准与资源观测工具 | [A21](tasks/A21.md) |
| A22 | ABI/API升级与兼容性测试 | [A22](tasks/A22.md) |
| A23 | 线程亲和与特殊平台接入探针 | [A23](tasks/A23.md) |
| A24 | Engine接入脚手架及conformance入口 | [A24](tasks/A24.md) |
| B01 | Data接口与动态metadata边界 | [B01](tasks/B01.md) |
| B02 | Rust PostgreSQL执行Adapter | [B02](tasks/B02.md) |
| B03 | Rust SQLite执行Adapter | [B03](tasks/B03.md) |
| B04 | 必需Rust Database Host与生命周期 | [B04](tasks/B04.md) |
| B05 | Rust事务、池恢复与Unknown | [B05](tasks/B05.md) |
| B06 | Rust有界结果批次与流 | [B06](tasks/B06.md) |
| B07 | Rust fallible参数codec与边界值 | [B07](tasks/B07.md) |
| B08 | Rust迁移执行与版本ledger | [B08](tasks/B08.md) |
| B09 | 最小查询绑定与metadata定义 | [B09](tasks/B09.md) |
| B10 | 可选静态descriptor与DTO生成 | [B10](tasks/B10.md) |
| B11 | Rust SeaQuery深度绑定与能力检查 | [B11](tasks/B11.md) |
| B12 | 静态C# DTO物化与异常清理 | [B12](tasks/B12.md) |
| B13 | 强类型runtime Fluent原生查询 | [B13](tasks/B13.md) |
| B14 | Rust显式关系CRUD与乐观并发 | [B14](tasks/B14.md) |
| B15 | C# Server Application、强类型 Handler 与静态注册 | [B15](tasks/B15.md) |
| B16 | Rust Body 与 C# 租约的有界流和预算 | [B16](tasks/B16.md) |
| B17 | 必需 Rust Server Host 与 Handler 边界 | [B17](tasks/B17.md) |
| B18 | 原生 Tonic gRPC 与 C# 静态 Protobuf 映射 | [B18](tasks/B18.md) |
| B19 | 原生 rmcp 与 C# 静态工具和 JSON 映射 | [B19](tasks/B19.md) |
| B20 | 诊断关联、总期限与关闭协调 | [B20](tasks/B20.md) |
| B21 | 通用幂等任务参考服务 | [B21](tasks/B21.md) |
| B22 | 端到端故障、崩溃与长期资源验证 | [B22](tasks/B22.md) |
| B23 | 领域全负载性能与内存报告 | [B23](tasks/B23.md) |
| B24 | 领域兼容矩阵、独立包与发布验收 | [B24](tasks/B24.md) |
