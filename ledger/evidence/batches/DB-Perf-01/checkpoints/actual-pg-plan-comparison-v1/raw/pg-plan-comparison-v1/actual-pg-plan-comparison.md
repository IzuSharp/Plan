# DB-Perf-01：原始 PostgreSQL 四路实际 SQL 与计划比较

## 结论

**Korda 优化前后全部 35 个 case、57 个 SQL 契约步骤的实际计划相同。Dapper 与 Korda 的 31 个非 CRUD case，以及 CRUD 的所有 UPDATE 计划，也完全相同。需要单独披露两处差别：Dapper 的主键 Find 少一个 Limit 节点；直接 C++ 在 `range`、`offset`、`early-stop` 的重复执行中换了访问路径。**

本报告只读复核失败 campaign `45452087158`、attempt 2、measure job `138657301659` 的既存记录，没有执行数据库、构建、修改产品或改变正式负载。计划诊断带有 `auto_explain` 和语句日志，不能计作性能验收。该 campaign 的有效长测仍为 **0/8**。

## 原始证据与比较规则

- 原 ZIP：`checkpoint-0.zip`，7,368,695 B，SHA-256 `bc4f1195eba7fcd518120e8e3c61b0e1f6304f8a76dd1992ba7d3da4ebc1cb39`。只选择性读取成员，没有完整解包。
- 配套 JSON：`actual-pg-plan-comparison.json`，SHA-256 `d8c69d0f216e70b9b37dba36e32bc7272b902cb8c45e83902dc897053bb11c75`；保留 51 个原始 member 的路径/长度/SHA、8 个固定 Git 源引用、51 个不同的完整 Plan 对象和四路全部 57 个步骤的 SQL、参数、出现位置及哈希。
- 实际 harness 固定 `4ee348d8b9834a14327dcf68a105e34f52f81795`，workflow 固定 `75db602c59f3c3366488df9f1c1717934f7d850f`；after 包源码 `3d5ba3f9884308caa691718f73a74aa42be19d94`，before 包源码 `771bc77cbd68d3f932b99ed2497c0697bbba5f02`。
- 从四份原始 PostgreSQL JSON 日志逐行重解析，完整 `statements`、`plans`、SQL、有序参数值、PID、日志行号与原 `query-plan-evidence.json` 完全一致。每路 627 次业务 SQL 执行、539 个业务 executor plan 的共享 signature 需求精确核平。
- 原始 member SHA 是原字节哈希。Plan、参数、记录的 canonical SHA 是解析后 JSON 的 UTF-8 编码哈希，规则为排序对象键、逗号和冒号紧邻、保留 Unicode；不冒充原 JSON 子串哈希。日志行 SHA 包含原行尾。
- 完整 Plan 比较保留估计成本、基数、宽度、谓词及所有节点字段。另列的 access projection 只比较明确列出的节点/索引/关系/排序/连接结构，不能替代完整 Plan。SQL 规范化保留引号、字面量和位置参数，不删除 LIMIT、不重排谓词。

四路原始文件均位于 `runs/postgresql/query-plans-<route>/attempt-00/`：

| 路线 | `query-plan-evidence.json` 原始 SHA-256 | `postgres-query-plans.json` 原始 SHA-256 |
| --- | --- | --- |
| `direct_cpp` | `e18529bae98e6aeceac09ff57d569f84358b864235f070c9e2f176e6e5199a59` | `8608bc1816bc987eef3d8b71632aa87880be006f2fdd3a8bed463a94cb4ef607` |
| `korda_before` | `55241ce04fa35d74e34e3b55c3d116e87816bd75d51670e0262b14f70f47930e` | `bab47551c3fbe2fda0afb60b671e69dd13b2d1d60dd733acfbb88fd2893f7085` |
| `korda_after` | `d6b6c13d0b233b81a913db6ca8bde3b0679c3b0f19a96abe42167d04dac6fb12` | `8ea81839f882eb4f989e48256b64c9e94e4b129f63bb91ef47b8a1f7ca0332be` |
| `independent_csharp_orm` | `ee59a9eeea452449e9e6dea8bf689eb0836fe9e11d8c2b7c6a0df267b1abebbc` | `d48f0f67513b62eb1fdb6cc3c0ab1b2e7d9c443534fa865522d43a870ce38670` |

