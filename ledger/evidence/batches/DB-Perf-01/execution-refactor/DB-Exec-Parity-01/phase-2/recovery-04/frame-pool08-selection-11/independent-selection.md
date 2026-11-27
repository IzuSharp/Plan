# Seal 最终临时帧：独立候选选择审查

**建议进入一个独立资源实验：只对 `Seal` 图编码慢路中 `4096 < logicalLength <= 65536` 的最终临时数组，使用私有 `ArrayPool<byte>.Create(65536, 4)`。** 这是待 Plan/Design 选择及有限正确性验证的方案，不是已证明安全、已获收益或已经采用的产品实现。本审查没有修改产品、构建、执行数据库、剖析或测量。基线为 integrated05 `2ea67ce1902f330679c3ebff4d6d5733be20f69c` / tree `4e3989f2ce9e0c554585aab5a8bbb656e689b18d`；tail06、pull-local07 均不叠入。所有长测继续取消。

## 为什么此范围足够小

现有 `QueryCommand.Submission.Encode` 在拓扑/额度/origin binding 准备后分配 `new byte[size]`；多个源 tape 随后复制到连续 envelope 并修正 dependency/origin ordinal。`Seal` 把这份连续内存同步借给 `Calls.Compile`，之后 metadata 和 `PublishOrigins` 只保留 managed 元数据及 native plan owner，不把 frame 字节交给异步读取器。ABI 明确输入借到同步调用返回；已核对 C++ literal cells 与 origin identity 都复制为自有 `Bytes`，`QueryCommandReplay` 在函数内完成 compile/shape/commit。[S1–S5]

因此可替换的是临时数组取得方式，不是 source tape 的所有权或图表示。保持全部 59,680 B tape copy、fixup、sidecar、同步 native replay、输入快照、origin 身份、metadata 发布顺序。保留 4096 B stack 快路、`Render`、`CreateCte`、小于等于 4096 B 的图慢路及大于 65536 B 的分配路径。不能把若干不连续源数组简单转成一个连续 frame，也不能原位改写 public clone/Combine 或已捕获图的 tape。[S1,S4,S6]

历史 capacity 报告明确把 final graph pooling 延后；其 60,504 B 数字是逻辑 60,480 B 的一次数组分配，当前本候选未运行。已采用的 branch consume/capacity 没有消除它，也没有证明它对应的 CPU 独占份额。此次不能宣称解决 text1000 的 CPU 差距。[S6,S7]

## 选择私有有界池，明确代价

已按实际 ILCompiler 包锁定 VMR `297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f`，直接取得官方 `ArrayPool.cs`、`ConfigurableArrayPool.cs`、`SharedArrayPool.cs`、`Utilities.cs`，逐文件 Git blob 身份匹配；原始字节保存在 `upstream/`，定位见 `upstream/source-links.json`。[U1–U4]

| 项目 | 锁定实现可证事实及本候选的边界 |
| --- | --- |
| 池实现 | `Create(65536,4)` 使用 ConfigurableArrayPool；13 个桶各有 4 个引用槽，实际 payload 按首次租用分配。每桶用 SpinLock；Rent 和 Return 都标记 NoInlining。它不是无同步成本的免费交换。 |
| 候选缓存范围 | 由于请求严格大于 4096 且不大于 65536，只触达 8192/16384/32768/65536 四种数组。缓存 payload 上界为 `4 × (8192+16384+32768+65536) = 491,520 B`，另有数组头、13 个桶及引用槽/运行时元数据。单独 related32 只用 64 KiB 桶，最多缓存 payload 262,144 B。上述数值是静态缓存上界，不是 RSS 或整个进程内存上界。 |
| 并发和 miss | 每桶 4 不是并发额度。可借后一个桶，仍无数组时直接分配；在途租约和被丢弃但尚未回收的数组可能超过缓存上界。高并发不能保证每次都省分配。 |
| related32 冷租用 | 60,480 B 请求落在 65,536 B 桶，数组分配按现有 x64 的 24 B 头约为 65,560 B，相对原 60,504 B 增加 5,056 B；池首次初始化还另有成本。这个计算不代替冷启动实测。 |
| 归还 | 该锁定实现对范围内数组的 `Return(clearArray:true)` 先 `Array.Clear` 整个实际数组，再尝试存回；即使桶随后已满而丢弃也清理。related32 每次多了对实际 65,536 B 的归还清理，不能只记录逻辑 60,480 B。编码时 reserved 仍必须显式写零。 |
| 驻留 | ConfigurableArrayPool 没有 Shared 的 Gen2 trimming；若私有 holder 为静态，保留数组可持续到该 holder/进程结束。不能声称 idle 后这些字节必然释放，更不能用分配率代替 RSS。 |
| Shared 对照 | Shared 的 TLS 命中可减少锁，但有每线程缓存、每核分区、相关初始化及 Gen2 trimming；当前未测此调用的 TLS 命中/速度，也不能给本候选同样局部固定缓存界限。它有可能更快，但没有充分证据把它同本实验一起引入。 |

