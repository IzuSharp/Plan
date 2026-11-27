# Frame08 ordinary 控制器与 idle 边界独立审查

**当前 source-02 的四个隔离工具可用于后续实际输入准备，未发现短测范围或因果比较的新阻断。** 本报告没有准备八个actual inputs、生成实际计划、构建或执行任何工作负载；这些仍需等真实consumer完成。01和02所有完整diff、旧源与新源SHA均已核实，未改早先冻结工具。

## 比较身份和有限范围

基线显式改为ownership05 / 0.1.0-parity05.2（69b2383），candidate为frame-pool08 / 0.1.0-parity08.1。08已将相同前置cleanup合入b0a6f229；独立核对相对749仅两处11增2删，逻辑块与69b相同，Seal只适配缩进。原integrated05 / parity05.1产物保留，不以标签替换其历史结果。

每库只跑related:32:prepared，2048次业务、128次专项暖机、C1、persistent session、batch32，三路ownership05→candidate→Dapper后整序反向，共12个测量进程加两个fixture initializer。related的prepared标签保留现有契约：Korda LoadRelatedAsync每次重建bounded batch，没有公共prepared overload。三方原32行--verify预检都保留，先跑mixed35再进行128次专项暖机，两部分都在steady边界前；不可只把启动工作记为128或混入每业务计数。测量的行数仍应按实际related业务oracle，32是父key数，不能直接写32结果行。

准备器会核同native、包版本、所有实际输入和12命令顺序；外层保留quiet、协作lock、持久失败lease、PG正常退还、前后输入snapshot和source SHA门禁。Allocation profile被拒绝；没有新增long或pressure运行安排。wrapper08在这里仅提供input snapshot/已审公共辅助函数，沿用其被记录的freeze07辅助源作为身份输入并不授予08 freeze或mixed测量信用。

## 五秒 idle 的实际含义

已读现成两route、两provider的Measurement.cs，逐route字节相同。CPU/managed before/after和steady end先结束；随后保存结果、释放全部worker/session/source并读取drained owner；之后才启动五秒Task.Delay和idle进程快照。没有强制GC。新增idle参数不会把这五秒加入EffectiveSeconds、稳态CPU或原始分配分母，但完整client进程/observer lifetime仍包含它。

因此后续可以报告**业务释放后、无forced GC的五秒驻留观察**，而不能称为垃圾回收后最低RSS或全部残留都属于私有pool。静态池本就可跨source保留；框架/驱动/DTO/工具在进程总量中仍混合。ProcessAfter峰值为到该快照为止的进程峰值，idle.After峰值可能还包含drain和idle，不可互换。现成driver summary未替代完整raw审核；取得raw后应核Idle非null、RequestedSeconds=5、ObservedSeconds足够、owner退还、CPU/alloc差分、GC pause以及相同oracle/计数，而不新增测量矩阵。

首次池初始化和cold buffer成本发生在preflight/warmup的可能性需与单独诊断说明；本短测只提供warm重复业务资源成本。不要从稳态净分配降低直接推算cold成本为0、clear免费或RSS有同等下降。
