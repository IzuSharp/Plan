# Current 17da allocation audit

核验时间：2026-11-26T07:38:22.340502+00:00。准确候选 `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa` / tree `bc9087d843d8d741d83d44f53d0b2c5af26dcffc`。

**12 份诊断记录全部通过；timingCredit=false，FrameworkOnlyBytes=null，没有做相减。** 两库各包含 candidate/Dapper × 1、100、1000 行，本轮没有 before allocation overlay。这组是插桩分配诊断，不能用于吞吐或延迟结论。

## 核验与来源

- 72 个窗口、18,432 次业务操作；每窗口 256 次、每 route 3 个窗口。映射器和 List.Add 各 6,764,544 次，List 构造 18,432 次；与完整消费的结果行数严格守恒。
- 精确核对 4 份成功 overlay build receipt、原普通消费者 receipt、实际 AOT ELF、原生库、源文件、包与 restore 图；重放固定构建器的源插桩及实际生成 mapper 插桩，所有字节与观察器身份一致。候选经已核验的当前公开包/source 链闭合；复用的 Dapper 历史 overlay 保留其原身份，只说明对应源字节与当前 harness 匹配，不重写其构建时间或推断原构建 commit。
- Candidate 的各窗口边界要求 Operations/Cursors/Buffers/PullChannels/CommandCompletions 严格整数 0；Source/Session/Owners 在窗口内仍有活对象。每个进程结束 Drained 的 Sources/Sessions/Operations/Cursors/Buffers/Owners/PullChannels/CommandCompletions 八项全部严格整数 0。
- Dapper 的 6 份 SQL contract 都指向同库、同行数、当前普通 candidate phase receipt，准确绑定其 SHA/ELF/SQL；没有沿用历史 SQL 证明。连接关闭、单物理连接、关闭 Npgsql auto-prepare 的回执均通过。
- 全部诊断 command exit=0、success=true、无 timeout/observerErrors，实际 argv/计划和两个 provider 的串行区间一致；PostgreSQL 连接由保留的 owner 进程 argv/port 推导，未假定 SQLite 的 connection 字段。
- 全部已绑定原件在审计末尾重新哈希，未改变。实际成功审计耗时 1.10 秒，没有构建或产品执行。

## 实际映射器与 List 范围

单位 B/次业务操作。映射器范围包含生成读取器内部发生的 codec/driver 临时分配；不是纯 DTO 存活大小。List 范围为实际构造加 Add。

| 数据库 / 路径 | 行数 | 映射器 B/次 | List B/次 | 两范围合计 B/次 |
| --- | ---: | ---: | ---: | ---: |
| sqlite / candidate 三路相同 | 1 | 72.0000 | 64.0000 | 136.0000 |
| sqlite / Dapper.AOT | 1 | 72.0000 | 64.0000 | 136.0000 |
| sqlite / candidate 三路相同 | 100 | 6,400.0000 | 856.0000 | 7,256.0000 |
| sqlite / Dapper.AOT | 100 | 6,400.0000 | 856.0000 | 7,256.0000 |
| sqlite / candidate 三路相同 | 1000 | 69,760.0000 | 8,056.0000 | 77,816.0000 |
| sqlite / Dapper.AOT | 1000 | 69,760.0000 | 8,056.0000 | 77,816.0000 |
| postgresql / candidate 三路相同 | 1 | 72.0000 | 64.0000 | 136.0000 |
| postgresql / Dapper.AOT | 1 | 72.0000 | 64.0000 | 136.0000 |
| postgresql / candidate 三路相同 | 100 | 6,400.0000 | 856.0000 | 7,256.0000 |
| postgresql / Dapper.AOT | 100 | 6,400.0000 | 856.0000 | 7,256.0000 |
| postgresql / candidate 三路相同 | 1000 | 69,760.0000 | 8,056.0000 | 77,816.0000 |
| postgresql / Dapper.AOT | 1000 | 69,773.5417 | 8,056.0000 | 77,829.5417 |

PostgreSQL Dapper 1000 行的映射器范围实测为 69,773.5417 B/次，其余千行范围为 69,760 B/次。这里只保留该观察，没有据此归因或扣除。

## 独立保留的进程分配与 GC

下表分配是原窗口进程级分配差值，包含已消费的业务结果；保留插桩语义。GC 为同一窗口的进程级 GC.CollectionCount 差值，按同 route 的 3 个窗口合计；不是线程局部，也不是包括 setup/warmup/窗口间隙的整次进程生存期 GC。没有从这些数字减去上表来宣称框架额外分配。

