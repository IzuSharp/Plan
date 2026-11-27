# pull-local07：真实默认调度器的双库 AOT 正确性

## 结论与身份

冻结源码 `645cfa5f184d65a67fa71455a5f7271ee8469309`（tree `244099ca35b396887d951299728a7bc2e0ecafb4`）的一份 Release Native AOT 完整 NativeHost 消费者已通过真实 SQLite 和 PostgreSQL 正确性执行。publish、原仓库 `tests/Data.NativeHost/run.py` 及外层驱动均正常退出 0。此处没有普通性能、分配、RSS 或排队延迟信用，也没有选择最终产品方案。按用户最新范围，所有本轮 1800 秒和 before 长测已取消。

产品改动仍仅为提交 `3fb88246b2fee303578f0527970e3d084d89ab40` 的 HostPull 默认 adapter 选择与新增常量 `preferLocal:true` adapter。完整 `CallbackCoordinator.cs`、原 `preferLocal:false` adapter、其它四个默认调用路径、MRVTS async=true、原生执行及取消语义均未作源码修改。新接口实现可能影响普通 AOT 去虚拟化；本正确性映像包含测试 scheduler，不能替代最终普通消费者 ELF 的调用形态核对。

完整身份、构建命令、退出和源前后哈希见 [receipt.json](receipt.json)，原始完整日志见 [runtime/consumer.log](runtime/consumer.log)，简要可机读结果见 [author-summary.json](author-summary.json)。ELF SHA256 为 `dbbd1f19e564a95deff10f8572426268d4cb5be3caa5eaae5add54408ac90900`；对应 `.dbg` SHA256 为 `cfa07d623d593b76e31acabac19e1eccef9f71d788d5d5706e9bfea7a8efd20f`，二者 Build ID 均为 `d173e5469481a0a6fa81dfc5089aaeb73594c466`。读取 debug ELF notes 时 readelf 曾输出“Unable to find program interpreter name”，调用仍返回 0 并成功取得匹配 Build ID；它不是构建或消费者错误。

## 实际默认调度器的六个场景

两库分别执行以下六个场景，三个 Test*Scheduler 均为 null。所有阻塞边界均用实际默认 worker 与真实数据库路径；测试 hook 只控制有限时序。

| 场景 | 实际证据与边界 |
| --- | --- |
| 非池线程提交 | ThreadStatic public-call 动态区间内不会执行 native Run；独立实际池线程在 BeforeRun held 时，调用者能够返回。原 caller EC/SC 保留，unsafe worker 不继承它们。 |
| 池线程提交 | 同一组动态区间与 EC/SC 断言也作用于实际 ThreadPool caller；不以不同 TID 或启动先后代替 never-inline 证明。 |
| A 的实际 Post held，独立 B 读取 | 两个 source/session 预先打开，避免连接容量混淆。B 从 A publisher worker 内提交，在另一实际 worker 上完成并消费自己的首行；A 的旧 Post 尚未返回。 |
| A Post held，B 取消及退休 | B 的 native Ready 回调 held 时取消。此前已准备的 id=1 行仍成功消费，registration/control/callback obligations drain；下一次 FetchAsync 在 admission 精确抛出原 token OCE，native Run 计数仍为 1；B cursor/session/source 在 A Post 释放前退休。 |
| A Post held，B 关闭 | 消费 B 首行后，B cursor/session/source 在 A Post 释放前退休。A 自己不要求 g2 抢在旧 Post 返回前执行。 |
| 有限热/冷竞争 | hot 的第一个 Run held 时，独立非池 cold 请求可抵达另一 worker；释放后 hot 依序消费 32 行并用恰好 33 次 pull 到 EOF，cold 恰好 1 次 pull。此场景只授予该有限 barrier 条件下的进展，不授予持续活跃 local 链的公平上界。 |

成功路径中，各 source/session/cursor 的最终 native owner counters 均为 0。所有 finally 先释放 holds；如果后续 Cleanup 本身抛出，剩余顺序 Cleanup 并不获得本报告的退休信用。此次实际运行没有该失败。

## 分套原始计数

以下是各测试类自己的计数，不能把 Program 的 438 当作全套总计，也不把部分计数随意相加。

| 原日志 suite | SQLite | PostgreSQL |
| --- | ---: | ---: |
| DefaultPullScheduling（新增） | 6 场景 / 178 assertions | 6 场景 / 178 assertions |
| ReadyScheduling | 4 场景 / 82 assertions | 4 场景 / 82 assertions |
| WorkerExecution | 4 场景 / 21 assertions | 4 场景 / 21 assertions |
| BorrowedHost | 16 场景 / 250 assertions | 16 场景 / 250 assertions |
| BufferedBorrowedHost | 12 场景 / 174 assertions | 12 场景 / 174 assertions |
| CursorClose | 296 assertions | 296 assertions |
| CommandCompletion | 451 assertions | 456 assertions |

完整 suite 还保留原有 parser/ABI/result fetch/parent transaction/rejected scheduler 等回归。最终 Program 自身输出 438 assertions、单独观测到 36 managed retirements，以及全部 source/session/operation/cursor/buffer/handle/pull/command counters=0。

## 保留失败与纠正

1. 初版测试提交 `c5b1ddb48e4e4c16d8b61404d2a5a5d032fc350b` 在独立源码审查中被发现错误预期：Ready 已准备结果后不应强制旧 pending 抛 OCE。该版本没有构建或执行。提交 `8d400ecc...` 只修窄测试，保留 result-wins 与下一请求取消 admission；未修改产品取消语义。
2. `correctness-01` 实际 publish exit=1，唯一编译错误是 Read 辅助 tuple 把 uint 行数声明为 int，CS0029，尚未启动数据库。原 receipt/publish.log 及该源身份均保留。`645cfa5f...` 单行改为 uint，未修改断言或门禁。
3. `correctness-02` 在独立有限复核后重新构建并通过完整双库运行；原 driver 身份、560MB build 前/450MB runtime 前磁盘门禁都没有弱化。实际可用空间分别为 753,831,936B 和 519,794,688B。

## 生命周期与保存

仓库原 `run.py` 负责 initdb、`pg_ctl -w start`、等待 consumer、finally 中 `pg_ctl -m fast -w stop`，以及 TemporaryDirectory 退出清理。harness 退出 0，PostgreSQL 原日志明确记录 `database system is shut down`。该证据是 pg_ctl 等待与日志确认，不声称直接 postmaster wait4 或外部宿主机全局排他。实际数据库及 runtime 没有性能观测信用。

实际 ELF、匹配符号、两原生库、生成 C#、完整原始日志均保留。另保留 63 个 compiler/restore metadata 文件（2,020,009B，包括 ILC rsp、assets、props/targets），索引为 [build-metadata.json](build-metadata.json)；候选相对 integrated05 的精确源码 patch 也在此目录。

Root 授权的独立清理只删除 bin 中与 publish 全字节相同的 ELF/debug/两 native 副本和已记录 SHA/size 的 ILC `.o`，共 5 项 86,640,714B。全部 publish 文件前后 identity 一致，DLL/PDB/生成文件/restore 元数据/源/失败日志未删除。详见相邻 `correctness-intermediates-cleanup-01/manifest-before.json` 与 `receipt.json`。正确性输出已封存，下一步由 root 做两个真实包普通消费者的实际 ELF 核对及最小 12-process text1000 反序短测。
