# Plan source lifecycle：10 份 packet 有界独立审查

**结论：通过；发现的 2 处语义问题已经由作者修复，并对最终字节独立复审。未解决发现为 0。**

审查者为本会话子代理 `/root/migration_evidence`，packet 作者为 `/root/plan_recovery`。这是不同作者的独立内容审查，不是 GitHub 另一账号的审批，也不是正式契约接受或产品实施授权。

## 范围与绑定

- Plan 基线及审查时 HEAD：`04c2f043c0ec60a2d49dd3ca8ea4ad1c8c888d89`；审查工作区包含尚未提交的候选修订。
- Design 读取时 HEAD：`670ffa0d9194661f9353fb177c64fab440592dff`。本报告绑定下面的实际输入哈希，不替代最终 Design merge / Plan baseline 配对检查。
- 只审 A03、A07、B05、B11、B13、B16、B17、B20 的实现设计，以及 B18/B19 的协议宿主限制。完整 graph/schema/host validator 由另一审查者负责。
- 本次没有修改 Plan，没有远端写入，没有重跑既有 native / AOT 实验。
- 作者冻结清单：`review-freeze-v3.json`，SHA-256 `dbc768ab2d2de47d0d8d2812995322ee7e6f4a3515ffcdc81a247dd8fd8a60aa`。
- 10 文件内容摘要：`13c4d99296acd6cf45d25bdff08177bf078eb2d9237e351adc6da0ed33f6a2bd`；编码算法及逐项检查见配套 JSON。

| Packet | Revision | 字节数 | 最终 SHA-256 |
|---|---|---:|---|
| A03 | 0.2.2 | 8316 | `bbc0a9b77b5d72797036bac10631f38731e77f7ccd1255586f986937045a315f` |
| A07 | 0.2.2 | 9068 | `8ba13c62a4ed4124920c90ff3358ce0fd29da487e0b98dc983fc2dac1e9d970b` |
| B05 | 0.2.1 | 8922 | `4eb76c29156e55bb5793976893803e28ce249b1a4e61a92669c539db6e3faa51` |
| B11 | 0.2.2 | 7804 | `ad401765d0cf501f82455000b9026fbc753985a0918634ff8f8f686ec2321452` |
| B13 | 0.2.2 | 6960 | `bb8fa8d02fcfb353187b8c283fdca3f591755b0e74f53ec84fccc4f6b2551698` |
| B16 | 0.2.1 | 9024 | `1b6827037b82da0d6fb9c7559a7009d599aeca761b1da75af549578c1b7b2f03` |
| B17 | 0.2.2 | 7839 | `0c55d08820feb0da75cbed4ee4bcfb32788ca06e76b0ad57d2e690183b3e9203` |
| B20 | 0.2.1 | 7971 | `fa5924f95b63c41a795ccac616e5d4a3c22b1b68cab293b730505dacc5f3bfcf` |
| B18 | 0.2.1 | 7867 | `fab37d5e458c4446f73131ff065b2dc821692b87994ebb9e70e81534e7fe395f` |
| B19 | 0.2.1 | 7902 | `cf867c4432a360cb6125d8532bd87823b57e2da88593dbe6320afd23b97f4f59` |

## 发现与修复

### PACKET-01 / A07：已转移结果不能因无人等待或重复通知再次释放

冻结 v2 把 take 后转换失败、Task 无人等待、重复通知并列为结果丢弃/释放条件，可能让实现释放已经转移给 Task 的 OwnedResult。D06 明确区分 native 未取结果、转换失败后的托管 wrapper，以及已交给应用的结果；没有 awaiter 也不能确定地回收最后一种。

作者在最终 terminal 段及测试表中明确：未 take 由 operation release；take 后 converter 失败由 wrapper 恰一次释放；成功发布的结果归应用 Dispose / 非阻塞后备及独立 held-result 预算；重复通知只锁存协议缺陷，不再次 take/free。审查者已复读修复内容并核验 `8ba13c62a4ed4124920c90ff3358ce0fd29da487e0b98dc983fc2dac1e9d970b`。该问题已解决。

### PACKET-02 / B05：Unknown 不能被清理用的 rollback 响应改写

冻结 v2 的末句只禁止 rollback 确认覆盖已证实的 commit，对尚未证实的 Unknown 留有歧义。D15 要求 Unknown 后的 cleanup rollback / 无活动事务响应只能更新清理与连接处置，不能证明先前 COMMIT 未发生。

作者已限定：从未 dispatch COMMIT 的 rollback 确认，或可信绑定原事务终态的恢复证据，才可确立 RolledBack；Unknown 的细化必须基于身份绑定恢复证据。审查者已复读并核验 `4eb76c29156e55bb5793976893803e28ce249b1a4e61a92669c539db6e3faa51`。该问题已解决。其余 8 份 packet 与冻结 v2 字节一致。

## 逐项语义结论

