# DB-Runtime-Compare-01 第二轮独立审查

## 最新用户授权：192 MiB 请求配置、取消 cgroup 要求

用户随后明确192可以接受，并不再要求cgroup。主代理据此将所有C#客户端的请求GC配置统一为 **192 MiB = 201,326,592 B = 0xC000000**，实际RSS与GC行为照实记录；不宣称192MiB总进程硬上限。下面128MiB/cgroup阻断部分保留为之前决策的历史事实，**不再作为当前运行准入阻断**。

新审查关注EF attempt03以及Java最终修复候选的源码/配置/执行文件绑定。用户允许继续不等于限制已生效，`enforced`必须保留实际状态；Satori配置被读取但未按heap limit生效的观察也不因此消失。runtime-async仍须保持，有限35类验证与正式八段30分钟分别记录。EF attempt03与Java最终正式准入候选现均已完成独立身份及有限正确性复核，结论与实际回执见文末；正式时长验收由后续串行campaign完成。

## 审查范围与初次记录时结论（历史）

这是对现有源码、构建身份、有限正确性回执和内存准入条件的只读审查。审查者没有启动数据库、运行客户端、发起编译或压测，没有改冻结源码或远端对象。先前 EF 四组 runtime-async 有限验证及64个PDB源码文档绑定结论保存在 `../review-01/`。

**截至本轮初次记录，正式30分钟长测仍为0/8，128MiB C#客户端总量边界尚未建立。** Java第一份绑定源码的Native ELF构建成功，但在首次SQLite配置/元数据查询阶段初始化jOOQ失败，没有完成业务验证；失败身份已核实保留。精确reachability metadata修复后的重建与双库Native结果待追加。

## 原128MiB边界审查及可见环境（历史）

实际只读观测保存在 `memory-environment-review.json`：当前观察进程UID/GID1000；`/proc/self/cgroup`为`0::/`；本命名空间mountinfo中没有cgroup挂载，`/sys/fs/cgroup`不存在，CapEff/CapBnd为0。可见进程资源限制没有设置本任务的地址空间、data或RSS上限。

这些事实支持“当前命名空间没有可访问或委派的memory控制接口，尚未建立或验证本任务的128MiB客户端边界”。**它们不支持“宿主或不可见父cgroup没有限制”**。原探针字段`cgroupMemoryLimitPresent=false`只来自某一路径的File.Exists，不能作全宿主无上限结论。

此次复核指出并由主代理更正了“Database memory全部排除”的过宽表述：

- C#客户端总量边界包括CLR/GC堆、JIT、线程栈、驱动和客户端原生内存。
- SQLite在同一客户端进程内。SQLite原生库、其堆和应用内页面缓存必须算入客户端；不能既约束该进程又豁免进程里的SQLite。
- PostgreSQL服务端是独立进程，置于客户端边界之外；原`shared_buffers=128MB`配置保留，它并非服务端总内存上限。
- Java客户端不受本次C#128MB要求限制。文案统一为C#clients，避免无意豁免C# Native AOT。
- 本批明确记录的数值是128MiB=134,217,728B。

