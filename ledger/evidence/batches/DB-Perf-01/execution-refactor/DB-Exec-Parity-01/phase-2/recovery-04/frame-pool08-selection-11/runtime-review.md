# Seal final-frame rental08：锁定 ArrayPool 实现核查

只读结论，未修改产品、构建或运行任何 workload/诊断。拟议范围为 `Seal` 慢路且 `4096 < logicalSize <= 65536`；原 stack、Render、CreateCte、tape copy 保持。本报告不授予普通性能信用，实施仍等待 root 的 Plan/Design 决定与明确授权。

## 精确来源

沿现有 `runtime.linux-x64.Microsoft.DotNet.ILCompiler/11.0.0` 身份读取官方 `dotnet/dotnet` VMR **297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f**；其 manifest 对应 runtime **deae2e32bf0e018e09d64597b7c59b62b73bb3ce**。旧本地 source 集合仅含 Threading 等已读子集，未含 Buffers，所以本次从该精确 VMR 补读以下四文件，没有使用 main。

- [ArrayPool.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Buffers/ArrayPool.cs)
- [ConfigurableArrayPool.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Buffers/ConfigurableArrayPool.cs)
- [SharedArrayPool.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Buffers/SharedArrayPool.cs)
- [Utilities.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Buffers/Utilities.cs)

与独立审查者分别读取的结果一致。为避免重复存储，本报告复用其已封存的 `experiments/relation-final-frame-independent-review-08/upstream/` 四份 raw，已独立计算 Git blob SHA 并逐一匹配本次官方响应；源链接/哈希、现有 pin 身份和本报告绑定见 `readback.json`。

## Create(65536, 4) 的实际含义

`ArrayPool<byte>.Create(maxArrayLength: 65536, maxArraysPerBucket: 4)` 返回 `ConfigurableArrayPool<byte>`。构造器按 `Utilities.SelectBucketIndex` 建立 13 个桶，数组长度分别为 16、32、…、65536。每桶有 4 个数组引用槽，payload 在需要时分配，构造时不预分配 52 份 byte buffer。[ConfigurableArrayPool 构造器、Bucket 构造器；Utilities]

| 范围 | 可缓存数组数上限 | 缓存 payload 上限（由源码推导，非 RSS 实测） |
| --- | ---: | ---: |
| 整个配置池的所有 13 桶 | 52 | `4 × (16 + … + 65536) = 524,224 B` |
| 本候选仅允许 4097–65536 的使用方式 | 16 | `4 × (8192 + 16384 + 32768 + 65536) = 491,520 B`，即 480 KiB |
| 当前 related32 的 60,480 B 帧，仅命中最大桶 | 4 | `4 × 65536 = 262,144 B`，即 256 KiB |

这些值只界定**每一个池实例保留的数组 payload**，不含数组/桶/引用表对象开销，更不是进程 RSS 或活跃租用的上限。须使用单一专用池；每 query/session 新建池会成倍增加这些上限。

`Rent` 先尝试对应桶，耗尽则最多再尝试相邻的一个更大桶；两次均失败便新建目标桶尺寸的数组。因此 8192 桶耗尽可借到 16384 B，不能假设实际数组长等于 round-up 后的最小桶。最大 65536 桶耗尽后直接 `new byte[65536]`。并发租用数量不被 4 限流，也没有等待 buffer 归还的队列。超过最大值的 Rent 会精确分配请求长度，Return 时不缓存；拟议产品范围应在调用池前明确排除这种情况。[ConfigurableArrayPool.Rent]

## 锁、清零、释放与错误边界

