# Four final segments: review notes after 92b9230 build closure

本页只说明本轮实际证据衔接，未改产品、selector、冻结工具或原算术分析器。92b9230 的两个包通过独立闭合核验，但已被事前 paired 性能规则拒绝；正式 source 保持公开 17da。此前 0aa 从未计时。下文最终输入按继续选用 17da 衔接，92b9230 的包/ELF 哈希只保留为拒绝实验的证据。

## 1. 最终四段与短段分开

最终矩阵严格是 SQLite candidate、SQLite Dapper、PostgreSQL candidate、PostgreSQL Dapper，各一段真实 steady 1800 秒，总计四段串行。固定 fixture 保留，但不进入 timing。before 不进入这四段。

优化前补测继续使用 f0078da 的 before-current workload 包，以最终相同 C/R、35-case 工作量和消费方式执行 before/candidate 120 秒。paired phases、offered 30 秒、120 秒补测与历史短测都不能获得 30 分钟信用。numeric 场景的实际 32 行也不能写成 PK 单行；1/100/1000 phase 是另一组结果契约。

## 2. 选定 source 后才冻结

复用 [现有 freeze 说明](../../local-load-tools/final-freeze-and-audit.md) 和 [selector 入口](../../local-load-tools/README.md)。原 generator、旧计划和历史结果保持原字节；生成新原始计划、新派生 final 计划和新输出目录。selector 的 source commit 必须是实际 runner/harness commit，derivedFrom 必须指回原计划及其 SHA。

当前正式 candidate 的 workload build receipts 是：

- `/workspace/scratch/fd78534029f7/builds/candidate-sqlite-02/consumer-workload/build-receipt.json`，release 是同目录上级 `public/release.json`。
- `/workspace/scratch/fd78534029f7/builds/candidate-postgresql-02/consumer-workload/build-receipt.json`，release 是同目录上级 `public/release.json`。

两份产品 commit 都是 `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa` / tree `bc9087d843d8d741d83d44f53d0b2c5af26dcffc`；四个最终 consumer 仍分别声明真实 harness commit。复用的 Dapper 二进制不能写成新构建，其历史 receipt 缺 builder_sha256 的边界保持原说明；源/项目/包/生成 SQL 证明和 ELF 必须实际匹配所选 harness。

`audit_final_identity.py freeze` 必须在两个 final 输出目录尚不存在时完成。检查 status=frozen，保存准确 freeze SHA，再启动真实运行。生成或冻结成功不构成最终测量成功。

## 3. 运行时要核对的证据

四段实际 command argv、run plan、runner、ELF、加载的 native 和所有起止时间必须与冻结描述相符。既有 source/binary/SQL 证据仍要保持可读；计时期间不并行构建、诊断、全量哈希或压缩。更改候选后不得编辑旧 freeze 来容纳新字节。

原算术分析器负责 35-case 覆盖、每秒业务进展、计数守恒、1800 秒 steady 区间、错误/拒绝、fixture 排除、四格完整、串行和 idle 语义。不能用进程墙钟 1800 秒代替真实 steady 时长，不能把退出时不可得的内存样本写为 0 RSS。host、资源采样和 cgroup 的实际限制保留，补充身份审计不增加主机资格。

候选实际结果必须完整序列化 Sources、Sessions、Operations、Cursors、Buffers、Owners、PullChannels、CommandCompletions，全部严格整数 0。Dapper 保留自己的应用连接归零证据；不伪造 Korda owner 计数。旧 before ABI 缺字段时保留缺失事实，不填造 CommandCompletions=0。

## 4. 分配、GC 与历史证据边界

正式普通负载记录进程分配、GC 和业务结果；插桩 allocation/FFI 诊断单独说明。17da 的 12 份 allocation 结果已经按其原 source 审计，因正式候选保持 17da，可继续引用为当前候选的单独诊断证据；不能把它们写成 92b9230 的分配数据，也不能与普通计时合并。

已观察 mapper/List 范围包含内部 codec/driver scratch；FrameworkOnlyBytes 仍为 null，不用总量相减推断纯框架分配。已保留的 allocation GC 只是窗口内进程级差值，不是含 setup/warmup/gaps 的进程完整生存期计数。最终报告须使用对应原测量实际拥有的 GC 范围。

## 5. 四段结束后的收口

先用原 index/算术分析器产生四格完整报告，再执行补充 `audit`：提供冻结文件、其准确 SHA 和实际算术报告。必须同时满足原四格/串行/idle 结论与补充 status=passed、四个实际 segments、inputsUnchanged=true。保留任何失败和对应 source/输入；修正时用新输出路径。

最终索引逐段列出 raw JSON、command receipt、resources JSONL、stdout、host、runner、计划，以及 command/steady/consumer/idle 的实际边界。source、包、原生库、生成代码、SQL、构建与运行工具形成同一个身份闭合；before120 秒及所有历史候选放在各自明确范围内。

正式 17da 的现有 CI `45772470391` 已 completed/success，准确 head 与各 job 的回执保存在 [当前 CI 记录](../../current-ci-review.md)。两个独立包的闭合也已单独完成，四段通过后仍须核对 PR head 与应触发的现有发布。此次对已拒绝 92b9230 的 GitHub PR-event workflow 查询返回空第一页，只表示没有取得该查询下的运行回执，不能断言所有事件均未运行；其记录保留但不充当正式 17da 的验收门。四段和证据门完成后才进行本轮正常合并及按现有规则的发布核对，不新增性能 CI。
