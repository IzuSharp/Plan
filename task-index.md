# 全任务索引

本批任务提示词/packet修订：**0.1.1**。首次启动请按 [README 的输入定位](README.md#首次启动输入定位) 解析两仓库完整 commit SHA，并核对任务图与正文 hash；契约仍为 `0.1.0-draft / proposed`，任务状态不变。

每行链接都是完整可复制的独立任务。源码目标是待查证线索，任务存在不表示已执行。研究/文档可以现在开始；产品条目是候选。

## Research（34）

| ID | 任务 | 当前状态 |
| --- | --- | --- |
| [R01](research-tasks/R01.md) | 稳定工具链与现代语言机制 | planned |
| [R02](research-tasks/R02.md) | Native AOT、裁剪与平台支持 | planned |
| [R03](research-tasks/R03.md) | C ABI、布局与版本协商 | planned |
| [R04](research-tasks/R04.md) | P/Invoke、回调入口与FFI调用成本 | planned |
| [R05](research-tasks/R05.md) | 绑定生成器与契约描述来源 | planned |
| [R06](research-tasks/R06.md) | Roslyn增量生成与分析器 | planned |
| [R07](research-tasks/R07.md) | 句柄、所有权、GC与父子资源 | planned |
| [R08](research-tasks/R08.md) | Callback注销、重入与释放竞态 | planned |
| [R09](research-tasks/R09.md) | 异步、取消与完成状态机 | planned |
| [R10](research-tasks/R10.md) | Buffer、Pinning、批处理与数据传输 | planned |
| [R11](research-tasks/R11.md) | Error、panic、异常与故障隔离 | planned |
| [R12](research-tasks/R12.md) | 并发、执行器、线程亲和与关闭 | planned |
| [R13](research-tasks/R13.md) | MSBuild/Cargo、链接与目标平台 | planned |
| [R14](research-tasks/R14.md) | 打包、兼容性、独立发布与来源 | planned |
| [R15](research-tasks/R15.md) | 形式化与并发证明义务 | planned |
| [R16](research-tasks/R16.md) | 差分、属性、模糊与故障测试 | planned |
| [R17](research-tasks/R17.md) | 端到端性能、内存与开发成本 | planned |
| [R18](research-tasks/R18.md) | 按能力组合的Engine接入与通用性 | planned |
| [R19](research-tasks/R19.md) | PostgreSQL驱动与纯C#对照 | planned |
| [R20](research-tasks/R20.md) | SQLite适配、并发与线程限制 | planned |
| [R21](research-tasks/R21.md) | 连接池、事务、取消与恢复 | planned |
| [R22](research-tasks/R22.md) | 类型映射、批量流与Schema演进 | planned |
| [R23](research-tasks/R23.md) | LINQ、Expression与编译期查询捕获 | planned |
| [R24](research-tasks/R24.md) | SQL语义、关系代数与参数安全 | planned |
| [R25](research-tasks/R25.md) | ORM特性、跟踪与现成方案比较 | planned |
| [R26](research-tasks/R26.md) | Kestrel与纯C# AOT服务器基线 | planned |
| [R27](research-tasks/R27.md) | Rust网络引擎与C# Handler边界 | planned |
| [R28](research-tasks/R28.md) | gRPC、MCP、TLS与协议适配 | planned |
| [R29](research-tasks/R29.md) | 请求流、背压、超时与优雅关闭 | planned |
| [R30](research-tasks/R30.md) | 可观测性、诊断关联与成本 | planned |
| [R31](research-tasks/R31.md) | 数据库+服务器参考应用与故障恢复 | planned |
| [R32](research-tasks/R32.md) | 桌面GUI/GPU与线程亲和扩展 | planned |
| [R33](research-tasks/R33.md) | iOS/Android、静态链接与平台生命周期 | planned |
| [R34](research-tasks/R34.md) | 边界安全、输入验证与资源滥用 | planned |

## Documentation（32）

| ID | 任务 | 当前状态 |
| --- | --- | --- |
| [D01](documentation-tasks/D01.md) | 工具链、AOT与平台规范 | draft_ready |
| [D02](documentation-tasks/D02.md) | ABI及类型布局契约 | draft_ready |
| [D03](documentation-tasks/D03.md) | 绑定IR、生成器与分析器规范 | draft_ready |
| [D04](documentation-tasks/D04.md) | 所有权与资源生命周期契约 | draft_ready |
| [D05](documentation-tasks/D05.md) | Callback注册撤销与静默契约 | draft_ready |
| [D06](documentation-tasks/D06.md) | 异步完成与取消契约 | draft_ready |
| [D07](documentation-tasks/D07.md) | Buffer、传输及内存契约 | draft_ready |
| [D08](documentation-tasks/D08.md) | Error、panic与异常边界契约 | draft_ready |
| [D09](documentation-tasks/D09.md) | 并发、Runtime与关闭规范 | draft_ready |
| [D10](documentation-tasks/D10.md) | 构建打包、版本与来源规范 | draft_ready |
| [D11](documentation-tasks/D11.md) | Engine接入规范与双模块验证 | draft_ready |
| [D12](documentation-tasks/D12.md) | 证明义务与真实验证规范 | draft_ready |
| [D13](documentation-tasks/D13.md) | 性能、内存与开发体验方法 | draft_ready |
| [D14](documentation-tasks/D14.md) | 数据库驱动能力与适配规范 | draft_ready |
| [D15](documentation-tasks/D15.md) | 连接池、事务与恢复契约 | draft_ready |
| [D16](documentation-tasks/D16.md) | 查询IR、SQL语义与ORM范围 | draft_ready |
| [D17](documentation-tasks/D17.md) | AOT查询捕获、生成与安全动态API | draft_ready |
| [D18](documentation-tasks/D18.md) | Server生命周期与适配规范 | draft_ready |
| [D19](documentation-tasks/D19.md) | 协议、可观测性与安全规范 | draft_ready |
| [D20](documentation-tasks/D20.md) | 生产级参考应用与验收设计 | draft_ready |
| [D21](documentation-tasks/D21.md) | 未来引擎和移动平台扩展边界 | draft_ready |
| [D22](documentation-tasks/D22.md) | ABI、内存与资源开发任务编制 | draft_ready |
| [D23](documentation-tasks/D23.md) | 生成器与分析器开发任务编制 | draft_ready |
| [D24](documentation-tasks/D24.md) | Callback、async与Runtime任务编制 | draft_ready |
| [D25](documentation-tasks/D25.md) | 构建、打包与独立发布任务编制 | draft_ready |
| [D26](documentation-tasks/D26.md) | Engine、证明、测试与基准任务编制 | draft_ready |
| [D27](documentation-tasks/D27.md) | Database完整实现任务编制 | draft_ready |
| [D28](documentation-tasks/D28.md) | ORM与LINQ AOT实现任务编制 | draft_ready |
| [D29](documentation-tasks/D29.md) | Server与协议实现任务编制 | draft_ready |
| [D30](documentation-tasks/D30.md) | 端到端、长期负载与领域发布任务编制 | draft_ready |
| [D31](documentation-tasks/D31.md) | 全局追溯、版本兼容与后续Engine任务规范 | draft_ready |
| [D32](documentation-tasks/D32.md) | 独立交叉Review与交付准备审查 | draft_ready |

## Delivery阶段A（24）

| ID | 任务 | 当前状态 |
| --- | --- | --- |
| [A01](tasks/A01.md) | ABI描述、布局探针和版本读取 | planned_candidate |
| [A02](tasks/A02.md) | 状态、能力及兼容性协商入口 | planned_candidate |
| [A03](tasks/A03.md) | 同步句柄与资源lease | planned_candidate |
| [A04](tasks/A04.md) | 拥有Buffer与异步租约 | planned_candidate |
| [A05](tasks/A05.md) | 受控错误与panic转换边界 | planned_candidate |
| [A06](tasks/A06.md) | Callback注册、撤销与排空 | planned_candidate |
| [A07](tasks/A07.md) | Task异步桥与取消状态机 | planned_candidate |
| [A08](tasks/A08.md) | 可选执行器、容量与关闭 | planned_candidate |
| [A09](tasks/A09.md) | 绑定契约IR与输入验证 | planned_candidate |
| [A10](tasks/A10.md) | C# LibraryImport绑定发射 | planned_candidate |
| [A11](tasks/A11.md) | Rust导出与ABI一致性检查 | planned_candidate |
| [A12](tasks/A12.md) | ABI、生命周期与AOT分析器 | planned_candidate |
| [A13](tasks/A13.md) | MSBuild与Cargo可复现构建图 | planned_candidate |
| [A14](tasks/A14.md) | Linux原生产物与AOT包验证 | planned_candidate |
| [A15](tasks/A15.md) | Windows原生产物与AOT包验证 | planned_candidate |
| [A16](tasks/A16.md) | 独立NuGet/crate发布与来源记录 | planned_candidate |
| [A17](tasks/A17.md) | 真实同步Engine接入验证 | planned_candidate |
| [A18](tasks/A18.md) | 真实异步Engine接入验证 | planned_candidate |
| [A19](tasks/A19.md) | 生命周期与异步可执行模型 | planned_candidate |
| [A20](tasks/A20.md) | ABI和资源跨语言性质与模糊测试 | planned_candidate |
| [A21](tasks/A21.md) | 三路线基准与资源观测工具 | planned_candidate |
| [A22](tasks/A22.md) | ABI/API升级与兼容性测试 | planned_candidate |
| [A23](tasks/A23.md) | 线程亲和与特殊平台接入探针 | planned_candidate |
| [A24](tasks/A24.md) | Engine接入脚手架及conformance入口 | planned_candidate |

## Delivery阶段B（24）

| ID | 任务 | 当前状态 |
| --- | --- | --- |
| [B01](tasks/B01.md) | DataSource与数据库能力基础 | planned_candidate |
| [B02](tasks/B02.md) | PostgreSQL纯C#适配与基线 | planned_candidate |
| [B03](tasks/B03.md) | SQLite适配与线程/锁语义 | planned_candidate |
| [B04](tasks/B04.md) | 可选Rust PostgreSQL Engine与Adapter | planned_candidate |
| [B05](tasks/B05.md) | 事务状态、池租约与恢复策略 | planned_candidate |
| [B06](tasks/B06.md) | 批量、COPY与流式读取 | planned_candidate |
| [B07](tasks/B07.md) | 静态类型codec与值语义 | planned_candidate |
| [B08](tasks/B08.md) | 迁移、Schema检查与升级协调 | planned_candidate |
| [B09](tasks/B09.md) | 受限查询语义IR | planned_candidate |
| [B10](tasks/B10.md) | LINQ/Fluent语法捕获增量生成 | planned_candidate |
| [B11](tasks/B11.md) | PostgreSQL/SQLite SQL方言生成 | planned_candidate |
| [B12](tasks/B12.md) | 静态Mapper、实体元数据与AOT | planned_candidate |
| [B13](tasks/B13.md) | 运行时安全动态查询API | planned_candidate |
| [B14](tasks/B14.md) | 关系、工作单元与并发更新 | planned_candidate |
| [B15](tasks/B15.md) | Kestrel Native AOT Host与Handler | planned_candidate |
| [B16](tasks/B16.md) | HTTP流、请求预算与背压 | planned_candidate |
| [B17](tasks/B17.md) | 可选Rust Server Engine适配 | planned_candidate |
| [B18](tasks/B18.md) | gRPC强类型与AOT协议包 | planned_candidate |
| [B19](tasks/B19.md) | MCP协议包与静态JSON元数据 | planned_candidate |
| [B20](tasks/B20.md) | 诊断关联、超时与关闭协调 | planned_candidate |
| [B21](tasks/B21.md) | 通用幂等任务参考服务 | planned_candidate |
| [B22](tasks/B22.md) | 端到端故障、崩溃与长期资源验证 | planned_candidate |
| [B23](tasks/B23.md) | 领域全负载性能与内存报告 | planned_candidate |
| [B24](tasks/B24.md) | 领域兼容矩阵、独立包与发布验收 | planned_candidate |