- **线程安全来自每桶 SpinLock。** Rent/Return 在锁下操作 index 与 buffer 引用；新建 byte 数组放在锁外。跨线程归还受支持。同一个 bucket 的并发调用仍可竞争，不等于无等待或无 CPU 成本。
- **Return(clearArray:true) 清整个实际数组。** 对池范围内数组，先 `Array.Clear(array)`，再进入 Bucket.Return。即使该返回最终因桶满被丢弃，也已清零。related32 因而每次归还明确清 65,536 B；不是 60,480 B 的逻辑帧长度。
- **没有配置池自动 trim 路径。** 放入槽的数组由池持有；单一静态池在空闲后仍可保留这些数组。不能把“owner/连接已归还”写成该池缓存也释放，释放后 RSS 必须保留这项观察。
- **它不验证线性 ownership。** API 要求同一 rental 只归还一次、归还后不得再读写。错误大小会被拒绝，但重复归还正确大小数组并不由此获得安全保证。唯一 Seal 租约必须由产品负责。
- 对 byte 的冷分配，Configurable 使用 `new T[bucketLength]`。当前帧从 60,480 B payload 变成 65,536 B payload，多 5,056 B；新对象和首次池初始化仍计入 cold 成本。

以上均为锁定实现事实；没有运行 contention 或 allocation 测试。[ConfigurableArrayPool.Rent/Return、Bucket.Rent/Return；ArrayPool.Return 合同]

## 与 Shared 的最小取舍

| 维度 | 专用 Create(65536, 4) | 锁定 Shared |
| --- | --- | --- |
| 快路径 | 每个 Rent/Return 都经过桶 SpinLock；无 TLS 命中路径 | 每线程每桶可保留 1 个数组；TLS 命中不进入 partition lock |
| 额外缓存 | 每桶 4 个，独立于线程/核数 | TLS 加 per-core partitions；默认每 partition、每 size 32 个。partition 数默认 `Environment.ProcessorCount`，可由已有环境配置限制 |
| 回收策略 | 无自动 trim，缓存上限固定 | gen2 回调按压力/时间 trim TLS 和 partitions；不能保证某个业务释放后立即清空 |
| 耗尽时 | 至多尝试目标/下一桶，再 new 目标桶大小 | 对应 size 的 TLS/partitions 失配后分配该 size；byte 可走 AllocateUninitializedArray |
| 本候选的解释范围 | 可以单独界定 Korda frame 缓存的最大 payload | 与进程其他 byte[] Shared 消费混用，不能把全池 retention 归给本候选 |

选择专用池的理由应是**小而明确的额外缓存边界，以及不需要自制锁/自制 buffer pool**，不能宣称它比 Shared 更快。它可能比 Shared 的 TLS 命中更贵，而且不自动 trim。实际 AOT 调用形态与稳态 CPU/尾延迟仍须后续候选验证；本文没有编译、没有机器码或性能结论。

Shared 对最大 bucket 的缓存规模可用 `(线程 TLS 数 + 32 × partition 数) × 65536` 理解，但本报告没有测当前进程线程数、ProcessorCount 或环境覆盖值，因此不报假定的实际驻留数字。专用池也不消除其他组件原有 Shared 使用或基类静态设施。[SharedArrayPool.Rent/Return/Trim、SharedArrayPoolPartitions、SharedArrayPoolStatics]

## 对拟议 Seal 租约的具体要求

1. 私有池应在**首次 eligible 慢路**才初始化；不要直接在 QueryCommand 的普通静态初始化中创建它，使原 4096 B stack 请求也承担冷初始化。采用明确按需 holder 或等价机制，并在实际源码审查中验证；本文不假定某个未构建写法的 AOT 行为。
2. 唯一词法 finally 从 Rent 调用所在的 try 起保护，局部 rental 未成功赋值时不 Return；成功后包括 Encode 内部失败都必须归还。EncodedCommand 只作为 descriptor，携带明确 logical length，不自行拥有/归还可复制租约。
3. frame view、wire header 总长只用 logical length。reserved bytes 必须显式初始化，不能把池“通常已清零”当编码合同。原编码只留下总头与各 block 的 reserved word，已写数据仍完整覆盖；是否只清这些字段或清全部 logical frame，应在设计中固定并计入字节成本。
4. 归还使用 `clearArray:true`，不改 runtime knob。正常或任何失败都只归还一次，且晚于同步 native 借用结束。metadata/origin 异常注入只能作为测试 cleanup 的工具，不引入 shipping mutable callback 或新业务失败语义。

当前建议与 root 拟定的 Seal-only、有界范围、完整 copy、唯一租约方向一致。它支持进入明确的候选设计决定，不代表候选已被接受，更不能预先把目标 60,504 B 当作实测节省。所有新 build/run 仍未授权执行。
