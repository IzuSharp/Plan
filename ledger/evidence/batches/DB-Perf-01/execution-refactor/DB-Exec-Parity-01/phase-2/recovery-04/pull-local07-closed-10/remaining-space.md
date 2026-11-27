# 剩余优化空间：只读判断07

**还有空间；目前不能承诺收回全部差距，也没有证据把差距都归为契约的必然成本。** integrated05 的 text1000 客户端CPU仍为 Dapper 的 SQLite 6.35–6.88倍、PG 8.53–9.76倍；但这只是剩余总量，不能直接分配给某段代码。除正在验证的 pull-local07，我未找到另一个“已量化独占CPU占比、尚未被普通A/B否定、且已有安全改法”的高影响执行热点。[S1,S2,S5]

## 还能继续查什么

| 方向 | 已量化的依据 | 可支持的下一步及边界 |
| --- | --- | --- |
| related32 构造与最终graph | 当前约516.1KB/业务，Dapper约74.1/51.2KB。深层已测 From 51,712B、EmitShape/Node 44,032/27,648B、最终frame60,504B及59,680B tape复制；capacity明确未改变From/最终graph。[S2,S3] | 最明确的剩余**资源**目标。可研究私有构造表示、有限形状复用或最终frame所有权；先证明具体重复工作可去掉，保持每调用输入快照、逻辑额度/错误顺序、mapper身份、DDL与并发安全。不能将这些B数换算成可回收CPU。 |
| PG单行结果与通用逐行/逐列工作 | Stage1千行有1,000个SINGLE_TUPLE、1,004次PQclear；两库有重复验证/编码/lease。B32只有124B尾部memmove、无vector-growth copy，不能称为“大量批搬移”。[S1] | 可研究能证明行/错误前缀及字节预算等价的执行适配或真正重复校验；目前只有次数/分配基数，未证明CPU收益。无条件chunk32已因部分结果/后续错误及额外lookahead所有权问题排除。[S1] |
| 剩余固定准入、EOF/close及非pull控制路径 | Worker-D已把千行native posts34→2，但仍有约33个managed offers；两个native posts分别为cleanup/final close。早停PG仍读取完整结果并完成额外Sync。[S5,S2] | 当前local07正在检验其中的managed调度。其它固定控制路径可列观察候选，尚无独占CPU/等待拆分或已验证替代；不能因有两个post就删除安全退休，也不能把WaitSlow采样占比等同可回收成本。[S8] |

## 哪些路已测过，哪些不能用来“省成本”

Common-A虽证明少一次符合条件的continuation hop，却没有稳定千行端点收益；PG无效cancel hook1002→0也无稳定收益；lease-B去掉1032次Release(0)/Monitor，CPU改善不复现。ready-row-C在PG千行两轮CPU **+4.91%/+8.55%**、p50 **+6.77%/+6.57%**，已拒绝。tail06虽有PG改善，SQLite mixed不复现净益且尾延迟风险，因此已拒统一合入。只有出现新的、可验证交互机制才有重开理由，不把这些旧方案再算作未开发收益。[S4,S5]

SQLite取消PERSISTENT、关系clone/capacity及decimal优化已有资源收益；capacity净省49,104B与55,552复制B，却未证明稳定CPU/延迟/RSS益处。BindCodec及SelectionEncoding深层scope本就为0B，不能继续凭名称指认分配热点。[S3,S4]

## 业务契约相同，不代表调度与寿命约束完全相同

同SQL/参数/DTO、完整oracle说明业务工作可比。Korda仍须同步捕获可变输入、在发起调用栈外执行需等待的provider工作，并保护每代owner、任意mapper期间的借用、取消注册/旧token退休及并发Dispose。PG还须在效果发生前确认元数据、关闭后证明ReadyForQuery或丢弃连接，并保留COMMIT确认丢失的Unknown结果。这些是**不可直接删掉的逻辑职责**，并未证明某一次锁、分配、队列或完整CPU差距不可优化。[S6,S7]

never-inline不等于每行都排队，也不要求后续执行使用不同OS TID；已就绪批内行仍可同步完成。Ready-row的负控已证明简单同步mapper会泄漏上下文，FromException(OCE)会改变Canceled状态。不能删借用、跳过动态SQLite类型/取消检查、提前归还owner/连接、缓存最后Cancel指针，或将Execute跨过metadata屏障。Dapper SQLite本次同步同线程路径也不能直接替换Korda的异步保证。[S1,S6,S7]

**继续/停止依据：**先让local07给出自己的机制和短测结论；若仍需推进，优先选择上表有具体资源基数的窄目标，或补尚未解释阶段的归因，再决定改动。收益必须在反向短A/B及相关业务/尾延迟/释放RSS中可复现；若方案落入噪声或只能靠放松契约成立，就结束该方案，保留未解释差距。既不预设本轮结束，也不把“还有差距”当成所有改法都值得继续的理由。用户取消的长测不恢复。

依据编号的精确任务相对路径见同目录 sources.json。这里只读既有小报告、源码和已发布汇总；没有新测量、构建、大档重哈希或产品改动。
