# Satori cgroup 感知路径：锁定源码核验

本次只读审查对应 `PublishWithSatoriGC 11.0.2-satori.45942668844.1`、发布标记
`20261127.1-net11.0`，源码锁定 commit
`bd2e3f834043b4bb68d5ef2255029dae36ab5e0e`。未修改 EF 冻结源码，未执行新的运行时实验或压测。
四个实际读取的源码文件 SHA-256、19 处行范围和逐项结论保存在
`satori-cgroup-source.json`。

**源码确认 Satori 会读取 Linux cgroup 的可见内存上限，并把它用于 GC 的可用内存和分配预算计算。
这支持在可配置 cgroup 的主机上继续验证；它不证明 Satori / EF 已能在 128 MiB 内完成业务或稳定长跑。**

## 已核实的调用链

| 环节 | 锁定源码依据 | 实际行为 |
| --- | --- | --- |
| GC 初始化 | [gcenv.unix.cpp:184–226](https://github.com/hez2010/Satori/blob/bd2e3f834043b4bb68d5ef2255029dae36ab5e0e/src/coreclr/gc/unix/gcenv.unix.cpp#L184-L226)、[cgroup.cpp:54–84](https://github.com/hez2010/Satori/blob/bd2e3f834043b4bb68d5ef2255029dae36ab5e0e/src/coreclr/gc/unix/cgroup.cpp#L54-L84) | 调用 `InitializeCGroup`，发现并缓存 cgroup 版本、进程所在组路径及可见挂载根。 |
| 找到进程所属组 | [cgroup.cpp:141–195](https://github.com/hez2010/Satori/blob/bd2e3f834043b4bb68d5ef2255029dae36ab5e0e/src/coreclr/gc/unix/cgroup.cpp#L141-L195)、[291–356](https://github.com/hez2010/Satori/blob/bd2e3f834043b4bb68d5ef2255029dae36ab5e0e/src/coreclr/gc/unix/cgroup.cpp#L291-L356) | 结合挂载信息与 `/proc/self/cgroup`，v2 解析 `0::` 后面的路径。 |
| cgroup v2 上限及祖先 | [cgroup.cpp:448–503](https://github.com/hez2010/Satori/blob/bd2e3f834043b4bb68d5ef2255029dae36ab5e0e/src/coreclr/gc/unix/cgroup.cpp#L448-L503) | 从缓存的当前组开始，逐级读取 `memory.max`，一直到可见挂载根（包含该层），取可读数值中的最小值。不会越过可见挂载根去读取隐藏祖先。 |
| 返回有效物理内存限制 | [cgroup.cpp:566–611](https://github.com/hez2010/Satori/blob/bd2e3f834043b4bb68d5ef2255029dae36ab5e0e/src/coreclr/gc/unix/cgroup.cpp#L566-L611)、[gcenv.unix.cpp:1196–1219](https://github.com/hez2010/Satori/blob/bd2e3f834043b4bb68d5ef2255029dae36ab5e0e/src/coreclr/gc/unix/gcenv.unix.cpp#L1196-L1219) | 发现有效限制则返回该值并标记受限，否则回退到主机物理内存。限制还受物理内存及 `RLIMIT_AS` 的最小值约束；这不意味着应使用 `RLIMIT_AS` 替代内存控制器。 |
| Satori 启动时状态 | [SatoriGC.cpp:334–360](https://github.com/hez2010/Satori/blob/bd2e3f834043b4bb68d5ef2255029dae36ab5e0e/src/coreclr/gc/satori/SatoriGC.cpp#L334-L360)、[786–801](https://github.com/hez2010/Satori/blob/bd2e3f834043b4bb68d5ef2255029dae36ab5e0e/src/coreclr/gc/satori/SatoriGC.cpp#L786-L801) | 初始化缓存 `g_totalPhysicalMem`；公开的 `TotalAvailableMemoryBytes` 由这个缓存值提供。 |
| 可用量及 GC 预算 | [SatoriRecycler.cpp:1454–1482](https://github.com/hez2010/Satori/blob/bd2e3f834043b4bb68d5ef2255029dae36ab5e0e/src/coreclr/gc/satori/SatoriRecycler.cpp#L1454-L1482)、[1555–1561](https://github.com/hez2010/Satori/blob/bd2e3f834043b4bb68d5ef2255029dae36ab5e0e/src/coreclr/gc/satori/SatoriRecycler.cpp#L1555-L1561) | 重新读取 OS 限制，结合主机与受限可用量，扣除至少总量 5% 的预留；`AdjustHeuristics` 再用可用量限制 Gen1 分配预算。 |

数值读取器遇到 `memory.max` 中的 `max` 不会把它当作有限值，因此仍能使用更上层可读的有限限制，见
[gcenv.unix.cpp:722–767](https://github.com/hez2010/Satori/blob/bd2e3f834043b4bb68d5ef2255029dae36ab5e0e/src/coreclr/gc/unix/gcenv.unix.cpp#L722-L767)。
GC 使用的 cgroup v2 已用量是当前缓存组的 `memory.current` 减去 `memory.stat` 的 `inactive_file`，不是进程 RSS；
其可用量按 `max(limit - used, 0)` 计算，见
[cgroup.cpp:506–547](https://github.com/hez2010/Satori/blob/bd2e3f834043b4bb68d5ef2255029dae36ab5e0e/src/coreclr/gc/unix/cgroup.cpp#L506-L547) 和
[gcenv.unix.cpp:1346–1368](https://github.com/hez2010/Satori/blob/bd2e3f834043b4bb68d5ef2255029dae36ab5e0e/src/coreclr/gc/unix/gcenv.unix.cpp#L1346-L1368)。
因此，读取到了祖先的较小上限，也不能据此认为它完整掌握了该祖先下其他兄弟组的占用余量。

## 应先入组再 exec，不能把事后迁移当作等价条件

根据上述缓存初始化路径，应先创建并配置客户端专用组，让启动器进入该组后再 `exec` 客户端，使 CoreCLR / Satori 初始化时看到目标组。
这段启动顺序是从源码得出的执行建议，尚未在当前环境验证。

运行后才把 PID 迁入另一个组有额外差异：这些源码没有在每次查询时重新解析 `/proc/self/cgroup`；后续读取仍使用已缓存的组路径。
`SatoriGC::RefreshMemoryLimit` 在本锁定版本仅返回 0，没有刷新组路径或启动缓存，见
[SatoriGC.cpp:942–945](https://github.com/hez2010/Satori/blob/bd2e3f834043b4bb68d5ef2255029dae36ab5e0e/src/coreclr/gc/satori/SatoriGC.cpp#L942-L945)。

需要区分“迁到不同组”和“修改已缓存组的上限”：后者可能被 Recycler 后续的文件重读看到，但公开的 `TotalAvailableMemoryBytes` 仍取启动缓存。
这些事实不能升级为已验证的动态限额或运行中迁移支持。内核内存 charge 迁移、控制器强制执行及 `memory.max` 与 RSS 的区别，另见 `cgroup-execution-plan.md`。

## 当前环境及尚未证明的部分

当前环境观察记录在 `cgroup-environment.json`：没有可见的 cgroup 挂载及 `/sys/fs/cgroup` 目录。
锁定代码会对该目录执行 `statfs`；失败时 cgroup 版本返回 0，见
[cgroup.cpp:108–126](https://github.com/hez2010/Satori/blob/bd2e3f834043b4bb68d5ef2255029dae36ab5e0e/src/coreclr/gc/unix/cgroup.cpp#L108-L126)。
仅有 `/proc/self/cgroup` 的 `0::/` 记录不足以让这条发现路径生效。

本次证据只确认源码的发现、预算和缓存行为。128 MiB 下能否启动 EF、是否发生 cgroup OOM、正确性和持续吞吐都尚未实测。
没有把内核限制描述为 RSS 每个瞬间严格逐字节不越界，也没有把 GC 感知限制等同于业务能在该限制下成功运行。