优先私有池是为了限制本资源实验的保留范围和跨业务干扰，不是认定它一定更快。私有 pool holder 应仅在首次 eligible 慢路租用时初始化；不应在 `QueryCommand` 普通静态初始化中加入池构造，让原 stack 快路也承担冷初始化。不要每次创建 pool，也不要为每次租用新建 heap lease 对象。新增池实现及分支可能改变 Native AOT 的代码布局/去虚拟化，普通候选总成本必须整体测量，不能因为其它源码没改就声称机器码不变。[U1–U4]

## 不可放松的 ownership / error 条件

1. `Seal` 是唯一租约 owner。建议局部 `byte[]? rental = null`，在进入可能 Rent 的 Encode 前就建立覆盖整个 Seal 的 `try/finally`。租到的数组先赋给该 owner，再执行任何可能抛错的编码尾部或 sidecar 收尾。`EncodedCommand` 可复制，只是借用 descriptor，不能实现 Dispose、参与归还或把池数组暴露到 QueryCommand 的持久状态。
2. 原 size/深度/记录数/owner/MaxEnvelope 校验及异常顺序不变，Rent 必须在原 `new byte[size]` 的位置。不可提前租用掩盖先发生的参数/额度错误；池容量不是逻辑额度，pool miss 也不是业务拒绝条件。
3. 显式记录 logicalLength。header offset 8、固定的 command span 和 `NwBytesViewV1.Length` 都只含该长度；任何 oversized 尾部不能提交。header reserved 28–31、每 block reserved 20–23 必须显式初始化。其它字段必须沿原路径完全覆盖，保留 source tape payload 和全部 fixup。
4. 同步 Compile 仍在 fixed 保护内完成；不能在 native 仍借用、metadata/origin 旧流程未结束时归还。成功、Encode 后半失败、Compile status 失败、成功但 null result、metadata/origin 失败均恰好归还一次；原错误仍可见，native owner 原清理顺序不改。
5. 最终 `Return` 使用同一个私有池且 `clearArray:true`。返回后旧 frame 不再读写；不能用 catch 吞掉 pool 错误来掩盖双还/错误数组。若受控测试池故意违反契约，其结论仅限测试边界，不推广为真实业务行为。

这些条件由现有源码结构支持，但本次仍是静态判断。尤其 metadata/origin 正常状态的失败多为分配/owner 异常，不能为了得到绿色测试新增 shipping 可变 callback 或发明新的用户可触发错误语义。[S1–S5]

## 最小有意义的验证范围

使用现有 CommandOnly 的真实完整 envelope/sidecar 捕获和双 provider native decoder；复用其 snapshots/额度/CTE/私有 consume 回归。不新增泛化的大矩阵。

