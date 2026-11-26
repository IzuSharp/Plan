# 当前候选的 CI 与公开包复核

审查对象是公开提交 [17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa](https://github.com/IzuSharp/Korda/commit/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa)，不是先前失败的 `cb233a7a`。本记录由 evidence_ci 独立只读核对；没有启动构建、数据库、消费者或性能负载。

## 源码身份与打包修正

GitHub Git commit API、PR #37 head 和本地对象一致指向 tree `bc9087d843d8d741d83d44f53d0b2c5af26dcffc`。根工作树 HEAD 是 `040911c5abdee740c0cd9fbf8295bf511c9cc69d`，tree 与公开提交完全相同，工作树干净；提交身份不同，不能把两者写成同一 SHA。基线 `origin/main` 与公开 PR base 都是 `e063f2eb6e2e857e3f19f96bf263cae372651a27`。API 快照保存在 [current-ci-review-evidence](current-ci-review-evidence/)。

此次后继只修改 [inventory.py](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Packaging.Domain/inventory.py)：把 `find-shape-v1.json / bit 29` 加入已经存在的扩展签名循环，仍检查版本、capability bit、[模型 capability 名称](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Packaging.Domain/model.py)，再交给既有严格 ELF 导出集合检查。没有改动或绕过 `NWPKG005`。

只读 `readelf --wide --dyn-syms` 对两份旧候选 ELF 的结果相同：实际导出 63 个，旧 inventory 预期 62 个；唯一额外导出是 [Find 扩展声明](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/database/binding/find-shape-v1.json) 中的 `nw_db_find_plan_create_v1`，没有缺失项。加入此声明后预期集合与实际集合精确相等。这解释了旧候选失败，也支持此次修正的范围；它不代替新候选的完整消费验收。

## 实际 impact 与现有路由

两个全新 provider worktree 均执行了要求的原命令：

```sh
python3 eng/ci/impact.py origin/main --output artifacts/plan.json
```

本次独立复算把输出放在仓库外 `/workspace/scratch/fd78534029f7/ci-review-17da-01/plan.json`，exit 0；其完整字节 SHA-256 为 `c29d60281cef458688a223c3923692d594318503d0a649d78430652dd26b5635`，与两份 `candidate-*-02` 的实际计划相同。完整计划和 whitespace 输出也在失败证据压缩包的 `review/` 内。

| 独立 worker scope | 实际选中的现有 actions |
| --- | --- |
| interop | `interop.async`、`interop.callbacks` |
| linux | `database.native`、`database.build`、`database.api`、`database.dependencies`、`database.regressions`、`fluent.api`、`api.tool`、`migrations.api`、`relations.api` |
| postgresql | `postgresql.build`、`postgresql.dependencies`、`public.pack`、`postgresql.packed-api`、`postgresql.test`、`public.consume-aot`、`public.validate` |
| sqlite | `sqlite.build`、`public.pack`、`public.consume-aot`、`public.validate`、`sqlite.dependencies`、`sqlite.packed-api`、`sqlite.test` |

`build_scopes=[interop,linux,postgresql,sqlite]`；`public_checks` 和 `packages` 都是两个 provider；`modules=[]`、`module_packages=[]`、`run_steps={}`、`releases=[]`、`deep=false`。与修正前实际计划的 actions/scopes/public checks/run steps/packages/releases 全部相同。

选择原因能由 [模块登记](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/eng/ci/modules/database.json) 和 [现有 action 实现](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/eng/ci/modules/database.py) 解释：共享 database/native/Packaging.Domain 源码沿依赖图触达两个顶层 provider；interop、Fluent、migrations、relations 及契约测试的实际 diff 选择相应检查。provider 各自构建、核对依赖和打包 API、执行测试与独立公开 AOT 消费。不是由 benchmark 执行入口触发这些检查。

[ci.yml](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/.github/workflows/ci.yml) 相对 main 未改变，继续按 `build_scopes` 并行、`fail-fast:false`，最终 Verify 汇总。相对接续点 `47fe650dfed5d7bba1c4d74c4a127c5d08b66082`，整个 `.github/workflows/` 和 `eng/ci/` 都没有新增 diff。

PR 相对 main 已有的 CI 改动属于此前历史：build.yml 多保留 provider 失败日志；release.yml 多保留实际 registry 字节和公开消费凭据；worker.py 为 PostgreSQL 测试初始化显式 UTF-8。两个 benchmark 模块 JSON 只有 `tests` 归属，没有 `run/checks/package` 或性能命令。没有新增性能 workflow、job、按钮、定时任务，也未把负载放入普通检查或发布脚本。原有周检、手动完整检查和安全检查保持原用途。

PR 事件没有发布资格。既有 publish 门仍要求 main push、Verify success、非空 releases 及 `NUGET_PUBLISH_ENABLED=true`；合并后的实际 fingerprint/版本与发布运行需要另外核对，不能从此 PR 计划推断已发布。

## GitHub 当前运行

- [17da CI 45772470391](https://github.com/IzuSharp/Korda/actions/runs/45772470391)，run 270，`pull_request`，创建于 2026-11-26 07:03:11 UTC；最新本次读取状态为 `in_progress`、conclusion=null（run updated 07:09:58 UTC）。plan、Secret scan、Dependency review 已 success；四个预期 build scope 与两种 CodeQL 在进行中；modules skipped。当前没有 CI 成功或合并资格结论。
- [旧 cb233 CI 45772036144](https://github.com/IzuSharp/Korda/actions/runs/45772036144) 已在 07:09:38 UTC completed/failure。interop、linux、plan 和安全检查 success；两个 provider 在既有 `public.pack` 阶段都报 `NWPKG005`，Verify failure，publish skipped。两份远端 job 完整日志保留在证据目录，不能用旧候选其余绿色 job 抵消失败。

## 两次本地独立构建的证据边界

旧 `candidate-sqlite-01`、`candidate-postgresql-01` 都绑定 cb233/tree `0ea8d431f2d322dc9278e516da99d084413add7f`，四阶段 exit 为 `impact=0,native=0,native-correctness=0,bundle=1`。SQLite 原生门 2/2、PostgreSQL 原生门 1/1 通过，不等于公开包验收通过。现场逐项确认两者没有 nupkg、public/feed、release.json 或消费者产物。

[failed-candidate-cb233-01.tar.gz](current-ci-review-evidence/failed-candidate-cb233-01.tar.gz) 原样保留两份回执、全部 build 输出日志、CMake/ctest 日志、native manifest、compile_commands、计划与构建器，共 32 成员、171500 B，SHA-256 `806e16034f681c8f53098fc321a7c05494a2d3c965de7c69be355e813d6b61a9`。进行了确定性双编码、全成员读回及每个原件重读比较；[manifest](current-ci-review-evidence/failed-candidate-cb233-01.manifest.json) 列出全部来源与哈希。旧 ELF 留在原路径并记录哈希；未把后继构建的进行中日志塞入此归档。

后继 `candidate-*-02` 在各自全新 `/tmp/DB-Exec-10-pack-{provider}-02` 产生。已读取两份完成回执，均绑定公开 17da/tree bc9087、sourceDirty=false，八阶段都 exit 0：impact、native、原生正确性、bundle、公开 AOT 消费、公开 validate、外部 query-phases AOT 构建、外部 workload AOT 构建。

| Provider | 完成时间 UTC | build-receipt.json SHA-256 |
| --- | --- | --- |
| SQLite | 2026-11-26 07:06:54.157121 | `1b9f8a60c7101a2cd4de88de6eb58c5b97c9b881459d6b682a268fcafe9adba2` |
| PostgreSQL | 2026-11-26 07:06:54.211513 | `d51a05735602b2edac46f1171da4c89395b1df2f1731e9bb4ed84d30129c5dfa` |

上述成功结论是对完成回执和既有阶段输出的复核。本审查中进一步重用离线 helper 的临时调用缺少 `reader.load_helpers(repository)` 初始化，在第一组 reader 处以 TypeError 退出；没有产品运行或产品报错，也没有生成虚假的完整身份核验成功记录。此时主线程进入串行测量准备，故停止继续全量哈希/压缩。下一空档补完 source → release/nupkg 全条目 → native → 外部 ELF 的独立闭合核验及成功输出归档；最终冻结 gate 仍必须通过，不能由这里的回执摘要替代。所有本节记录的 performanceCredit 均为 false。

## diff-check 范围

`git diff --check origin/main 17da...` exit 2：36 条既有 trailing-whitespace，分布于 12 个文件（当前 Dapper/Oracles.cs 一处，以及冻结 reproduction-inputs 原件/patch 中的其余位置）。完整输出 SHA-256 `4e7134c872da2a9ea7ccf55922db43aa82edabb7daea39ffe448f5de68e8b12a`，与 `origin/main..47fe650...` 的结果逐字相同。

`git diff --check 47fe650... 17da...` exit 0、无输出；本接续 diff 干净。没有改写历史证据 bytes 来清除此观察。`ci.yml` 中无参数的 `git diff --check` 检查工作树 diff，不应描述成已验证整个历史 PR 相对 main 无 whitespace。

## 测量空档补完：后继产物身份闭合

2026-11-26 07:14:40.537768 UTC，在 SQLite phases 结束且主线程明确确认无 measurement process 的空档，补齐 reader 初始化并完成两路独立只读核验，实际进程耗时 0.78 秒、exit 0。此前 helper 初始化失败观察保留；本次结果独立记录为 [completed-public-builds-17da-02.json](current-ci-review-evidence/completed-public-builds-17da-02.json)，SHA-256 `f0595d46fe40af1c8c8ee9f1b2dae2483fe2e3ddb64c7d1ccd0046c8b03b706e`。

- 两个 producer checkout 都是准确公开 17da、tree bc9087、干净；每路 120 项原生源码输入以及 compiler/installed/output 三处 native 字节与原生 manifest 一致。
- 逐项重核八阶段 exit/sourceUnchanged/log 哈希、构建器、impact、native/release 回执；每路只有一个独立顶层包，NuGet dependencies 为空。
- release、nuspec commit、准确 nupkg 字节和全部未签名成员闭合：SQLite 40 项，PostgreSQL 41 项；包内 native 与 workload/query-phases 发布目录中的 native 完全相同。
- 两类外部消费者均为 Release Native AOT/Linux x64，无 ProjectReference；核对实际源码与 17da 的 harness、项目/配置/资产图、发布日志和 ELF。workload 每路 65 个实际生成源文件进入身份记录；phase 的 Program.cs、项目与目录属性匹配固定源码。

| Provider | nupkg SHA-256 | workload ELF SHA-256 | query-phases ELF SHA-256 |
| --- | --- | --- | --- |
| SQLite | `059a0df6b2ed428788b2bf5a7212dd4d73d43cd642eee0de152b975efaf03d6a` | `1ce8d74112e6dff217bb69d39c1f939474d04617b4f7961fb4e9b7edc5bf8953` | `b8006d36928a594439f335cae3837a4ef1a6db71ea24e88d6d756c52b480cc92` |
| PostgreSQL | `46d5757c6dc48c721167476e2975f025b6884dc0c54b6956b9677a8eb4b29dec` | `3e22e2ce1e9912f190b643b172360539d25d1b0558de3a253a3c19a67726c0b8` | `618175683cf5b68c0e53b9423957c6c3c60de1d9067a74f59e0b89a01a1324fc` |

只复制 [completed-17da-02](current-ci-review-evidence/completed-17da-02/) 内 28 个小回执、manifest、计划和阶段日志，共 522996 B，复制后按字节比较；没有压缩完整消费者或复制大产物。核验完成后立即通知主线程可继续 PostgreSQL phases。没有运行产品、构建或负载，也没有性能信用；最终 load plan 的冻结及运行后 gate 仍另外执行。本次远端复读 CI 45772470391 仍为 in_progress/conclusion=null。