## 35 个业务 case 的核对结果

每路均有 350 次暖机与 35 次正式操作，共 11 个 case 周期。正式消费均为 854 行，失败、oracle failure 均为 0，资源所有者归零。三个托管实现的完整预期结果 digest 相同；原生结果未输出同类 expected-digest 字典，因此这里只沿用其原始逐操作 oracle 成功记录，不声称重新读取数据库验证了持久化状态。

下表的“完全相同”指完整 Plan 对象相同，包含估计值；“表达式/估计”仍保留原差异，不能改写为完整计划相同。

| Case | 正式消费行数 | 直接 C++ 相对 Korda | Dapper 相对 Korda |
| --- | ---: | --- | --- |
| `numeric` | 32 | 完全相同 | 完全相同 |
| `text` | 32 | 完全相同 | 完全相同 |
| `money` | 32 | 完全相同 | 完全相同 |
| `json` | 32 | 完全相同 | 完全相同 |
| `wide` | 32 | 完全相同 | 完全相同 |
| `optional-filter` | 32 | 同节点/索引；表达式或估计变化 | 完全相同 |
| `range` | 32 | 重复执行后换访问路径 | 完全相同 |
| `left-join` | 32 | 完全相同 | 完全相同 |
| `inner-join` | 32 | 完全相同 | 完全相同 |
| `null-notes` | 32 | 同节点/索引；表达式或估计变化 | 完全相同 |
| `literal-note` | 32 | 完全相同 | 完全相同 |
| `customer-totals` | 9 | 同节点/索引；表达式或估计变化 | 完全相同 |
| `product-totals` | 32 | 同节点/索引；表达式或估计变化 | 完全相同 |
| `empty-sum` | 1 | 完全相同 | 完全相同 |
| `cursor` | 32 | 完全相同 | 完全相同 |
| `offset` | 32 | 重复执行后换访问路径 | 完全相同 |
| `exists` | 1 | 同节点/索引；表达式或估计变化 | 完全相同 |
| `in-subquery` | 32 | 同节点/索引；表达式或估计变化 | 完全相同 |
| `cte` | 32 | 完全相同 | 完全相同 |
| `window` | 32 | 完全相同 | 完全相同 |
| `union-all` | 32 | 完全相同 | 完全相同 |
| `union` | 24 | 完全相同 | 完全相同 |
| `intersect` | 8 | 完全相同 | 完全相同 |
| `except` | 8 | 完全相同 | 完全相同 |
| `running-total` | 32 | 完全相同 | 完全相同 |
| `three-join` | 32 | 完全相同 | 完全相同 |
| `anti-association` | 32 | 完全相同 | 完全相同 |
| `nullable-order` | 32 | 完全相同 | 完全相同 |
| `raw-sql` | 32 | 完全相同 | 完全相同 |
| `related` | 53 | 同节点/索引；表达式或估计变化 | 完全相同 |
| `tx-commit` | 3 | 同节点/索引；参数表达式变化 | Find 少 Limit；UPDATE 相同；BEGIN 文本不同 |
| `tx-rollback` | 3 | 同节点/索引；参数表达式变化 | Find 少 Limit；UPDATE 相同；BEGIN 文本不同 |
| `partial-update` | 3 | 同节点/索引；参数表达式变化 | Find 少 Limit；UPDATE 相同；BEGIN 文本不同 |
| `stale-conflict` | 2 | 同节点/索引；参数表达式变化 | Find 少 Limit；UPDATE 相同；BEGIN 文本不同 |
| `early-stop` | 3 | 重复执行后换访问路径 | 完全相同 |

## 直接 C++ 的三处访问路径变化

三项的实际 SQL 和有序绑定值在四路完全一致；声明的客户端参数种类相同，但原日志没有服务端参数 OID。每项 C++ 的前 5 个实际记录与另外三路相同，随后 6 个记录出现另一种树；另外三路各 11 个记录保持共同树。此次数描述包括暖机的日志先后顺序，不冒充服务端 generic/custom 计数，也不凭此给暖机/正式边界打新标签。

