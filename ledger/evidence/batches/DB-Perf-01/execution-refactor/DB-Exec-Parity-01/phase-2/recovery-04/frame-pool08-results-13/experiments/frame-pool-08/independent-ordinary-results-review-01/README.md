# Frame pool 08：独立普通短测审查与选择

**建议拒绝将 frame pool 08 作为当前双库统一优化合入，保留 ownership05（既有五项优化 + 独立 owner cleanup 修复）。** 本次观察确实证明重复的托管分配节省，但未满足预先写定的 CPU、尾延迟和释放后内存成本均可接受的条件。这是本候选的选择结论，不是提前停止 DB-Exec-Parity-01 或取消其余已授权正常审查、合并、发布验证。

## 证据与执行范围

冻结审计器仅执行一次，SHA `893178ea625474f41bf985d38e9131e3418ad19325f8d202268d188e851e62af`，exit 0；[validation.json](validation.json) 的 2,470 项检查全部通过。836 个唯一实际输入文件复核，八份输入身份在各 provider 前后相同。12 个业务进程成功完成 24,576 次业务，返回 1,302,528 行；两份初始化进程另列，共 14 个串行子进程。没有重跑业务、构建、采样或扩大矩阵。

外层实际时间为 `2026-11-27T13:11:20.693763+00:00` → `2026-11-27T13:14:11.324361+00:00`。每库第一轮 ownership05 → frame08 → Dapper，第二轮反向。每格是 `related:32:prepared`，persistent session，C1、batch32，128 次专项暖机另计，随后 2,048 次计时业务；已有 mixed35 `--verify` 预检也另计。每业务相同 oracle：53 行，digest `2847736615530494015`。原生 SQL 工作量在 Korda 每格为 2,048 次，PG 协议提交计数每格 8,192；协议提交计数不等于解析过的网络消息数。Dapper 没有该原生计数，不能以空值推断零执行。

真实 PackageReference Native AOT 消费者：ownership05 / `0.1.0-parity05.2` 含共同 cleanup 修复，frame-pool08 / `0.1.0-parity08.1` 对应普通源 `13b25de2b67d858d8b6524f615e3a84b4c541817`。08 的 local03 诊断 overlay 不在普通消费者中。前后实际 C#、csproj、assets、生成代码、ELF/debug/native、nupkg、构建/准备/绑定回执和 runner/observer 身份均由原冻结审计器验证；详见 [input-identities.json](input-identities.json)。不将旧05的历史性能重新标记为 ownership05。

Korda related 的 `ActualDiagnosticSql` 字段是公开操作说明，**不是 SQL 指纹**。它的 SHA `21a3788a6e9a9dae7e90a5e236e7d566d72916f9c72ae1f144c0883f9534f973`、两轮原文、53 行/digest oracle、真实源/生成代码/ELF 链分别核验。Dapper 保存实际 SQL；不能强行要求双方说明字段的文本哈希相等。完整原文在 [diagnostic-contracts.json](diagnostic-contracts.json)。

## 每格绝对成本

CPU = 本进程测量区间 user + system CPU / 成功业务；托管字节 = 同区间进程累计分配差 / 成功业务，包含框架、驱动、DTO 和工具实际计入部分。p50/p95/p99 为原直方图的桶上界。下表延迟和 CPU 用 ms，分配用 B；吞吐是本次 C1 闭环成功业务/s。