| Packet | 审查结论 |
|---|---|
| A03 | 同一短 gate 内检查 Open 并 AddRef，锁外 FFI / finally Release；关闭后拒绝新业务，旧租约仍可完成；父子与线程亲和释放责任没有被 SafeHandle 引用计数替代。 |
| A07 | native 终态、native retirement、setup、registration drain、managed call/callback 租约分别收敛；停止等待不释放仍受访问的 context；最终结果所有权按修复后的四类路径处理。 |
| B05 | 事务效果、连接协议/返池资格、本地回收相互独立；提交未知不自动重试，Drop/清理/超时不证明回滚；真实 SQLite 实验与未来 PostgreSQL / C# AOT 要求分开。 |
| B11 | SeaQuery AST 与方言归 Rust；C# 只提供描述符和调用；single writer、owner 匹配、seal/poison、fallible binder 与 capability 检查先于执行。 |
| B13 | 手写 metadata 与可选 SG 都可消费同一预编译 native；新实体不要求 Cargo；参数快照、owner/alias 检查及 DTO 异常清理责任明确，没有新增 C# SQL AST。 |
| B16 | retained allocation 预算独立于 queue slot；共享 owner 的非空 slice、已有 permit、等待者与 Closing/retirement-pending 槽继续计费。Body None 只表示 EndObserved，不能制造 transport 正常完成证据。 |
| B17 | Rust host 仍 undecided；复用 Hyper/Tokio 等候选实现及 A07 退休协议；header / Future 完成不结束 body/owner，runtime timeout 不证明静默；完整 managed handler、网络/TLS、AOT 验证仍待做。 |
| B20 | 关闭先停止准入，再按各 owner 的屏障排空；调用方停止等待不等于执行终止、SQLx ack 不等于线程 join；待清理 roots/预算继续保留；有限计数归零不证明进程 RSS 已回收。 |
| B18/B19 | 当前 D19 是 managed Kestrel-specific，不能直接作为 Rust 协议 adapter。Rust-only 需要另行 accepted 的 profile；双 host 可以明确协议只支持 Kestrel。协议不能暗中决定产品 host。 |

## 证据与授权界限

D04 的主同步准入证据沿用 PR8：run `43373306474`，源提交 `28f6cf7e6e4e80b9f32a92ad587a528d82911bd0`，Windows/Linux 普通及 Native AOT 执行各 653 断言和 64 轮受控 gate 竞争。它不能代替 A07 完整异步 retirement 或产品验收；此前本代理的 Linux 补充复现不作为新增覆盖。

D15/D18 的 source lifecycle 证据沿用 run `43375871731`，源提交 `de43481581df9876cb2d0aed5de2db796d048c9d`：4 个成功 job、12 个不同 native 测试、24 次平台测试执行。它们不是完整 C# adapter/AOT、PostgreSQL 故障、HTTP/2 网络或 RSS 验证。此前独立 artifact 审计保存了 5 个 Database Windows 输入的实际 LF→CRLF 转换及双方哈希；本报告没有把这些 checkout 字节误称为原始 git blob。

10 个 packet 的 status、acceptance_evidence、independent_reviewers、implementation_authorization 均与基线相同；全部仍为 `planned_candidate` / `not_authorized`。B15/B17 两个 host 和 B18/B19 协议选择仍 `undecided`，required contract status 仍为 `accepted`，实际所读契约仍 `proposed`。

D19 当前没有 accepted 的 registry 内容 hash，也没有 `nativeweave-protocol-host-profiles-v1` 机器声明。因此 B18/B19 的产品启动前置条件仍不成立，这是明确保留的未完成条件。该内容审查不把文字候选当作 accepted profile，也不声称已独审 validator 实现。

关键 Design 输入（完整 12 文件哈希及 registry 快照见 JSON）：

| 输入 | SHA-256 |
|---|---|
| `docs/contracts/lifetime-v0.1.md` | `d527369dfd97a2d97ecd0930e25effc523791eb5e22586b1d9e18ac6f4aa31c9` |
| `docs/contracts/async-v0.1.md` | `8f09504a07632fe53ca6e5d2861cf70a3c2d7cea9ff1e4e3035a6a8beaec8672` |
| `docs/database/transactions-and-pooling.md` | `34788328a967205b6d139aa4d613fdb224cde1bf3dca5f4784acc4eb18c09cce` |
| `docs/server/body-retirement-protocol.md` | `d2aa6bc99a89665726a806ef580c777eb4ae8af181397ed6e827cc2560a52a15` |
| `docs/server/hosting-and-streaming.md` | `9acf2b3bd464815ac0bb66700ee0c5c8791fa3772f7b0fbe54736e59e2f47358` |
| `docs/server/protocols-and-observability.md` | `36fec912e6e9511fc28dddb03c06888f07c9c2286e761074c90ffdc09d24c6d9` |

机械绑定核验共 77 项全部通过。这些是文件哈希、选定节点字段与已有证据 manifest 的只读检查，不是新增 native 测试数。

**有效范围：仅上述 10 份 packet 的精确字节。内容变化后需更新本有界审查；本报告不替代完整图/schema/host validator 审查、最终 pair pin、GitHub 强制检查、契约接受或产品阶段授权。**
