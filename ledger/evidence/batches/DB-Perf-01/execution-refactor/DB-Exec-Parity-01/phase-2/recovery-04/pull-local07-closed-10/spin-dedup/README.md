# 既有 runtime spin 敏感性去重建议

**结论：已经做过，而且是双库、双框架、两轮反序的真实同 ELF 控制。当前不重跑，也不把运行时开关变成产品候选。**

原权威说明是 Plan `phase-1/native-sampler-findings-01.md` 的 “Same-ELF causal sensitivity” 节；本地原始数据在 `restored-stage1/measurements/spin-sensitivity-01/{sqlite,postgresql}`，执行器是 `restored-stage1/diagnostics/run_spin_sensitivity.py`。本次只读回 16 个既有 process 的结果和 command receipt：均 exit0/success，default/spin0 同 client 的 ELF 身份相同。32 个原始输入文件的 SHA 和重算 CPU 值见 [history-readback.json](history-readback.json)。没有重新采样、构建、执行消费者或修改产品。

原运行清除 DOTNET 与 COMPlus 两个 alias 作为 default，spin0 仅设 `DOTNET_ThreadPool_UnfairSemaphoreSpinLimit=0`。每库是 Korda/Dapper × default/spin0 × 两轮，共 8 进程，第二轮逆序；两库合计 16 进程。每 route 每 round 为 3×256=768 次、1,000 行查询。Korda phase consumer 还有 fluent/host-sql 路，以下仅列原报告选择的 hot Prepare。没有 sampling preload。这是旧 baseline phase 消费者，不是当前 integrated05 普通 workload 身份。

| 路径 | 轮次 | default CPU µs/op | spin0 CPU µs/op | 原报告 service p50 default→spin0 µs |
| --- | ---: | ---: | ---: | ---: |
| SQLite Korda Prepare | 0 | 3811.408 | 2036.668 | 1802.622→1760.814 |
| SQLite Korda Prepare | 1 | 3654.510 | 2086.790 | 1772.745→1805.356 |
| SQLite Dapper.AOT | 0 | 394.697 | 388.641 | 359.135→358.009 |
| SQLite Dapper.AOT | 1 | 369.568 | 384.008 | 350.287→357.944 |
| PostgreSQL Korda Prepare | 0 | 4105.382 | 2844.908 | 2498.735→2764.354 |
| PostgreSQL Korda Prepare | 1 | 4666.160 | 2878.413 | 2849.088→2731.834 |
| PostgreSQL Dapper.AOT | 0 | 500.716 | 370.188 | 485.758→480.159 |
| PostgreSQL Dapper.AOT | 1 | 525.844 | 431.953 | 491.721→489.385 |

旧数据已证明相当大的**设置敏感的净客户端 CPU**：Korda SQLite 每业务减少约1.57–1.77ms，PG减少约1.26–1.79ms；SQLite p50基本同区间，PG p50两轮方向相反。Dapper PG也有敏感性，不能把全部节省归为 Korda 专有成本；spin0下 Korda CPU 仍明显高于 Dapper。

锁定 runtime 源 `LowLevelLifoSemaphore.cs` 中，该参数只控制 WaitSlow 的乐观 backoff budget；零值会更早进入 WaitNoSpin/WaitAsWaiter。其余锁竞争、wake cooldown等 spin 不因此全部消失。已有 runtime 静态 ELF 证据确认配置读取；Recovery04又在实际捕获栈中核实9,350个样本走Thread.SpinWait→Backoff→WaitSlow。这加强了 caller 归因，仍不把样本百分比换成精确阶段 CPU。

## 当前还能回答什么，以及为什么不重复

“ThreadPool semaphore spin 是否贡献大量 CPU”早已得到肯定的有限因果证据。再次跑同类控制只能更新当前 integrated05 的设置敏感度；它不会自动提供一个尚未检验的安全产品改法，也不能挽救已拒的 tail06/local07 普通结果。

严格说，当前05剩余 CPU 中的**净设置敏感差额**尚未重新量化；只有这一差额会改变一个具体待决实现的取舍时，新的同 ELF 有界控制才有新增问题可答。即便如此，default−spin0 也包含 park/wake、线程调度与业务交错改变后的连带成本，不是“独占 spin 耗时”，不能据它定位到某次 offer、某个 batch 或计算可回收的框架 CPU。当前没有这样的新待决实现，本轮明确不追加该诊断。

后续应继续从已量化的具体分配/复制及所有权证据选择窄实现假设；保持普通消费者运行时默认。此结论不主张已达到 Dapper parity。