| 库 / 轮 | 路径 | CPU ms/业务 | 托管 B/业务 | p50 ms | p95 ms | p99 ms | 闭环业务/s |
|---|---|---:|---:|---:|---:|---:|---:|
| sqlite / 1 | ownership05 | 4.483250 | 516145.859 | 3.211264 | 8.781824 | 11.337728 | 243.774 |
| sqlite / 1 | frame08 | 5.505271 | 455377.809 | 3.768320 | 10.092544 | 14.680064 | 201.603 |
| sqlite / 1 | Dapper.AOT | 0.982877 | 74098.188 | 0.933888 | 1.335296 | 1.679360 | 1010.141 |
| sqlite / 2 | Dapper.AOT | 1.404860 | 74098.172 | 0.991232 | 3.325952 | 4.980736 | 711.639 |
| sqlite / 2 | frame08 | 4.481099 | 455357.445 | 3.211264 | 8.454144 | 11.272192 | 247.916 |
| sqlite / 2 | ownership05 | 4.523294 | 516179.207 | 3.276800 | 8.847360 | 11.599872 | 237.600 |
| postgresql / 1 | ownership05 | 4.021659 | 516146.953 | 5.013504 | 10.092544 | 13.565952 | 173.554 |
| postgresql / 1 | frame08 | 4.055282 | 455360.746 | 4.816896 | 9.895936 | 12.845056 | 178.885 |
| postgresql / 1 | Dapper.AOT | 0.528494 | 51224.242 | 1.564672 | 4.259840 | 5.570560 | 481.334 |
| postgresql / 2 | Dapper.AOT | 0.444885 | 51224.242 | 1.376256 | 3.375104 | 4.653056 | 597.638 |
| postgresql / 2 | frame08 | 3.636083 | 455373.566 | 4.489216 | 9.240576 | 12.582912 | 189.983 |
| postgresql / 2 | ownership05 | 4.470196 | 516170.172 | 5.079040 | 10.420224 | 13.369344 | 170.556 |

## 两轮配对结果与 Dapper 差距

| 库 / 轮 | 08 CPU vs ownership05 | 08 p50 | 08 p95 | 08 p99 | 08 托管分配 | 减少 B/业务 | 08 CPU / Dapper | 08 p99 / Dapper |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| sqlite / 1 | +22.796% | +17.347% | +14.925% | +29.480% | -11.773% | 60768.051 | 5.6012× | 8.7415× |
| sqlite / 2 | -0.933% | -2.000% | -4.444% | -2.825% | -11.783% | 60821.762 | 3.1897× | 2.2632× |
| postgresql / 1 | +0.836% | -3.922% | -1.948% | -5.314% | -11.777% | 60786.207 | 7.6733× | 2.3059× |
| postgresql / 2 | -18.659% | -11.613% | -11.321% | -5.882% | -11.778% | 60796.605 | 8.1731× | 2.7042× |

| 库 / 轮 | ownership05 CPU / Dapper | ownership05 p99 / Dapper | ownership05 分配 / Dapper | 08 分配 / Dapper |
|---|---:|---:|---:|---:|
| sqlite / 1 | 4.5614× | 6.7512× | 6.9657× | 6.1456× |
| sqlite / 2 | 3.2197× | 2.3289× | 6.9662× | 6.1453× |
| postgresql / 1 | 7.6097× | 2.4353× | 10.0762× | 8.8896× |
| postgresql / 2 | 10.0480× | 2.8732× | 10.0767× | 8.8898× |

四个配对都减少 60,768.051–60,821.762 B/业务，即 11.773%–11.783%。独立 local03 的三次暖租借/归还窄边界为 0 B，配合普通进程的稳定分配下降，支持“避免重复分配临时 frame”的方向。**不能把约 60.8 KB 整体差额精确归给旧的 60,504 B 数组**；每业务额外 264.051–317.762 B 的差额尚未逐调用点解释。原生分配本次没有 profile，保留未知；也没有框架整体 0 B 结论。

## GC、峰值与释放后观察

每格已有 5 秒 idle，位于 workload/session/source drain 之后、正式时间/分配边界之外，无强制 GC。idle 的 CPU 和 heap 样本不加进上表。下表内存用 MiB（1,048,576 B）；峰值使用原进程报告字段，另保留 direct wait4 全寿命峰值。heap 是 `GC.GetTotalMemory(false)` 的存活样本，不能当分配量。