主代理新增的`memory-verification/cgroup-execution-plan.md`准确区分了控制器charged memory、进程RSS与managed heap，并明确只是合适宿主上的执行协议，尚未在此应用。已查核[Linux官方cgroup v2文档](https://docs.kernel.org/admin-guide/cgroup-v2.html)的memory.max、memory.swap.max、memory.oom.group与memory ownership：memory.max可能短暂超限，无法回收时可能组内OOM；迁移PID不会搬迁旧内存记账。因此exec和暖机之前入组、PG/观察者留在组外、记录真实控制器值及OOM退出结果的协议是必要的。它不能保证Satori在128MiB内完成业务，也不是严格瞬时RSS上限。

## 新增Native AOT内存探针

未重跑探针；直接核对既有 `clients/efcore/verification/native-aot-memory-probe/` 的project/source、publish/run回执、结果JSON与实际ELF。检查细节在 `native-aot-memory-review.json`。

| 观察项 | 已核实值 |
| --- | ---: |
| 编译/运行退出码 | 0 / 0 |
| ELF | 64位x86-64；SHA-256 `1f24ff8c0c28b68df7955e736c6d6334ef34912fe5a799f70ee383d5963538ed` |
| DynamicCodeSupported / Compiled | false / false |
| 请求与GC报告heap预算 | 134,217,728 B |
| 保留且逐页写入的数组 | 125,829,120 B，之后捕获OOM |
| GC committed | 126,070,784 B |
| 报告时RSS / peak RSS | 131,809,280 / 131,809,280 B |
| 正式比较资格 | false |

实际ELF大小/hash、result hash和两份源文件hash与运行/发布回执全部一致。项目明确PublishAot=true，probe源是显式包含的Program.cs.txt，未改变冻结EF实现。其有限算法最多保留24块8MiB数组，OOM被有意捕获，exit0不代表没有发生OOM。

这支持**所测stock Native AOT runtime应用了GC heap设置**。小探针RSS低于128MiB不是总进程硬上限的证明，更不是Dapper真实业务RSS或Satori行为的测量。已有Workstation/Satori三份配置探针与它分开保留；Satori两种配置传输方式均保留192MiB数组无OOM，不能按其打印的heap配置给限制有效信用。

## Java初次Native失败及修复范围

已核对 `clients/java/verification/native-final/` 的build identity、lifecycle与原始stderr hash，三处失败ELF身份均为`4c555266cea29024a33b105c91b086104540f8afb4de3bcb415df1e1995a2028`。构建成功与执行成功已明确分开：SQLite有限命令exit2，lifecycle=failed，无成功JSON。原始栈位于Database.open→jOOQ SQLDataType初始化，尚未进入35业务循环。PG当时未启动。

`native-metadata-agent/fix-evidence.json`的38个数组lookup已逐项与真实Graal agent元数据核对；注入resource metadata hash为`55b6b629411f46749d278b73d8447552c342f85a9ab564b3e1b96038e3794b0d`。与首次冻结相比，Java运行源码和pom hash全部不变，修改局限于Native Image可达性配置。没有把JIT成功替代Native，也未改SQL、DTO或oracle来绕过失败。检查文件为 `java-native-failure-review.json`。

上轮发现的Java主异常被cleanup替换问题也已在当前冻结Main源码修正：保存primary，最终清理继续尝试所有连接并将cleanup附加为suppressed。Failed>0保留完整结果后非零退出，JIT/Native标签分开，当时所有有限正确性路径的TimingComparisonEligible固定false；后续正式准入分流见文末，有限路径继续false。

## 待追加的最终Java复核

最终重建完成后，需只读核对冻结source/resources/pom、工具链、依赖、JAR和ELF身份，并核对同一ELF两库各35case+64warmup有限原始回执及退出码、实际SQLite映射和PG server-stop结果。只有这些实际完成后才可将Java有限正确性标为完成。正式长测、排队/拒绝模型实测、持续稳定性、受限内存性能与跨runtime效率结论不由有限检查推出。

## 192MiB授权后的EF attempt03最终复核

四组新的EF候选已独立完成只读绑定检查，详见 `ef-attempt03-binding.json`；可复现脚本 `review-ef-attempt03.py`。结果是**新授权下的有限正确性及构建身份通过，可以交外部正式runner评估执行条件**，并非四次正式测量已经完成。

- 四份Portable PDB的64个业务源码文档hash均与冻结attempt03源码匹配；source.zip全部源码/锁文件、DLL/PDB/apphost/runtimeconfig/deps、实际CoreCLR/JIT及原始回执hash均匹配。
- 四份真实编译参数仍有runtime-async=on，四运行均观测19个Async方法。
- SQLite/PG × Workstation/Satori各35业务成功一次、0业务错误、0Oracle错误、4次独立持久状态检查、逻辑连接归零。35项结果oracle与原manifest一致。
- runtimeconfig、运行ENV和实际GC配置三者一致为201326592B / 0xC000000。ClientMemoryBudgetEnforced与GcHeapBudgetEnforcementProven全部为false；OwnerAcceptedUnenforcedMemoryPolicy为true。
- Workstation实际报告可用201326592B；Satori实际仍报告10451427328B，原值完整保留。准入资格true不能被解释为Satori执行了heap硬限。
- 运行命令为35 operations而非1800 seconds，summary标记formalBenchmark=false/performanceAcceptanceCompleted=false。TimingComparisonEligible只表示用户接受的新配置策略，并未偷换已完成正式时长。
- attempt02旧四组全部20项发布产物及旧source archive仍匹配原hash，历史证据未覆盖。

## Java metadata修复候选的实际双库Native结果

`verification/native-metadata-fixed/`现已具有真实成功结果。同一ELF SHA-256为`dfabe47a9e92bf17d1d5fac96cbb6799cee4a5a39c1db61ca20b5702d6975cdb`，与两个运行回执和lifecycle一致；它是真实ELF64/x86-64，两个回执NativeAot=true。

检查 `java-metadata-fixed-binding.json`确认：保留source.tar.gz全部编译输入hash、JAR和JAR中的reachability resource、9个实际runtime依赖、JDK release和Graal metadata archive均绑定；build helper当前文件hash也与receipt一致。源归档没有包含build helper本体，此项明确以仍保留的helper文件hash核对，不假称它在archive中。

两库分别完成35类验证及64次暖机，exit0、Oracle0；预期行数/digest逐项匹配原manifest。SQLite实际映射本批libsqlite3 hash，PRAGMA为WAL/FULL/FK1/busy5000；PG报告18.0，有限测试结束后pg_ctl stop退出0。所有command log及原始JSON hash也已核对。此结论覆盖metadata修复候选，初次失败日志及hash继续保留。

主代理随后要求正式campaign准入，Java新增FormalAdmission/Options/Main分流，因此上述通过**不能继承给新增准入代码的下一个ELF**。新代码源审已检查真实ELF hash、manifest、provider、mixed/prepared/persistent、1800秒、SQLite C4/R3000或PG C8/R3600、queue64、warmup64和idle15的严格匹配；finite仍false、业务/Oracle失败或证据截断不给eligible。审查发现并在最终冻结前补齐了强制--verify，保留独立35case验证+64暖机。主异常/cleanup suppressed链也保留。正式候选仍须最后一次构建和双库有限回执后追加绑定结论。


## 最终正式准入候选的Java绑定结论

最终检查文件为 `java-campaign-final-binding.json`，可复现只读脚本 `review-java-campaign-final.py`。审查对象是 `clients/java/verification/native-campaign-final/` 和保留目录 `toolchains/java/campaign-final-native/`。**finalReadOnlyReviewPassed=true：可以交主代理的外部冻结、准入与串行正式runner；并不表示已经完成任何30分钟性能验收。**

| 身份 | SHA-256 |
| --- | --- |
| 最终Native ELF | `30f437c78ff6b9e1dcb16a70f97ab44eee660b07320536dd4fcd4a044402043e` |
| 最终JAR | `4ce2fa14e20467db3279fff69814b1a47ce57c7ce49fc61326a78c1e6adf52b9` |
| 最终source.tar.gz | `774150dc19326c4207d7104489c9a648409a5c5af4f21e85ebff536c6f163617` |
| 最终build identity | `ae0f2adc1808f7f047b3fc56e84738f69a177abe0da0288d23b3997022d0f5d9` |
| SQLite有限回执 | `1b98b3b2706aec0c82130da585cf9396d1761d0a1bef94483831c2d734707867` |
| PostgreSQL有限回执 | `834f0829f5fb26f6b3822c21a79ae7c3dbf973842b6c468c9b26bcf8a0539c27` |

原始构建前freeze全部输入、当前文件、归档内全部编译输入与build identity完全匹配。ELF为64位x86-64；JAR业务class major version为69（Java25），新FormalAdmission.class真实存在。9个运行依赖、Graal metadata archive、JDK release、JAR内reachability metadata及构建工具文件hash均核实。没有将metadata修复前一候选的成功继承给新ELF。构建helpers在当前文件上有独立hash核对，未声称source archive包含其本体。

最终两库各使用同一ELF完成35类验证及64次暖机，C1/prepared/persistent，业务oracle逐项与历史manifest相符，Oracle0、退出0；两份回执均VerificationOnly=true、NativeAot=true、TimingComparisonEligible=false。SQLite实际映射本批SQLite3.51.3和JNI，engine hash/PRAGMA均匹配；PG18.0于2026-11-28T08:31:22.547800Z完成stop，exit0。原始命令日志和JSON hash全部一致。

额外 `admission-rejections/receipt.json` 的三条实际负向守卫也通过只读复核：缺少准入文档、verify-only带正式准入、ApprovedForFormalMeasurement=false。三者均快速exit2，日志hash和对应准入错误信息一致；源码中守卫早于Database.open，并非用数据库连接失败冒充准入拒绝。本轮没有执行正向正式campaign分支；该分支必须由外部runner生成真实ELF/hash/参数一致的准入文件并完成1800秒、完整drain和所有失败/正确性检查后才可接受。

最终源码强制正式运行保留独立35类验证（--verify）及每worker64次暖机。有限模式继续不合并为正式结果；业务错误、Oracle失败或截断不给正式eligible，错误退出与主异常/cleanup suppressed证据链继续保留。此前首次jOOQ初始化失败、metadata修复候选成功与最终正式准入候选成功均有各自身份，未覆盖旧证据。

本次全部审查仅读取已存在文件并计算hash、解析PDB/JAR/ELF/JSON，未发起编译、客户端业务、数据库启停或正式压测。后续性能报告仍须使用本机实际八段连续30分钟回执，不能把这些有限验证作为吞吐、内存上限或跨runtime性能结论。
