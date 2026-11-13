# 既有任务执行与并行政策

## 当前阶段

Research/Documentation及Design实验已授权；全部A/B任务只是未来实施说明，保持planned_candidate和not_authorized。接受相关契约不会自动授予产品写权限。无需为已授权的研究、修复、审查、提交和规则允许的Design/Plan合并反复确认。

## 局部依赖与组件验收

start边限制实际开始，acceptance边限制最终接受；两类边合并必须无环。references只追溯，不能变成等待全部Research/Documentation或整个阶段A的隐式锁。单一组件可以通过实际上游/ABI fixture完成组件验收；最终组合必须由明确下游任务使用精确组件Commit真实验证，不能让fixture冒充Host或无人负责集成。

B01声明Data公共接口；B02/B03原生provider、B05事务、B06流、B07codec可按接口并行，B04承担完整Host组合。B09依赖B01且B11复用B07，避免重复metadata/binder。B15声明C#应用层并在接受时等待B17真实Host；B16独立流组件，B17依赖B16，避免B16↔B17循环。A16可在A13后编制包，最终接受等待A14/A15/A22。A10/A11验证生成组件，A17/A18和领域Host负责与真实Core组合的完整验收。

## Rust Host 与协议

NativeWeave 采用 Source-Driven Deep Native Integration。C# 是应用开发语言，提供强类型 Fluent、静态元数据/DTO 和业务 Handler；数据库驱动、查询/方言/ORM 关系执行及 Server 网络/协议/运行时必须复用成熟 Rust 引擎。Kestrel、Npgsql 等只作对照。普通应用不手写 Rust/FFI，不因新增 Entity/DTO/Handler 重编译 native。保持正常 dotnet build/run 与真实 Native AOT 发布，不构造 C# SQL AST/完整 LINQ Provider 或巨型 Core runtime。

B15与B17不是候选Host选择组。B17是唯一正式Host；B18/B19的规范声明host_task_ids=[B17]，应用可不引用协议包，但现有48任务仍完整规划这两个包。B24发布scope包含B01–B23的精确revision，B04/B17始终必需。旧条件选择schema保留用于历史验证，当前图不再使用它表达已确定的Rust使命。

## Worktree与文件所有权

每任务使用task/<ID>-implementation（研究阶段相应research分支）。只改packet列出的模块/测试/evidence路径；native子目录互不覆盖。根solution、Directory.Build.props、Directory.Packages.props、global.json及native/Cargo.toml/lock由A13的workspace-manifest-integration锁串行合入最小注册补丁。任务自身代码与测试继续并行，不锁整个仓库。

新版本按精确输入更新受影响节点/契约和审查；不任意重排无关任务。先固定失败、输入hash和实际状态，再修复再验。发现真实基础契约冲突时回到其规范/ADR解决，不能在每个模块里各加一层胶水规避。

## 实施证据

正式产品验收必须覆盖任务的正常/异常/取消/并发/释放语义、Windows/Linux实际AOT、独立NuGet、真实DB/HTTP/TLS、源和制品身份。A16/B24要求真正干净的无Rust消费环境；移除当前PATH工具是已执行研究的一种机制验证，不能冒充从未安装Rust的机器。

B22/B23负责完整故障/长期资源/性能证据，正确性失败不能换成性能成功。比较路线必须功能/协议/数据/持久性等价；Kestrel只属于对照程序。包发布还需未来明确授权，当前不发布。
