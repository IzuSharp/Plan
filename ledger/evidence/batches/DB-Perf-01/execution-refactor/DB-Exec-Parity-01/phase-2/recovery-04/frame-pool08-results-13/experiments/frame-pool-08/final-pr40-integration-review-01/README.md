# Current PR40：有限最终整合审查

**对 `106fe68b6f6c2537f478daf65a71ab97cc4b15ff` / tree `f7660759bba43ae83324620e2fb731efd479c3b5`，本次有限审查未发现具体阻断正常合并的契约或证据问题。** 可以按既有授权走正常合并，再核验合并后既有 main CI、规则发布和真实公共 NuGet Native AOT 消费。本结论不授予尚未执行的合并、发布、合并后 CI 或完整 Dapper 性能对齐信用。

本审查只重读必要小源码差异、原封存结论和 exact-head CI/impact 元数据；不重复构建、正确性、普通性能或历史全部身份检查。12 项当前整合检查全部通过，见 [validation.json](validation.json)。

## 准确产品组成

当前 head 与已审 local69b 的 tree 相同，两个提交都直接以 retained05 `2ea67ce1902f330679c3ebff4d6d5733be20f69c` 为父。相对05只有 `QueryCommand.Submission.cs` 的 11 insert /2 delete，见 [source-diff.patch](source-diff.patch)。因此当前 PR 中保留的产品组成是05的五项和独立 owner fix，不包含被拒绝的 tail06、preferLocal07、frame-pool08，也不包含 local03 插桩。

| 保留项 | 本次复用的契约证据与边界 |
|---|---|
| Worker-D：预约托管工作项执行 prepared native pull | 四项集成独立审查覆盖 generation、唯一 claim、执行帧/source ticket、never-run abandonment、callback-tail 和取消/冷关闭。减少每批 native WorkerPool post，仍保留 managed scheduling 与完成/关闭语义；不宣称 FFI 总数减少。 |
| canonical decimal 快路径 | 精确 canonical shape/范围才走捷径，非匹配字节回落既有 validator，profile/错误优先级保留。历史单行 CPU 未解释部分不会因 native 样本比例下降而消失。 |
| SQLite prepare flag | 去除不合实际生命周期的 PERSISTENT hint，语句仍按原生命周期 finalize；不是物理语句缓存或减少 prepare 次数。 |
| 私有 relation consume/import | 仅私有临时分支，destination 先持有 graph，成功导入后才消费 source；公共快照仍独立。 |
| 私有 relation capacity hint | 首分支实际容量、2048 cap、原 envelope clamp、fresh guard 和相同组件编码长度限制；原额度/错误/快照/所有权保持。原已测资源节省与 CPU/尾部不稳定分别保留。 |
| metadata-before-adoption owner fix | Plan 与 CTE 的完整 metadata 在 raw-owner catch 内先求值，再采用 DatabaseOwner；成功后的 origin 失败仍由 wrapper.Dispose 归还。无公共 API/native ABI/CI 变化。 |

前四项复用 `experiments/worker-d-diagnostic/integrated-independent-review-04.md`。capacity 的源码独立检查由 root 完成，记在 `experiments/relations-recovery-04/capacity-results.md`；本审查者曾实现该局部实验，不把这次复用报告伪称对自己原实现的首次独立审查。已保留实际 Binding253 / Relations1224 及集成05既有正常 CI 身份，未重跑。

## 所有权修复的异常证据

已审 source-confirmed 风险是：旧 initializer 在可能分配/抛错的 Metadata() 前已让 finalizable SafeHandle 采用 native 指针，raw catch 可能先释放；之后 finalizer 再释放可能与地址重用相互作用。**没有把旧 unsafe ABA 写成运行中已复现事故。** 修复没有改变业务验证、native compile/status/null 和 origin 的相对顺序；metadata 与 wrapper 的内部 allocation/OOM 顺序发生明确变化，不能声称 OOM 出现位置相同。

