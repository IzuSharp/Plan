# related32 最终帧：只读所有权核查

状态：仅提出一个可证伪的资源假设；未选择产品方案，未修改产品、构建或运行诊断/计时。基线为 integrated05 `2ea67ce1902f330679c3ebff4d6d5733be20f69c`，tree `4e3989f2ce9e0c554585aab5a8bbb656e689b18d`。tail06、pull-local07 已拒绝，不能把它们作为本建议的基线。本轮所有长测已由用户取消。

## 结论

**值得提交决定的单一资源假设是：有界复用 `QueryCommand.Seal` 图编码慢路径的最终临时帧，保留现有完整编码、复制与同步 native compile。** 当前这份数组每个 related32 业务实测分配 60,504 B，其中逻辑帧为 60,480 B。它在 managed 侧有明确的同步借用结束点，可以设计一个不逃逸、仅一处负责归还的租约。收益尚未测量；冷分配、归还清零、跨线程池命中、驻留与竞争成本都可能抵消收益。[E1, S1–S4]

**不建议把现有 tapes 直接“转移”给最终图作为同一个小改动。** 现有 59,680 B tape copy 不是又一次私有 branch clone：它将多个独立数组组成精确、连续的 NWQC envelope，并在目标帧中重写全图 dependency 与 origin 索引。即使 related32 的临时 branch 已被消费，唯一 caller 也不能让 32 个数组变成一块连续内存。通用路径还容纳 public Combine、clone、共享 origin 与先前 plan/CTE capture。当前引用模型不能直接授予对这些源 tapes 的原位重写权。[S1, S5–S8]

## 实际数据流与所有权

| 位置（均相对 `worktrees/Korda`） | 已读取的事实 | 对候选的约束 |
| --- | --- | --- |
| `src/Orm.Relations/RelationBatch.cs`，`LoadRelatedAsync` 26–61 | 每次先复制 parent key 集合；每个 branch 独立 `From`。后续私有 branch 经 `CombineConsumed` 接到首 branch；最终调用 `ToListAsync`。 | 保留输入快照、重复父位置、mapper 与序号投影；不增加形状/计划缓存。 |
| `src/Query.Binding/QueryBinding.cs`，`SnapshotAndImport` 162–172、`ConsumeAndImport` 175–191 | 公共路径克隆 source 后保留图；私有路径在双方 admission 下先成功 retain/import，再标记 source 已消费。 | 私有 clone 消除已在 recovery03 采用，不能重新计为本次收益；公共 source 必须继续独立可修改。 |
| `src/Query.Binding/QueryCommand.cs`，`SnapshotAndImport` 368–389 | dependency retain 源图，不再次复制 tape；append/metadata/额度失败会回滚引用。 | 最终编码不能提前消费共享 graph、修改 source tape 或改变原失败顺序。 |
| `src/Query.Binding/QueryCommand.Submission.cs`，`Encode` 34–103 | 先拓扑遍历/额度检查、建立 origins/bindings，然后第 76 行分配 `new byte[size]`；第 91 行复制每个 tape，第 92–99 行在目标帧做 fixup。 | 可瞄准第 76 行分配；复制与 fixup 保留。不能把池容量当逻辑帧长。 |
| 同文件，`Seal` 105–133 | `ValidateSeal`、origin gates、4096 B stack 快路保持；慢路帧在 `fixed` 区间同步传给 `Calls.Compile`，然后构造 metadata、发布 origins。 | 租约可覆盖整个 `Seal`，只在所有使用结束后归还；不进入异步 reader/mapper 生命周期。 |
| 同文件，`PublishOrigins` 194–207 | 发布只读取 `encoded.Origins`，并持有 native plan owner；不读 `encoded.Bytes`。 | frame 字节不是原生 plan owner 或后续 origin 身份的存储。 |
| `src/Query.Binding/QueryCommandCalls.cs` 6–8、`native/database/binding/query-command-v1.md` 10–15 | 明确所有输入只借到同步调用返回；C++ 在返回 immutable plan 前重放并编译完整命令。 | 这是复用临时 frame 的 ABI 基础；不能改为异步持有 managed bytes。 |
| `native/cpp/src/query.cpp`，`decode_values` 749–780、`NativeQuery::value` 1039–1053、`origin_scope` 2893–2915 | decoded cells 构造自有 `Bytes`；slot 保留这些 owned cells；新 origin identity 复制到自有 `Bytes`。 | 实际核查的 literal/origin 路径不会在返回后借用 managed frame；仍须用 poisoned-buffer 实际回归覆盖。 |
| 同文件，`compile_query_command` 2933–2943 | `QueryCommandReplay` 为函数局部；完成 replay、`compiled_shape` 和 registry commit 后才返回 plan。 | 当前借用周期同步有界；不是可直接移交 `byte[]` 所有权的 native ABI。 |
| `src/Query.Fluent/QueryContext.cs`，`Stream` 186–209 | Seal/PublishPlan 同步完成，然后才构造会异步打开 stream 的 lambda。 | 保留本次 schema/plan 编译与 mapper 绑定，不缓存 DDL 敏感计划，不改异步阶段。 |

## 唯一建议的最小范围

只研究 `Seal` 的慢路临时 frame：保留单 root 的 4096 B stack 快路；超出选定有界租用范围时仍走当前分配。`Render` 的可继续修改语义与 `CreateCte` 路径初次可以维持现状。是否使用现成 `ArrayPool<byte>`、具体容量上限和清零策略，需在 Plan/Design 选择后固定，本文没有实施授权。