| 数据库 | 行数 | 路径 | 进程 B/次 | GC 0/1/2（3 窗口） |
| --- | ---: | --- | ---: | --- |
| sqlite | 1 | fluent | 19,551.8125 | 5/1/0 |
| sqlite | 1 | prepared | 2,569.3229 | 2/0/0 |
| sqlite | 1 | host-sql | 8,119.3125 | 3/0/0 |
| sqlite | 1 | dapper-aot | 2,131.3646 | 1/0/0 |
| sqlite | 100 | fluent | 26,651.4062 | 8/0/0 |
| sqlite | 100 | prepared | 9,769.3646 | 4/0/0 |
| sqlite | 100 | host-sql | 15,338.2604 | 6/1/0 |
| sqlite | 100 | dapper-aot | 9,251.3646 | 3/0/0 |
| sqlite | 1000 | fluent | 97,494.5521 | 36/0/0 |
| sqlite | 1000 | prepared | 80,601.4583 | 29/0/0 |
| sqlite | 1000 | host-sql | 86,330.7292 | 32/0/0 |
| sqlite | 1000 | dapper-aot | 79,810.1875 | 29/1/0 |
| postgresql | 1 | fluent | 19,555.8021 | 6/1/0 |
| postgresql | 1 | prepared | 2,568.0625 | 1/0/0 |
| postgresql | 1 | host-sql | 8,116.9896 | 3/0/0 |
| postgresql | 1 | dapper-aot | 2,108.1250 | 1/0/0 |
| postgresql | 100 | fluent | 26,640.4375 | 8/0/0 |
| postgresql | 100 | prepared | 9,742.4167 | 4/0/0 |
| postgresql | 100 | host-sql | 15,314.9792 | 6/1/0 |
| postgresql | 100 | dapper-aot | 9,246.0625 | 2/1/0 |
| postgresql | 1000 | fluent | 97,471.2812 | 36/0/0 |
| postgresql | 1000 | prepared | 80,575.3333 | 31/0/0 |
| postgresql | 1000 | host-sql | 86,292.3854 | 31/0/0 |
| postgresql | 1000 | dapper-aot | 79,855.4479 | 29/1/0 |

## 复用入口、控制与失败保留

脚本基于 `continuation-3/allocation-audits/audit-allocation-{provider}-01.py` 的窗口/分配/GC算法，改为每库准确 6 份记录，并增加当前 source/package/ELF、原始/生成源码、计划命令、八项 owner 和当前 Dapper SQL 引用的闭合。原历史脚本与结果未修改。

```sh
python3 audit_current_allocation.py \
  --root /workspace/scratch/fd78534029f7 \
  --repository /workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-korda \
  --output /ABSOLUTE/FRESH/audit.json
python3 check_allocation_controls.py --output /ABSOLUTE/FRESH/controls.json
```

只在测量空档运行完整审计。输出必须不存在；脚本不构建、不加载消费者、也不启动数据库。152 个纯内存有限控制覆盖正例、计数 skew、整数类型/缺字段、FrameworkOnlyBytes、进程分配/GC、SQL计数、八项 owner 和非严格 JSON。控制不读取测量文件、不做哈希扫描。

首个适配运行在 PostgreSQL argv 展开处以 `KeyError: connection` 退出，0.64 秒；对应原脚本和失败记录完整保留于 [failed-01](failed-01/)。原因是 PostgreSQL plan 使用 runner 分配的连接，需要从 postgres-owner argv 绑定端口。修正后成功报告为 [current-allocation-audit-02.json](current-allocation-audit-02.json)，未把首轮误记为产品失败，也没有抹掉它。

本目录 [receipts](receipts/) 原样保留 12 份 allocation receipt（包含完整 scope、base/build/ELF 引用和每窗口字段）；[receipt-copies.json](receipt-copies.json) 记录原路径和复制 SHA。完整 base JSON、资源采样与消费者大归档留在原测量目录，待统一证据归档；当前报告的 inputFiles 已列出实际核验的全部原件身份。

没有 before allocation cohort，因此不输出本轮 before/after 分配收益；没有 30 分钟或最终性能信用。候选三路是 fluent/prepared/host-sql，没有据此宣称单独的 Find 分配收益。
