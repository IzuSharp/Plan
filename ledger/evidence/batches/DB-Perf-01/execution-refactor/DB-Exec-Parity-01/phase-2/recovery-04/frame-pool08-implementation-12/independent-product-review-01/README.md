# frame-pool08 首个产品提交：独立源码审查

**74917fd4 的单文件产品 diff 未见阻断。** 允许继续已选有限测试的准备；本审查没有构建、运行正确性、数据库或测量，不给采用/安全实测/性能信用。root仍掌握实际build/run授权。

唯一改动为 QueryCommand.Submission.cs。原TryEncodeSingleRoot、Render、CreateCte、LockOrigins/PublishOrigins逐字节不变；Encode分配前的图遍历、全部逻辑配额、bindings和Owner算法逐字节不变。原Compile、null检查、metadata失败release、origin失败Dispose、sealed/return语句不变。

Seal局部rental初值null，外层try/finally先于LockOrigins及Encode。唯一Rent位置仍在原new byte[size]位置；Rent返回后立即赋给ref owner，下一次可能失败的frame/编码/owners.ToArray之前已经登记。只有Seal传true；fresh Encode传false，Render/CTE所用Bytes.Length因此仍等于logical size，不能被后续复用误改。

实际实现携带EncodedCommand.Length，header写size，Seal提交AsSpan(0,Length)，大桶尾部不会送native。头reserved28与块reserved20均显式写0；payload复制及dependency/origin fixup保留。descriptor仍只读record struct，不Dispose、不持久存入图。池在private nested显式cctor后，仅eligible调用触达；范围严格4096<size<=65536，不给stack路径引入池初始化。

Return同池、唯一调用点、clearArray:true，晚于原using session→gates的退出顺序，涵盖成功/Encode尾部/Compile/null/metadata/origin失败。没有shipping全局测试callback、租约heap对象、原生/公共API/调度/CI改动。私有池在冷初始化、miss、清零、锁和驻留上的已记代价仍需实际计入；新增控制流与descriptor布局不保证其它AOT机器码相同。

已读已提交diff对应的impact：linux、PostgreSQL、SQLite独立scope，两个顶层包各含pack/AOT消费/API及原有正确性；无额外run_steps。它以origin/main为基准，还包含本任务先前已保留改动，故native和历史测试同时被选中；不误称这一个文件单独导致全部选择。后续test commit/推送前仍按规则检查当时完整已提交diff。

下一步仅既定有限lifetime控制。自然postRent Owner quota异常未必可由正常公共状态触发，不能为造用例放松额度或强制OOM；如果无法简洁构造，独立local fault variant可证明该finally边界，并明确synthetic而非真实业务失败。测试若主动访问池字段，会自己触发初始化，不能把这种测试当作stack路径冷初始化未发生的实测。不得为了计数/故障新增普通shipping callback。

精确源、patch、当前impact快照与只读一致性核对见validation/receipt；当作者提交测试时仍须另外审其有效性，不能把此产品源码通过冒充测试通过。