| 控制 | 必须辨别的现象 |
| --- | --- |
| 正常与边界 | `4096/4097/65536/65537` 的 actual frame、一个小 shared graph，以及 Render/CTE。只 eligible Seal Rent；dirty oversized array 的 header/每 block reserved、完整 bytes、sidecar、logical view、SQL/参数次序与原 fresh 路径一致。原 quota 失败仍在 Rent/Compile 前。 |
| Encode 获租后失败 | 用窄的确定性测试手段在分配点后、Encode 返回前失败；Return 同一数组一次，Compile 零次，原异常顺序/字段不变。若仅人为故障注入，明确它验证 cleanup，而非真实公共输入契约。 |
| Compile error 与 null | unmanaged stub 必须返回合法 status/error 或 status OK + null，不能从 UnmanagedCallersOnly 跨 ABI 抛 managed exception。分别验证原 BindingFailure 字段、Return 一次、原生 owner 没有泄漏或新误释放。 |
| metadata / origin 收尾失败 | 在独立测试构建中定位到两条 post-compile 分支，证明原 plan 清理与 rental finally 同时覆盖。不得靠真正耗尽内存，不增加普通包的全局可变故障回调；不可把 synthetic 故障覆盖写成产品正常运行失败。 |
| held borrow | 在真实 Compile 动态范围内持有第一份数组，独立第二次提交必须使用不同在途 buffer；释放前第一份 bytes 和 owners 不变，释放后才归还。可在同一有限控制中验证超过缓存槽仍可取得独立租约，不另加吞吐/公平性测试。 |
| poison / re-rent | Return 后立即 poison 或取得同一 buffer 再覆盖；此前编译的真实 plan 仍执行得到相同 literal、参数和 origin 结果。仅比较 SQL 字符串不足以发现 literal storage 的错误借用。 |
| 公共快照与现有 relation | 保留 public Combine 后源可修改/释放而已捕获图不变；复用 parent 1/2/32、重复位置、empty、变宽 key、mapper/cancel/owner 用例。Render/CTE 不租用，但仍作为 fresh 编码及 origin 捕获对照。 |

必要失败控制可共享一套 pool 计数与 compile 包装器，不以增加十几种业务场景取代真实 lifetime 证据。不可把本次只读审查写成这些控制已经执行。

## 因果验收与拒绝条件

机制证据应同时计数成功业务、Rent/Return、实际 rental length、pool miss/新增数组、冷初始化、全部清理字节；保留原 tape copy 59,680 B 不变的事实。目标是在稳态消除该一次 60,504 B 分配，理论约占原 516.1 KB/业务的 11.7%；只有净 process 分配也重复下降，才可给予资源收益信用。不要把 pool/清理放到 scope 外漏记，也不要从每请求租用次数推断 CPU 时间。[S6,S7,U2]

若机制成立，再按 root 已选的一次双库 related32 反序短 A/B 检查净分配、客户端 CPU、服务尾延迟和释放后 RSS；保留 cold/warm 区别及池静态驻留。无需为此重开 text1000/coordinator/spin，或恢复长测。是否需要一次有限并发短混合只由该候选的实际竞争/驻留风险与既有 gate 决定，不能先把未执行 mixed 写成验收义务。

以下任一项应拒绝或收窄候选：逻辑长度/dirty reserved 错误；双还或借用期间早还；public snapshot、原生借用、错误顺序或 quota 被改变；依赖新的普通热路径故障回调；分配收益不重复或转移为其它同量分配；已观测 CPU/p99/RSS 回退超过该资源收益能够合理支持的范围。仅有较少 B/op 不等于整体对齐，也不承诺全框架 0 B。

## 精确来源

- S1：`worktrees/Korda/src/Query.Binding/QueryCommand.Submission.cs`，Encode / Seal / Render / CreateCte / PublishOrigins。
- S2：`worktrees/Korda/src/Query.Binding/QueryCommandCalls.cs`，同步借用 ABI 与 RetainedQueryOwner。
- S3：`worktrees/Korda/src/Query.Binding/QueryCommandMetadata.cs`、`QueryCommand.cs`，origin/Metadata/ValidateSeal。
- S4：`worktrees/Korda/native/database/binding/query-command-v1.md` 与 `native/cpp/src/query.cpp`，frame、decode_values、origin_scope、compile_query_command。
- S5：`worktrees/Korda/src/Query.Fluent/QueryContext.cs`，先 Seal 后异步执行。
- S6：`experiments/relation-final-frame-readonly-08/README.md` / readback.json，作者身份与历史去重范围。
- S7：`experiments/relations-recovery-04/capacity-results.md`、README.md，既有资源计数与延期项，不使用其旧 native CPU 绝对值拼接当前 05。
- U1：[锁定 ArrayPool.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Buffers/ArrayPool.cs)。
- U2：[锁定 ConfigurableArrayPool.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Buffers/ConfigurableArrayPool.cs)。
- U3：[锁定 SharedArrayPool.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Buffers/SharedArrayPool.cs)。
- U4：[锁定 Utilities.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Buffers/Utilities.cs)。

精确来源及本报告字节身份见 receipt.json。本审查提供选择与风险边界，不授予实现、安全实测、普通计时或 parity 信用。