| 库 / 轮 | 路径 | steady 后 RSS MiB | idle 后 RSS MiB | steady 后报告峰值 MiB | wait4 全寿命峰值 MiB | idle heap MiB | GC 0/1/2 | 测量 GC pause ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| sqlite / 1 | ownership05 | 30.4727 | 30.3750 | 31.7344 | 31.7344 | 1.3850 | 416/76/1 | 340.289 |
| sqlite / 1 | frame08 | 30.5156 | 30.4180 | 30.7109 | 30.7109 | 2.9779 | 311/95/1 | 328.468 |
| sqlite / 1 | Dapper.AOT | 20.5703 | 20.5586 | 22.0469 | 22.0469 | 1.6342 | 72/0/0 | 29.472 |
| sqlite / 2 | Dapper.AOT | 20.7930 | 20.7812 | 22.1953 | 22.1953 | 1.8730 | 72/0/0 | 23.234 |
| sqlite / 2 | frame08 | 30.5195 | 30.4219 | 30.7812 | 30.7812 | 1.7099 | 303/89/1 | 273.795 |
| sqlite / 2 | ownership05 | 30.3672 | 30.2852 | 31.8516 | 31.8516 | 1.3506 | 429/73/1 | 360.735 |
| postgresql / 1 | ownership05 | 28.6836 | 28.3633 | 30.1758 | 30.1758 | 1.3484 | 415/82/1 | 354.383 |
| postgresql / 1 | frame08 | 29.2969 | 29.0000 | 29.6445 | 29.6445 | 2.8081 | 304/95/0 | 277.549 |
| postgresql / 1 | Dapper.AOT | 26.2773 | 26.2812 | 28.0508 | 29.6328 | 2.7346 | 49/0/0 | 30.615 |
| postgresql / 2 | Dapper.AOT | 26.3125 | 26.3203 | 27.8984 | 29.5156 | 2.7219 | 49/0/0 | 31.511 |
| postgresql / 2 | frame08 | 29.1211 | 28.7891 | 29.5742 | 29.5742 | 1.9521 | 309/96/1 | 269.305 |
| postgresql / 2 | ownership05 | 28.6133 | 28.2656 | 30.2461 | 30.2461 | 0.8075 | 425/67/1 | 374.163 |

| 库 / 轮 | 08 idle RSS 增量 B | 08 报告峰值变化 B | GC0 变化 | GC1 变化 | pause 变化 ms |
|---|---:|---:|---:|---:|---:|
| sqlite / 1 | +45,056 | -1,073,152 | -105 | +19 | -11.821 |
| sqlite / 2 | +143,360 | -1,122,304 | -126 | +16 | -86.940 |
| postgresql / 1 | +667,648 | -557,056 | -111 | +13 | -76.834 |
| postgresql / 2 | +548,864 | -704,512 | -116 | +29 | -104.858 |

报告的峰值 RSS 与 GC pause 四对都下降；GC0 次数下降，GC1 次数四对上升。idle RSS 四对均增加，幅度分别为 45,056、143,360、667,648、548,864 B。idle heap 也更高，但没有强制收集，因此不能把全部差额直接算成 pool 长期保留或泄漏。所有 idle 段报告 GC pause 为 0。静态池的有限缓存本来就不提供自动 trim；它的 491,520 B 可缓存 payload 上限不是 active memory 或 RSS 上限。该段只提供五秒观察，未证明长时间平台或并发池成本。

## PostgreSQL 服务端成本单列

下表使用同一 postmaster PID/startTicks 的 visible live/reaped tree，端点在稳态区间内（inner）或区间外（outer）。采样是非原子 /proc 可见树读取；它们不是精确稳态值或数学上严格的上下界，退出子进程和拓扑读入空隙仍有未知。没有 per-PID maximum 累加或边缘外推。完整端点和 user/system 分项留在 [per-process.json](per-process.json)。

| 轮 / 路径 | inner user s | inner system s | inner 总 s | outer user s | outer system s | outer 总 s |
|---|---:|---:|---:|---:|---:|---:|
| 1 / ownership05 | 2.67 | 0.98 | 3.65 | 2.78 | 1.00 | 3.78 |
| 1 / frame08 | 2.59 | 1.06 | 3.65 | 2.71 | 1.12 | 3.83 |
| 1 / Dapper.AOT | 2.62 | 0.16 | 2.78 | 2.90 | 0.17 | 3.07 |
| 2 / Dapper.AOT | 2.16 | 0.12 | 2.28 | 2.39 | 0.14 | 2.53 |
| 2 / frame08 | 2.68 | 0.87 | 3.55 | 2.78 | 0.93 | 3.71 |
| 2 / ownership05 | 2.49 | 0.92 | 3.41 | 2.64 | 0.95 | 3.59 |

