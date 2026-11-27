# Pull-local07：correctness-02 实际结果独立审查

**645cfa5f184d65a67fa71455a5f7271ee8469309 / tree244099ca35b396887d951299728a7bc2e0ecafb4 的唯一双库完整 Native AOT 正确性运行通过独立回读。** 实际 publish、nativehost-full 均exit0，源码前后快照相同；实际ELF与.dbg SHA和Build ID匹配，两个published native与原manifest相同，44份保留生成C#逐项匹配。没有重跑构建或数据库工作。

实际consumer.log中SQLite与PostgreSQL各一次 DefaultPullScheduling 6场景/178断言；原ReadyScheduling各4/82，WorkerExecution各4/21仍运行并通过。Program末尾438是Program自身计数，不能叫整个suite的全部断言，也不能与重复日志相加；它另外报告36次托管退休、全部列示native owner计数0。新默认测试的成功已包含其自身逐场景owner检查。

取消测试保留现存结果先胜顺序：held Ready帧内stop，已ready结果正常消费；下一请求在admission以原token取消，未多跑native；B仍可在无关A Post held期间安全关闭。有限hot/cold控制不证明持续队列公平或吞吐。

PG沿原tests/Data.NativeHost/run.py专用临时数据目录运行，finally调用check=True的pg_ctl -m fast -w stop；整体进程exit0，postgres.log另记录fast shutdown请求和database system is shut down。这里授予既有正确性生命周期证据，不把它冒充普通mixed observer的PID/startTicks、稳态CPU或协议等待观测。

correctness-01仍保存publish exit1 / CS0029 uint→int编译错误；只有publish命令，没有启动数据库，不能算运行正确性失败或成功。此前c5b Ready后强制OCE是审查修掉的测试预期，亦无运行信用。

产品仍是新singleton常量preferLocal:true与HostPull默认选择，native及原MRVTS/其他defaults不改。此正确性ELF含大量测试类型，不能替代后续真实PackageReference普通consumer的去虚拟化与调用点检查。当前可接root授权的两个普通包构建和最小text1000短A/B；没有性能收益、对齐或长测信用。