| Case | 有序参数值 | 四路共同树 / C++ 前 5 次 | C++ 后 6 次 |
| --- | --- | --- | --- |
| `range` | `[1,1700000100,1700000200,32]` | Limit → orders_pkey Index Scan，CreatedAt 作为过滤 | Limit → Sort(Id) → orders_created Index Only Scan |
| `offset` | `[1,32,768]` | Limit → Sort(CreatedAt,Id) → Bitmap Heap Scan → orders_pkey Bitmap Index Scan | Limit → orders_created Index Only Scan |
| `early-stop` | `[1,1024]` | Limit → Sort(Id) → Bitmap Heap Scan → orders_pkey Bitmap Index Scan | Limit → orders_pkey Index Scan |

例如 `range` 的共同计划估计输出 32 行、总成本 27.08；另一计划估计输出 1 行、总成本 15.46。这些是规划器估计，不能当实测行数或速度收益；正式实际消费仍为 32 行。完整条件、估计值和差异路径均保留在 JSON 的 `planCatalog` 与 `caseComparisons`。

| Case | 共同完整 Plan canonical SHA-256 | 后续 C++ 完整 Plan canonical SHA-256 |
| --- | --- | --- |
| `range` | `a53600f1d8a11189bafe2db8d089e4992483b2028a4cfea476604c3999193e64` | `db91de84fb43fc290597b96605e5dc831a52673da262a7534d006b9547cc5064` |
| `offset` | `ffe59ce14e69615b9a65dff51b12f7b2d1d3e2d2fb640fe7abe4a6a89060ba67` | `002d7ecae5cd1ff71fa4940825cc029e252ca70288b251e5af6bfb43b2d65d10` |
| `early-stop` | `7176d59aac912ac112cf1587b3e7fdb5794642837fba2f06349b8c55757a2288` | `e5ea60dc5042e852d4b32ad5f92291f56b8ad1808fa63ed393dbb4f5eb251960` |

原生日志显示命名 prepared statement 的重复执行，两版 Korda 与 Dapper 日志使用 unnamed execute；变化后的 C++ 计划谓词含 `$1…`，而先前记录含具体常量。**“准备语句复用后 generic/custom 选择改变”只能列为假说。** 原记录的 `serverParameterOids` 和 `genericCustomPlanCounts` 都为 null，没有同连接的服务端计数，也未控制所有潜在因素，不能把 5/6 次直接命名为 custom/generic 次数。

另外七个 case（optional-filter、null-notes、customer-totals、product-totals、exists、in-subquery、related）只看到成本/基数或参数表达式变化；节点、索引及所定义的 access projection 一致。21 个 case 的四路完整 Plan 对象完全相同。

## CRUD：Find、事务开始与 UPDATE 参数

### Find 的 Limit 节点

四个 CRUD case 共用一个完整 Order 主键读取形状。Korda/native 的 SQL 有 `LIMIT $3`，绑定值 `[1,1024,2]`；Dapper 的真实 `FindSql` 没有 LIMIT，绑定 `[1,1024]`，通过 QuerySingleAsync 检查唯一结果。

Korda 的实际树为 Limit → orders_pkey Index Scan，Dapper 为 orders_pkey Index Scan。去掉 Korda 的唯一 Limit 根节点以及子节点因成为根而不再需要的 Parent Relationship 字段后，完整子树与 Dapper 完全一致，包括 Forward 方向、主键条件、估计 1 行、宽度 122、成本 0.28–8.30。固定数据契约的主键为 (TenantId,Id)，这里没有观察到扫描/索引/结果基数的实质变化。Limit 节点的差别是真实的，性能影响尚未单独测量。

| 实现 | Find Plan canonical SHA-256 |
| --- | --- |
| Korda（两版） | `55b1ee09da24a68633a55cca27f824f01cf029ebae8bd68958757a755a80fd22` |
| Dapper | `f5f909753b3db99beb2a7bbe604d52933958d791b7908490dab1826ece9d80fb` |

原日志没有应用 case 标签。同一个 Find signature 在每路有 121 个执行/计划记录，服务于 11 个逻辑 Find 步骤、各 11 个周期；这些索引不能在每个逻辑步骤重新相加。报告用共享 signature 总需求核对，保留逐步骤的关联索引和这一归因限制。