现有 fresh `byte[]` 不逃逸出编码/提交方法，适合显式租约；**现有 `EncodedCommand` 并非线性所有权类型**。它是可复制的 readonly record struct（同文件 224 行），`Seal` 的 pattern matching 也会复制它。因此不能只给该 struct 加 `Dispose`，再依赖多个副本各自“负责归还”。必须让唯一词法 owner 持有 rental，其他编码结果只借用 span/metadata；异常时也只归还一次。

保持以下边界是必要条件：

1. 继续在原位置计算 logical size、验证节点/深度/总帧/owner 额度。不得用实际池容量提前允许原本非法请求，或把新的投机缓冲租用提前到原校验前。
2. wire header 第 8 字节与传给 native 的 view 都使用 logical size。当前 `bytes.Length` 恰好正确；换成 oversized rental 后必须显式切片。总头的 reserved 28–31 字节、每个 block 的 reserved 20–23 字节必须为零，不能依赖脏 rental 的初始内容。
3. 不修改 source tapes。保留全部 dependency/origin fixup、sidecar、metadata 与 origin publication 顺序；不得替换 input snapshot、public Combine、mapper identity 或本次 DDL/plan 校验。
4. 从获得 rental 开始，Encode 内部 `Owner`/数组收尾可能抛错，不能只在 Encode 成功返回后才建立 finally。Compile 失败/null result、metadata 构造失败、origin 发布失败、正常成功都须归还一次，且不能在 native 同步借用中或 origin 所需 metadata 消费前失效。

## 最小必要验证，待决定后才执行

先使用既有 `CommandOnlyTests` 的完整 envelope/sidecar 捕获：私有 stack 边界、共享 clone、captured origins、public Combine、private consume、额度失败后原 source 可用。这些当前测试分别在该文件 205–255、283 起、363–464 等区间；不需要重建全部性能矩阵。

新增辨别力应集中在新的 lifetime：脏且 oversized rental 下完整字节/sidecar 与现状相同；每个成功/失败路径租用归还恰好一次；在 native Compile 被真正持有时，第二个独立提交不能复用第一份正在借用的 buffer；返回后立即 poison/re-rent，原计划再执行仍保留原值和 origin。公共 source 在 Combine 后修改、执行、释放仍不改变已捕获图。使用现有 relation parent 1/2/32、重复位置、empty、不同 key 宽度、mapper/cancel/owner 回归核查实际选定实现；这些不是新 API 或新的排序保证。[S9, S10]

若这些成立，最小后续机制问题只是“该一次 60,504 B 分配是否在稳态消失、是否转移为别处分配/驻留”，不需要再诊断 coordinator 或 runtime spin。随后才用原 related32 同 SQL/DTO 的双库反序短 A/B 检查进程分配、CPU、尾延迟与释放后 RSS。只用资源收益和实际回退决定去留；不预排长测或广泛新场景。

## 能减少什么，仍不知道什么

60,504 B 约占当前 516.1 KB/业务的 11.7%；这是理想消除该数组分配的上限参照，不是候选预测值。Cold rent、租约对象、池 miss 与实际桶容量仍可能分配。清零和保留数组可能增加 CPU/复制字节/RSS；必须如实记录，不能把租用写成零成本。

本假设**不减少**已观测的 59,680 B tape copy，也不减少 From 51,712 B、EmitShape/EmitNode、native replay 或异步调度。它不能解释、保证缩小或抹去 text1000 的 6–10 倍 CPU 差距。直接 tape transfer 是否存在更大且安全的表示重构，目前仍未知；当前证据不足以把它选成小候选。

## 历史去重与来源

`experiments/relations-recovery-04/README.md` 148–152 已明确把 ArrayPool final graph frame 列为独立延期项；`capacity-results.md` 113 说明未捆绑该方案。已做 capacity 实验只改变后续匹配宽度私有 branch 的预留容量；已做 recovery03 consume 消除的是私有 branch clone。独立审查者也确认自己未试验/否决 final Freeze/SnapshotAndConsume 的所有权转移。

本次对 Plan 的 `DB-Perf-01/execution-refactor` markdown 做了有界关键词检索（GraphFrame/GraphTape/graph.frame/ArrayPool/pooled command/frame/freeze transfer/tape transfer），只找到上述 final frame 归因和延期条目；没有发现已运行或已拒绝的同一 final-frame rental 实验。这个结论是已读历史的边界，不是对所有丢失历史的存在性证明。

- E1：`experiments/relations-recovery-04/capacity-results.md`，尤其 35–50、60–63、111–113：scope 数字和普通分配，不将旧 native 身份下 CPU 绝对值拼接到当前 05。
- E2：`experiments/recovery/remaining-space-review-07/README.md`：当前剩余资源目标与解释边界。
- S1：`src/Query.Binding/QueryCommand.Submission.cs`。
- S2：`src/Query.Binding/QueryCommandCalls.cs`。
- S3：`native/database/binding/query-command-v1.md`。
- S4：`native/cpp/src/query.cpp`。
- S5：`src/Query.Binding/QueryBinding.cs`。
- S6：`src/Query.Binding/QueryCommand.cs`。
- S7：`src/Query.Fluent/Terminals.cs`。
- S8：`src/Query.Binding/QueryCommandMetadata.cs`。
- S9：`tests/Query.Binding/CommandOnlyTests.cs`。
- S10：`tests/Orm.Relations/FluentExperience.cs`。

精确输入与本报告 SHA 见 `readback.json`；它仅绑定本次只读结论，没有普通计时、机制运行或安全实测信用。
