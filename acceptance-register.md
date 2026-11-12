# 初始验收登记

截至首次交付，状态如下；本登记是便于阅读的解释，权威任务状态在各图，契约状态在Design registry。不要独立在此复制每个task的动态状态。

| 对象 | 实际状态 | 能说明什么 |
| --- | --- | --- |
| 34个Research任务 | planned | 问题、候选来源、证据标准和独占输出已定义，可并行查证 |
| 32个Documentation任务 | draft_ready | Design规范与Plan fragment可以并行编制 |
| 21个契约 | proposed，0.1.0-draft | 需求和职责已分配，尚未接受具体产品设计 |
| 48个Delivery候选 | planned_candidate | 完整覆盖两阶段并提供候选接口/范围/验证；不能据此无审查实施 |
| Python图校验 | 实际执行，结果见verification | 校验ID、依赖、版本、路径与本地证据门禁；不证明产品 |
| 错误注入检查 | 实际执行，结果见verification | 指定错误会被拒绝且ready fail closed |
| Windows/Linux产品AOT | 未执行 | 没有对应产品制品，不能声称通过 |
| 独立Review | 仅限本次初始体系实际审查记录 | 不替代全部未来Design与产品最终验收 |

进入accepted需要本地manifest完整性校验和独立实质审查。manifest自身可被人写出来；工具不认证身份或实际执行真伪，Review必须回到固定源码、原始日志、制品与可信执行环境。