### BEGIN 的写法

Korda/native 实际发送 `BEGIN ISOLATION LEVEL READ COMMITTED READ WRITE`；Dapper/Npgsql 实际发送 `BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED`。BEGIN 是事务控制语句，原记录没有相应 executor Plan。两者都明确请求 READ COMMITTED，实际更新成功且回滚/恢复后的完整业务结果通过 oracle；这不构成读取了服务端 read-only GUC 的证据。单凭 BEGIN 文本差别，不能声称产生了访问路径、协议提交次数或网络往返的差别。

### UPDATE 参数次序

Dapper 源码的匿名对象把 tenant/id 放在前面，但实际服务器 `$1…` 按 SQL 出现顺序绑定。原始日志中普通更新值为 `["perf-mutated","2","1","1024"]`，部分 NULL 更新为 `[null,"1","1024"]`；乐观更新和 stale 更新也分别与 Korda/native 的有序值一致。不能把匿名对象字段顺序当作服务器参数序号。所有托管 UPDATE 完整计划相同，均为 ModifyTable(Update) → orders_pkey Index Scan；stale 检查另有相同的 Version 过滤。服务端 OID 仍未采集，客户端 kind 声明与服务器实际类型观测需分开。

### 真实执行步骤差异：提交前 SELECT 1

两版 Korda 各有 22 次额外 `SELECT 1`，每次紧邻后续 COMMIT；原生和 Dapper 没有这些探测。在 11 个业务周期中，tx-commit 和 partial-update 各执行一次。这与固定 after 产品 `native/cpp/src/host.cpp` 的提交前事务状态探测对应，异常状态处理属于现有语义，本次只读分析不提出删除。

| 范围（每路，包含暖机） | C++ | Korda before | Korda after | Dapper |
| --- | ---: | ---: | ---: | ---: |
| 去重后的业务契约 SQL 执行 | 627 | 627 | 627 | 627 |
| 对应 executor plan | 539 | 539 | 539 | 539 |
| 额外提交前 SELECT 1 | 0 | 22 | 22 | 0 |
| 原日志全部 statement（另含设置/诊断） | 666 | 659 | 659 | 633 |

全部 statement 总数包含不同的初始化、EXPLAIN 和框架探测，不能直接当每操作 SQL 次数比较。原生 result 中的 protocol counter 属于正式计量窗，服务器日志则包含暖机与设置；两者分母不同。SQL 执行、协议提交、poll 等待及物理网络往返分别保留；本报告不推导物理 RTT。

## 现有分层缺口与最小后续项

原有 native-layer-0/1/2 分别为 per-operation/drain-only、per-operation/product、reuse/product。它们保留了真实计时与 protocol 计数，但 `diagnosticExecutionPlans` 都是空对象，且没有 query-plan evidence。它们既没有证明各 preparation 生命周期下的实际计划相同，也不能解释 Dapper Find 的 SQL/Limit 差异。

1. **优先补 3 个 case：range、offset、early-stop。** 复用同一 SQL、有序参数、数据/索引、完整结果消费及提前结束后 drain 契约，另做非计时的实际计划诊断。固定 C1，至少保留同样 11 次记录。要隔离 preparation，应固定 confirmation，再比较 reuse 与 per-operation；若使用 reuse/drain 与 per-operation/product，只能说明两套完整执行契约的差别，不能单独归因 preparation。必要时在同一个执行连接采集 prepared-statement 参数类型和 generic/custom 计数，并把这些观察排除在计时窗外。
2. **Find 只有一个 SQL 形状，可条件性补窄对照。** 当前没有发现实质主键访问路径变化，不能宣称 Limit 对性能有影响。若要求精确树也一致，可仅增加完整 Order、复合键、LIMIT 2 的同 SQL 查询诊断，供四个 CRUD case 共享解释，并保持 exactly-one 检查和事务结果语义。保留真实 Dapper 无 LIMIT 主路；BEGIN 和 UPDATE 参数顺序没有证据支持再加新的分层。

