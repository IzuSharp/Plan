# 独立审查：先完成 metadata，再采用 native owner

**69b2383 的两个修正没有源码层面的阻断，可作为 frame-pool08 的共同前置正确性修复。** 本审查只读实际提交和现有 impact，不构建、不执行故障控制，也不把源码论证写成运行验证。

## 精确范围

基线为 integrated05 `2ea67ce1902f330679c3ebff4d6d5733be20f69c`；候选 `69b2383dadc280f1a81de592592a1442069eed0c`，tree `f7660759bba43ae83324620e2fb731efd479c3b5`。只有 `QueryCommand.Submission.cs` 两段改动：Seal 先调用 Metadata，再构造并初始化 DatabaseOwner；CreateCte 先完成整个 QueryCteMetadata（包括 Metadata），再构造并初始化 DatabaseOwner。精确替换后，其余源字节与基线相同。

`DatabaseOwner` 的 SetHandle 仍是构造函数最后一步。前面的失败留下 invalid handle；之后的 QueryPlan/QueryCte 仍为自动 init 引用赋值，没有新增可分配工作。metadata 分配失败时，尚无带有效 handle 的 wrapper，原 raw catch 是唯一释放者。构造成功后，现有 PublishOrigins 失败由 wrapper.Dispose 清理。继承风险及锁定 SafeHandle/native registry 证据保存在相邻 inherited-owner-failure-review-01，原始报告不变。

Native Compile/Cte 调用、status/null 检查、业务验证、PublishOrigins 的相对顺序保持；只有内部 metadata 与 managed wrapper 分配/构造的顺序改变。尤其不能声称 OOM 的分配顺序完全不变。这个显式变化使异常时所有权单一，属于独立正确性修正，不属于池化收益。

## 门禁与后续边界

18 项有限源码/身份/impact 检查通过。已提交 diff 的 impact 选择 linux 共用检查以及 SQLite、PostgreSQL 各自独立的 package/API/correctness/AOT 检查；run_steps 为空。列表中的历史 native 等原因来自本任务相对 origin/main 的累计差异，本次修复没有 native 或 CI 编辑。本审查没有重新运行 impact、CI 或测试。

有意义的运行控制仍是：在真正 metadata 求值位置保留旧路径故障负控；修正后验证原异常、对应 native handle 恰好一次 release、有限 finalizer 控制以及后续 owner 可用。Seal/CTE 各一条即可；实际地址复用无需为此强制制造。shipping 产品不加入可变 fault hook，独立本地故障构建保持单独身份。frame rental 的 exactly-once Return 与 native owner release 分开计数。

后续池化 A/B 的 baseline 与 candidate 必须都包含相同 cleanup 修复。原05的历史身份和测量保留，不能把 cleanup→pool 与旧05→新组合混为同一因果比较。本次代码审查不授予 build/run 或性能信用。
