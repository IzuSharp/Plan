# NativeWeave task index — source-driven Rust1.100 revision

Existing 34 Research, 32 Documentation, 48 candidate Delivery IDs retained. Exact paired Design commit: source-driven-baseline.json. No product implementation authorized.

## research

| ID | Task / packet | State |
|---|---|---|
| R01 | [稳定工具链与现代语言机制](research-tasks/R01.md) | partially_evidenced |
| R02 | [Native AOT、裁剪与平台支持](research-tasks/R02.md) | planned |
| R03 | [C ABI、布局与版本协商](research-tasks/R03.md) | planned |
| R04 | [P/Invoke、回调入口与FFI调用成本](research-tasks/R04.md) | planned |
| R05 | [绑定生成器与契约描述来源](research-tasks/R05.md) | planned |
| R06 | [Roslyn增量生成与分析器](research-tasks/R06.md) | planned |
| R07 | [句柄、所有权、GC与父子资源](research-tasks/R07.md) | planned |
| R08 | [Callback注销、重入与释放竞态](research-tasks/R08.md) | planned |
| R09 | [异步、取消与完成状态机](research-tasks/R09.md) | planned |
| R10 | [Buffer、Pinning、批处理与数据传输](research-tasks/R10.md) | planned |
| R11 | [Error、panic、异常与故障隔离](research-tasks/R11.md) | planned |
| R12 | [并发、执行器、线程亲和与关闭](research-tasks/R12.md) | planned |
| R13 | [MSBuild/Cargo、链接与目标平台](research-tasks/R13.md) | planned |
| R14 | [打包、兼容性、独立发布与来源](research-tasks/R14.md) | planned |
| R15 | [形式化与并发证明义务](research-tasks/R15.md) | planned |
| R16 | [差分、属性、模糊与故障测试](research-tasks/R16.md) | planned |
| R17 | [端到端性能、内存与开发成本](research-tasks/R17.md) | planned |
| R18 | [按能力组合的Engine接入与通用性](research-tasks/R18.md) | planned |
| R19 | [PostgreSQL驱动与纯C#对照](research-tasks/R19.md) | planned |
| R20 | [SQLite适配、并发与线程限制](research-tasks/R20.md) | planned |
| R21 | [连接池、事务、取消与恢复](research-tasks/R21.md) | planned |
| R22 | [类型映射、批量流与Schema演进](research-tasks/R22.md) | planned |
| R23 | [LINQ、Expression与编译期查询捕获](research-tasks/R23.md) | planned |
| R24 | [SQL语义、关系代数与参数安全](research-tasks/R24.md) | planned |
| R25 | [ORM特性、跟踪与现成方案比较](research-tasks/R25.md) | partially_evidenced |
| R26 | [Kestrel与纯C# AOT服务器基线](research-tasks/R26.md) | planned |
| R27 | [Rust网络引擎与C# Handler边界](research-tasks/R27.md) | partially_evidenced |
| R28 | [gRPC、MCP、TLS与协议适配](research-tasks/R28.md) | planned |
| R29 | [请求流、背压、超时与优雅关闭](research-tasks/R29.md) | planned |
| R30 | [可观测性、诊断关联与成本](research-tasks/R30.md) | planned |
| R31 | [数据库+服务器参考应用与故障恢复](research-tasks/R31.md) | planned |
| R32 | [桌面GUI/GPU与线程亲和扩展](research-tasks/R32.md) | planned |
| R33 | [iOS/Android、静态链接与平台生命周期](research-tasks/R33.md) | planned |
| R34 | [边界安全、输入验证与资源滥用](research-tasks/R34.md) | planned |

## documentation

| ID | Task / packet | State |
|---|---|---|
| D01 | [工具链、AOT与平台规范](documentation-tasks/D01.md) | draft_ready |
| D02 | [ABI及类型布局契约](documentation-tasks/D02.md) | draft_ready |
| D03 | [绑定IR、生成器与分析器规范](documentation-tasks/D03.md) | draft_ready |
| D04 | [所有权与资源生命周期契约](documentation-tasks/D04.md) | draft_ready |
| D05 | [Callback注册撤销与静默契约](documentation-tasks/D05.md) | draft_ready |
| D06 | [异步完成与取消契约](documentation-tasks/D06.md) | draft_ready |
| D07 | [Buffer、传输及内存契约](documentation-tasks/D07.md) | draft_ready |
| D08 | [Error、panic与异常边界契约](documentation-tasks/D08.md) | draft_ready |
| D09 | [并发、Runtime与关闭规范](documentation-tasks/D09.md) | draft_ready |
| D10 | [构建打包、版本与来源规范](documentation-tasks/D10.md) | draft_ready |
| D11 | [Engine接入规范与双模块验证](documentation-tasks/D11.md) | draft_ready |
| D12 | [证明义务与真实验证规范](documentation-tasks/D12.md) | draft_ready |
| D13 | [性能、内存与开发体验方法](documentation-tasks/D13.md) | draft_ready |
| D14 | [数据库驱动能力与适配规范](documentation-tasks/D14.md) | draft_ready |
| D15 | [连接池、事务与恢复契约](documentation-tasks/D15.md) | draft_ready |
| D16 | [查询IR、SQL语义与ORM范围](documentation-tasks/D16.md) | draft_ready |
| D17 | [AOT查询捕获、生成与安全动态API](documentation-tasks/D17.md) | draft_ready |
| D18 | [Server生命周期与适配规范](documentation-tasks/D18.md) | draft_ready |
| D19 | [协议、可观测性与安全规范](documentation-tasks/D19.md) | draft_ready |
| D20 | [生产级参考应用与验收设计](documentation-tasks/D20.md) | draft_ready |
| D21 | [未来引擎和移动平台扩展边界](documentation-tasks/D21.md) | draft_ready |
| D22 | [ABI、内存与资源开发任务编制](documentation-tasks/D22.md) | draft_ready |
| D23 | [生成器与分析器开发任务编制](documentation-tasks/D23.md) | draft_ready |
| D24 | [Callback、async与Runtime任务编制](documentation-tasks/D24.md) | draft_ready |
| D25 | [构建、打包与独立发布任务编制](documentation-tasks/D25.md) | draft_ready |
| D26 | [Engine、证明、测试与基准任务编制](documentation-tasks/D26.md) | draft_ready |
| D27 | [Database完整实现任务编制](documentation-tasks/D27.md) | draft_ready |
| D28 | [ORM与LINQ AOT实现任务编制](documentation-tasks/D28.md) | draft_ready |
| D29 | [Server与协议实现任务编制](documentation-tasks/D29.md) | draft_ready |
| D30 | [端到端、长期负载与领域发布任务编制](documentation-tasks/D30.md) | draft_ready |
| D31 | [全局追溯、版本兼容与后续Engine任务规范](documentation-tasks/D31.md) | draft_ready |
| D32 | [独立交叉Review与交付准备审查](documentation-tasks/D32.md) | draft_ready |

## delivery

| ID | Task / packet | State |
|---|---|---|
| A01 | [ABI描述、布局探针和版本读取](tasks/A01.md) | planned_candidate |
| A02 | [状态、能力及兼容性协商入口](tasks/A02.md) | planned_candidate |
| A03 | [同步句柄与资源lease](tasks/A03.md) | planned_candidate |
| A04 | [拥有Buffer与异步租约](tasks/A04.md) | planned_candidate |
| A05 | [受控错误与panic转换边界](tasks/A05.md) | planned_candidate |
| A06 | [Callback注册、撤销与排空](tasks/A06.md) | planned_candidate |
| A07 | [Task异步桥与取消状态机](tasks/A07.md) | planned_candidate |
| A08 | [可选执行器、容量与关闭](tasks/A08.md) | planned_candidate |
| A09 | [绑定契约IR与输入验证](tasks/A09.md) | planned_candidate |
| A10 | [C# LibraryImport绑定发射](tasks/A10.md) | planned_candidate |
| A11 | [Rust导出与ABI一致性检查](tasks/A11.md) | planned_candidate |
| A12 | [ABI、生命周期与AOT分析器](tasks/A12.md) | planned_candidate |
| A13 | [MSBuild与Cargo可复现构建图](tasks/A13.md) | planned_candidate |
| A14 | [Linux原生产物与AOT包验证](tasks/A14.md) | planned_candidate |
| A15 | [Windows原生产物与AOT包验证](tasks/A15.md) | planned_candidate |
| A16 | [独立NuGet/crate发布与来源记录](tasks/A16.md) | planned_candidate |
| A17 | [真实同步Engine接入验证](tasks/A17.md) | planned_candidate |
| A18 | [真实异步Engine接入验证](tasks/A18.md) | planned_candidate |
| A19 | [生命周期与异步可执行模型](tasks/A19.md) | planned_candidate |
| A20 | [ABI和资源跨语言性质与模糊测试](tasks/A20.md) | planned_candidate |
| A21 | [三路线基准与资源观测工具](tasks/A21.md) | planned_candidate |
| A22 | [ABI/API升级与兼容性测试](tasks/A22.md) | planned_candidate |
| A23 | [线程亲和与特殊平台接入探针](tasks/A23.md) | planned_candidate |
| A24 | [Engine接入脚手架及conformance入口](tasks/A24.md) | planned_candidate |
| B01 | [Data接口与动态metadata边界](tasks/B01.md) | planned_candidate |
| B02 | [Rust PostgreSQL执行Adapter](tasks/B02.md) | planned_candidate |
| B03 | [Rust SQLite执行Adapter](tasks/B03.md) | planned_candidate |
| B04 | [必需Rust Database Host与生命周期](tasks/B04.md) | planned_candidate |
| B05 | [Rust事务、池恢复与Unknown](tasks/B05.md) | planned_candidate |
| B06 | [Rust有界结果批次与流](tasks/B06.md) | planned_candidate |
| B07 | [Rust fallible参数codec与边界值](tasks/B07.md) | planned_candidate |
| B08 | [Rust迁移执行与版本ledger](tasks/B08.md) | planned_candidate |
| B09 | [最小查询绑定与metadata定义](tasks/B09.md) | planned_candidate |
| B10 | [可选静态descriptor与DTO生成](tasks/B10.md) | planned_candidate |
| B11 | [Rust SeaQuery深度绑定与能力检查](tasks/B11.md) | planned_candidate |
| B12 | [静态C# DTO物化与异常清理](tasks/B12.md) | planned_candidate |
| B13 | [强类型runtime Fluent原生查询](tasks/B13.md) | planned_candidate |
| B14 | [Rust显式关系CRUD与乐观并发](tasks/B14.md) | planned_candidate |
| B15 | [Kestrel Native AOT Host与Handler](tasks/B15.md) | planned_candidate |
| B16 | [HTTP流、请求预算与背压](tasks/B16.md) | planned_candidate |
| B17 | [可选Rust Server Engine适配](tasks/B17.md) | planned_candidate |
| B18 | [gRPC强类型与AOT协议包](tasks/B18.md) | planned_candidate |
| B19 | [MCP协议包与静态JSON元数据](tasks/B19.md) | planned_candidate |
| B20 | [诊断关联、超时与关闭协调](tasks/B20.md) | planned_candidate |
| B21 | [通用幂等任务参考服务](tasks/B21.md) | planned_candidate |
| B22 | [端到端故障、崩溃与长期资源验证](tasks/B22.md) | planned_candidate |
| B23 | [领域全负载性能与内存报告](tasks/B23.md) | planned_candidate |
| B24 | [领域兼容矩阵、独立包与发布验收](tasks/B24.md) | planned_candidate |

Task revisions are exact per graph; unaffected packets were not rewritten. R/D continuation is distinct from product acceptance.
