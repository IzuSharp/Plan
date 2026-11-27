# pull-local07：两库普通 AOT ELF 的实际调度分支

## 结论

现有真实 PackageReference Release Native AOT 普通消费者已经证明：只有 HostPull 的默认 scheduler 对象改为 Local；共同 base constructor 的空值回退仍为原 Global。SQLite 和 PostgreSQL 均如此。没有运行查询、构建、新诊断或性能测量。本报告作者也是候选源码作者，因此这是分离保存、可独立回读的实际 ELF 分析，不冒充另一位审查者。

新增实现类型确实改变了共同 `CoordinatedCallback.Signal` 的机器码。05 的单实现路径直接清零 `esi`，调用 runtime `UnsafeQueueUserWorkItem(IThreadPoolWorkItem, false)`。07 在同一源码行内先比较 scheduler 的 EEType：等于旧 Global 类型时走 false，另一条已静态解析分支设置 `esi=1` 走 true。两条都是成熟 runtime 的直接调用，没有变为泛接口间接调用。`Signal` 两库都从 240B 增为 261B，新增类型判断由所有经过这个共同方法的调度路径承担；不能把源码没改表述为执行成本或机器码没改。

## 实际位置

| 证据 | SQLite 07 | PostgreSQL 07 |
| --- | --- | --- |
| Signal / 大小（05→07） | `0x10ae20` / 240→261B | `0x10af20` / 240→261B |
| 比较的 Global EEType | `0x6cb2b0` | `0x6ca1f0` |
| true 参数、runtime call | `0x10ae8a` / `0x10ae8f` | `0x10af8a` / `0x10af8f` |
| false 参数、runtime call | `0x10ae96` / `0x10ae98` | `0x10af96` / `0x10af98` |
| runtime UnsafeQueue 目标 | `0x192ad0` | `0x192d70` |
| HostPull constructor / 大小（05→07） | `0x11ed20` / 227→241B | `0x11ee20` / 227→241B |
| HostPull 的 Local frozen object | `0x6b7000` | `0x6b5f38` |
| base constructor 的 Global frozen object | `0x6b7018` | `0x6b5f50` |

`HostPullController` 实际先读取 TestPullScheduler，再以 `test/cmove` 选 Local 默认对象并调用共同 base constructor；注入值的优先级保留。base constructor 自己继续以 `test/cmove` 选 Global 空值回退。HostPull ctor 中 MRVTS async flag 的 `movb $1,0xc2(%rbx)` 仍存在，没有混入已拒绝的 tail06。

## 其它路径及编译器影响

每库选定 10 个很小的实际方法范围：base constructor、Signal、HostPull constructor、HostCursorClose constructor、AsyncOperation constructor、HostCommand 的 Int64/Canon/TransactionSnapshot 三个 constructor，以及 runtime UnsafeQueue 和 Enqueue。

10 个范围的原始机器码字节在 05/07 间都不同，原始 byte hash 均保存在 receipt。为了区别布局地址变化与指令形态，另把直接 call/jump/RIP 目标替换为实际 nm 符号名或本方法内部相对偏移。按这个有边界的规范，只有 Signal 与 HostPull constructor 不同，其余 8 个目标指令文本相同。该比较不声称全程序二进制等价，也不证明所有 Process/Execute 方法逐字节不变。

HostClose、HostCommand 三个实际泛型及 AsyncOperation constructor 都继续把自己的 scheduler 参数传到共同 base constructor，因此其空默认值仍选原 Global，并经新的共同 Signal 的 false 分支。即使各自 constructor 规范后形态相同，它们调用的 Signal 仍增加了共同类型判断。

`CallbackRegistration` 在两库的 05/07 普通映像中均未找到独立方法或类型符号。已知其源没有改、默认值仍传给共同 base；本报告不为该通知路径虚构实际 ELF 通过信用。不能仅凭符号未找到对所有潜在内联代码作绝对不存在断言。

## runtime 分支和观察边界

两库实际 UnsafeQueue 都以 `test preferLocal; sete forceGlobal` 将布尔值取反后传入原 Enqueue。Enqueue 的实际分支在 `!forceGlobal` 且已有 runtime thread-local queue 时调用 `WorkStealingQueue.LocalPush`，否则继续原 global/assigned-global queue 路径；两边最后保留请求 worker 的逻辑。true 是偏好，不能据此声称每次提交必在同一线程执行或绝无 stealing/global fallback。

这次检查证明变量已进入普通机器码，同时揭示其额外类型分支代价。它不计量这个代价，也不授予每次业务的新 offer 次数、跨线程比例、吞吐、分配或尾延迟收益。是否保留由 root 的最小反序普通短测决定。现有有限默认调度器正确性仍是独立契约门禁，不能从 ELF 推导公平上界。

## 原始资料

[findings.json](findings.json) 绑定两份完整 receipt、四个实际 ELF 身份及比较结果。相邻 `actual-elf-readonly-sqlite-01` 和 `actual-elf-readonly-postgresql-01` 各保存 22 条 filtered nm / bounded objdump 命令、原始输出和 stderr、20 个小方法范围的地址/字节 hash、规范后的指令文本。共 44 条命令，无全文件反汇编；读取前后 ELF/.dbg 哈希不变。捕获工具为相邻 `capture_actual_elf.py`。

SQLite07 ELF SHA256：`59b92a8f0493436ee7887c54153ce6f9c8afcf2e0c17812fc93eb462cea79a0e`。PostgreSQL07 ELF SHA256：`a07ee215e4302b5afa27c24303a66d52721359b37202e407b3ed03b34adebc5e`。