本次只将当前106的 Plan/CTE cleanup 五行块与已运行 local03 的普通 base13b 对应块做缩进去除后的内容绑定，两块分别相同。local03 的单一 AOT ELF在独立故障进程中完成两 profile 共10个控制 /102 assertions；8个真正 native OK/nonzero 后的 Metadata/origin 错误各 target release1 /forward1 /duplicate0，最后 GC drain 后 owner恢复，2个 Encode故障未提交。local03完整 ELF带诊断和候选池；这些是共同 cleanup 机制的定向支持，不冒充 shipping106整 ELF 的 fault rerun。当前106本身的普通 CI与 ownership05真实包消费者另外绑定。

pool08的正常 Binding557、Relations1244、资源/故障控制均通过，但固定12普通格显示分配收益伴随 SQLite 首轮 material CPU/p99 回退和更高 idle RSS，故已选择拒绝08；这个选择不撤销独立 owner fix。当前合并无需带入候选特有池测试或诊断回调。

## CI 与独立包门禁

已直接读取固定 `observations/recovery/owner-cleanup-ci-jobs-success.json`。run **45995931048** 的11个 job均绑定head106：9项 success；`modules`、`publish` 按此次 PR 路径 skipped。Linux、PostgreSQL、SQLite三个独立 action job 和最终 Verify 均 success。root另行 GET确认run completed/success/event pull_request；本次 [ci-summary.json](ci-summary.json) 保留 fixed job receipt来源。**这不是合并后 main CI。**

已提交diff的既有 impact SHA `c7cc02e7bdca3b4a11a6e055feba54b044f9782ea746fe835868948bc9f8fc9d`，scope linux，packages/public_checks各包含 postgresql、sqlite，run_steps空，releases空。两顶层包独立验证，已有 native等累计原因来自05相对main的未合并差异。owner fix增量无 workflow、eng/ci或native改动；本次没有新增、调用或间接触发 CI性能任务。

如最终合并前head或tree变化，本报告不能自动覆盖新的产品内容。保持当前tree时，不需要为本报告另开完整性能 campaign 或重复已过正确性门禁；正常仓库保护规则仍由既有 CI/合并流程执行。

## 必须随交付保留的性能限制

历史 integrated05 的12格 zero-cost mixed中，成功180,000次，0拒绝/业务错误、owner归零，过程 CPU 与托管分配相对早期 Korda均下降；这支持保留既有收益。该 lane是30秒/500 offered ops/s，含 producer 的进程CPU比值1.2323–1.2807× Dapper并不能代表执行路径已接近。producer的自旋是共享计入成本，不能未经实测相减。

尤其 PostgreSQL queued/scheduled-to-completion p99相对早期Korda在两轮仍 **+26.238% / +17.593%**；service p99分别−1.075% /+8.247%，释放后idle RSS分别+7.310% /+9.869%。early-stop历史p99方向也不一致。不能把这些风险因后来拒绝06/07/08而抹去，也不能把它们重标成owner fix的效果。这些是保留05的已知性能限制，未观察到对应本批错误/归还契约失败。

最新固定related32普通观察的ownership05是含修复的实际新基线：CPU/Dapper SQLite两轮4.5614×/3.2197×，PG7.6097×/10.0480×；这些窄业务依旧有明显差距。PG服务端成本保持非原子visible-tree inner/outer窗口与独立wait4全寿命分列；原生分配、完整框架0B、调度指令精确归因仍不能补造。这里复用sealed08报告，不再运行性能工具。

用户已取消所有长测，包括before补测；不会将0个长测写成“待补的强制合并门禁”。当前性能没有全面对齐，仅重复得到支撑的资源/CPU指标可标相应改善。普通合并是交付已选择并验证的实现，不能把合并本身写成全目标性能验收完成。

## 正常交付待办范围

本报告不执行远端review/merge/publish。root可继续当前head的正常PR审查与合并；之后实际回读merge commit/tree、既有main CI、按仓库规则产生的两包版本和公共NuGet消费AOT结果。若它们失败，只处理对应具体门禁；本审查没有要求新测量、全量重复回归或额外批准。