上述是待执行项，不是已获得的结果。正式 35 case 混合负载和 8 段长测要求均不变。

## 身份与使用范围

| 路线 | 本次实际 ELF SHA-256 |
| --- | --- |
| `direct_cpp` | `ed8f8f3fc069e51ab185d7e626b4fbc9945b5048fa8f29472dd516335d18d45c` |
| `korda_before` | `d4fc9c4f4f0d861a78f56a9417c09c37c0827e6fe7a0ee37a67c455aa7d0dec3` |
| `korda_after` | `6d011e3feaad72bfe12b44be3a0f309623adafdd586b4b625ea013d4c8576319` |
| `independent_csharp_orm` | `e0f6ab1774d5e5da10d069c274daa8d22d0dfe348a4eefb595dbde81ce2e749b` |

两版 Korda 实际加载的 PostgreSQL 原生库 SHA 均为 `73f725104fb1bee5fc86a9bc371e556ea8358ac3a2d774c4823185e6da8984c6`。before 包版本 0.1.0-preview.3，after 候选 0.1.0-ci.1；Dapper 2.1.100 / Dapper.AOT 1.1.0 / Npgsql 11.0.0，均来自本次原始消费 receipt。原生静态驱动和运行包的完整输入身份仍以 runtime checkpoint 为准。

本报告不代表动态查询、并发业务期间的全部计划，不外推 SQLite 或后续 campaign。这里不拆分业务/框架分配，不新增 0 B 结论；全部端到端分配原始计数继续保留。成本估计、instrumented 日志时长和执行树差别都不能替代吞吐/尾延迟/CPU/内存的独立有效测量。

固定源码引用（完整字节 SHA 在 JSON 中）：

- [benchmarks/db-perf/plan_diagnostics.py](https://github.com/IzuSharp/Korda/blob/4ee348d8b9834a14327dcf68a105e34f52f81795/benchmarks/db-perf/plan_diagnostics.py)，commit `4ee348d8b9834a14327dcf68a105e34f52f81795`。
- [benchmarks/db-perf/workload/queries-v3.json](https://github.com/IzuSharp/Korda/blob/4ee348d8b9834a14327dcf68a105e34f52f81795/benchmarks/db-perf/workload/queries-v3.json)，commit `4ee348d8b9834a14327dcf68a105e34f52f81795`。
- [benchmarks/db-perf/managed/Dapper/LifecycleCases.cs](https://github.com/IzuSharp/Korda/blob/4ee348d8b9834a14327dcf68a105e34f52f81795/benchmarks/db-perf/managed/Dapper/LifecycleCases.cs)，commit `4ee348d8b9834a14327dcf68a105e34f52f81795`。
- [benchmarks/db-perf/managed/Korda/LifecycleCases.cs](https://github.com/IzuSharp/Korda/blob/4ee348d8b9834a14327dcf68a105e34f52f81795/benchmarks/db-perf/managed/Korda/LifecycleCases.cs)，commit `4ee348d8b9834a14327dcf68a105e34f52f81795`。
- [benchmarks/db-perf/managed/Korda/Dataset.cs](https://github.com/IzuSharp/Korda/blob/4ee348d8b9834a14327dcf68a105e34f52f81795/benchmarks/db-perf/managed/Korda/Dataset.cs)，commit `4ee348d8b9834a14327dcf68a105e34f52f81795`。
- [benchmarks/db-perf/native/main.cpp](https://github.com/IzuSharp/Korda/blob/4ee348d8b9834a14327dcf68a105e34f52f81795/benchmarks/db-perf/native/main.cpp)，commit `4ee348d8b9834a14327dcf68a105e34f52f81795`。
- [benchmarks/db-perf/campaign.py](https://github.com/IzuSharp/Korda/blob/4ee348d8b9834a14327dcf68a105e34f52f81795/benchmarks/db-perf/campaign.py)，commit `4ee348d8b9834a14327dcf68a105e34f52f81795`。
- [native/cpp/src/host.cpp](https://github.com/IzuSharp/Korda/blob/3d5ba3f9884308caa691718f73a74aa42be19d94/native/cpp/src/host.cpp)，commit `3d5ba3f9884308caa691718f73a74aa42be19d94`。