单个 PG owner 的 direct wait4 全寿命 CPU 为 22.538294 s，包含 setup、预检、所有六格、暖机、idle 和 shutdown。**不把它按六格平摊、不加到客户端 CPU 或上述稳态窗口。** 所有原 command 与 adapter retirement / owner wait4 通过，后台已正常退出。

## 选择理由与剩余未知

1. 资源目标已得到重复支撑：普通每业务分配下降约 11.78%，local03 证明窄边界暖租借免去数组新分配，同时记录 cold 67,000 B（含 nested pool init 1,400 B）、forced miss 65,560 B、每次完整 65,536 B 清零范围。清零是源码范围及清后零值证据，不是硬件 store/带宽测量；cold 前 40 B 未归因。不以窄边界收益遮盖完整候选成本。
2. CPU 收益没有跨两轮重复。SQLite 第一轮 CPU +22.796%、p99 +29.480%，第二轮仅 −0.933% / −2.825%。PG 第二轮 CPU 改善明显，第一轮 +0.836%；PG p99 两轮改善约 5%–6%。因此不能授予统一双库性能收益，也不能以 PG 覆盖 SQLite 首轮结果。
3. 分配/峰值节省换来每格更高的 idle RSS，GC1 增加。幅度不自动证明不可接受泄漏，但当前证据也未建立整体内存代价一定更好的结论。
4. 任务成员已协调 quiet，未证明宿主租户独占。整进程 host steal 比例和 Dapper 跨轮变化保留在逐进程文件；这些不同范围的观测不能精确归因单轮 CPU/p99，不能把坏结果抹去。当前实验支持候选整体观察，不证明 pool 的某个 lock/clear/分支独占回退。
5. 依照已发布 [frame-pool-08-hypothesis.md](../../../worktrees/Plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/DB-Exec-Parity-01/phase-2/recovery-04/frame-pool-08-hypothesis.md) 的“重复净资源收益且 CPU/tail/memory 代价可接受；材料性回退拒绝或收窄”，本轮选择拒绝统一候选。此时不另做 provider-specific shipping 分叉，也不增 mixed、加时长或补有利轮次。保留该方案与全部原始证据，继续当前已审 ownership05 的正常交付。

原有正常 Binding 557 assertions/13 cases、Relations 1,244 assertions/133 retirements，local03 10 个故障 /102 assertions 及 99 个资源断言已分别封存，未重跑。它们证明本候选相应已测契约，不会把性能选择拒绝改写成正确性失败。owner cleanup 修复仍独立保留；旧 unsafe ABA 仅 source-confirmed 风险，没有运行复现，且内部 OOM 分配顺序变化已限定。

## 审查文件与边界

- [per-process.json](per-process.json) / [CSV](per-process.csv)：全部 12 进程绝对值、PG 端点、host 观测、ELF/native/command/raw 身份。
- [per-round-comparisons.json](per-round-comparisons.json) / [CSV](per-round-comparisons.csv)：四个同轮配对，不把 p99 跨轮平均。
- [validation.json](validation.json)：冻结审计器原输出，2,470 checks；计数、oracle、PID/startTicks、所有权、串行、真实输入、默认运行时、无 profile、时间/GC/idle 边界均通过。
- [decision.json](decision.json) 与 [review-receipt.json](review-receipt.json)：人工选择及本报告封存身份。

这批 C1 闭环专项不提供外部到达率下的拒绝点、排队容量或持续吞吐信用。服务直方图不冒充 scheduled latency。没有原生分配实测，没有新的 broad mixed gate。所有长测已由用户取消，`finalCredit=false` 表示没有原始长测验收信用，不是要求以后补测。与 Dapper 仍有数倍 CPU/分配/延迟差距，不标记已全面对齐。
