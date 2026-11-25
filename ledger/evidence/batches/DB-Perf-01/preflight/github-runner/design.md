# DB-Perf-01：专用 GitHub Linux VM 执行路线（只读设计）

## 可行性结论

可以把八段计量放在**一个单独的 GitHub Actions `ubuntu-24.04` job**，在该 job 的一台 VM 上串行执行 8 × 1800 秒有效混合负载；常规 PR CI 保持短检查。建议 job 超时 330 分钟，给 240 分钟有效负载之外的输入准备、短校准、暖机、排空及上传留下最多 90 分钟。GitHub 官方当前 hosted job 上限是 6 小时，因此这个时间配置在平台上限内，但实际前置耗时必须通过准备阶段门槛确认。

这里的“专用”指本 job 获得一台新 VM，测量期间 VM 内不运行其他构建或负载；并不保证物理宿主机独占，也不保证不同 workflow attempt 获得相同 CPU 型号。官方当前公开仓库的 `ubuntu-24.04` 标准规格为 Linux x64、4 vCPU、16 GB RAM、14 GB SSD。应实测并记录当次 VM，不能只把规格表填进环境记录。来源：[GitHub-hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)、[Actions limits](https://docs.github.com/en/actions/reference/limits)，均于 2026-11-24 查询。

本设计没有修改或触发任何远端 workflow、创建标签或启动 runner。工具当前能读仓库/规则和添加 PR 标签，但没有暴露 `workflow_dispatch` 的调用入口；本地 `gh` 未证明有认证。普通 PR 事件由已连接 GitHub 工具触发是可用的设计路线，不需要先把测量代码合并 main。

## 已核实的仓库状态

精简 API 原始状态见 [capabilities-20261124.json](capabilities-20261124.json)，基线文件 Git blob、SHA-256 及行数见 [workflow-sources.json](workflow-sources.json)。

| 项目 | 已观察值及意义 |
| --- | --- |
| Korda main | `771bc77cbd68d3f932b99ed2497c0697bbba5f02`，本次重新读取仍相同 |
| 仓库 | public，当前连接返回 admin/maintain/push/pull/triage=true；这不单独证明任意 Actions 管理端点可用 |
| 默认分支规则 | `protectmain`，规则 ID 27094343，禁止删除与 non-fast-forward，无 bypass；不阻止正常 PR merge 或 PR 事件 |
| 自动合并 | `allow_auto_merge=false`；可用正常 merge/rebase/squash API，不应依赖 enable_auto_merge |
| 最近 main CI | [45356659607](https://github.com/IzuSharp/Korda/actions/runs/45356659607)，success；实际 build/publish jobs 的 runner group 为 GitHub Actions，label 为 ubuntu-24.04 |
| 当前批次远端 PR | `head=IzuSharp:task/DB-Perf-01-linux&state=all` 本次返回空；这只是读取时状态 |
| 自托管/定制 runner | connector 拒绝 `/actions/runners` 非白名单端点，不能由此推断不存在；当前路线使用已经实际成功的标准 hosted VM |

基线 `.github/workflows/ci.yml:3–17` 的 `pull_request` 未列 types，按 GitHub 默认只响应 opened/synchronize/reopened；另有 main push、merge_group、手动 dispatch 和定时触发。`build.yml:24–27` 当前普通模块 job 超时 120 分钟，不适合直接塞入四小时负载。独立长测 workflow 是更清晰的归属。

## PR 事件触发与剩余的标签前提

推荐新建 `.github/workflows/db-perf-01-linux.yml`，只响应 `pull_request` 的 `labeled`，并在 job 级严格限定：

- repository 为 `IzuSharp/Korda`；
- head repo 为同仓，head ref 为 `task/DB-Perf-01-linux`，base 为 main；
- **此次新增** label 名字为约定的 `db-perf-01-run`；
- 从 `github.event.pull_request.head.sha` checkout，冻结本次触发的 harness 提交，不跟随之后的分支移动；
- 只给 contents/actions/pull-requests 读取权限，不授予 id-token 或发布环境权限。

GitHub `pull_request` 官方活动类型包含 labeled，事件默认 checkout 的是 PR merge ref；所以这里要显式指定 head SHA。存在 merge conflict 时该事件不会运行，先正常解决冲突即可。与要求默认分支已有 workflow 的 workflow_dispatch/issue_comment 不同，pull_request 使用 PR merge ref 的定义；本方案据此在正常同仓 PR 中引入并验证 workflow。来源：[Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request)。

**标签存在性尚未证实。** 当前 GitHub connector 提供 `label_pr`，没有提供 `create_label`；`GET /repos/IzuSharp/Korda/labels` 被 endpoint allowlist 拒绝，历史 #19 的 issue labels 为空。官方 label 自动化示例要求标签已经存在，因此不能承诺任意新名字可直接使用。应在实际准备完成后，通过正常可用入口确认/创建标签，或选择已确认存在的标签并相应修改精确 gate。来源：[Adding labels to issues](https://docs.github.com/en/actions/tutorials/manage-your-work/add-labels-to-issues)。

若标签入口不能完成，现有工具有两个不依赖新标签的正常 PR 事件替代：

1. `types: [ready_for_review]`，由 `mark_pull_request_ready_for_review` 对准备完成的 draft PR 触发；精确同仓/分支 gate 不变。
2. `types: [edited]`，只有 PR 标题被显式改为带约定运行标记时才运行；用 `github.event.changes.title` 和精确标记 gate 避免普通正文编辑启动长测。由 `update_pull_request` 完成该显式操作。

这两种事件也不会触发现有默认类型的常规 PR CI。它们是普通仓库工作流入口，不需要读取、导出或伪造任何凭据。来自 Actions 内部 `GITHUB_TOKEN` 的标签操作通常不会再触发 workflow；应由当前外部 GitHub connector 施加明确触发动作，而非让 job 给自己加标签形成递归。来源：[Triggering a workflow](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)。

## Workflow 核心建议

下面是待实现的结构示意；`campaign.py` 子命令及相关 manifest **当前尚未实现**，不是已经可执行或已发布的 workflow。最终应使用团队确定的共同协议替换这些拟议接口。

```yaml
name: DB-Perf-01 Linux campaign
on:
  pull_request:
    branches: [main]
    types: [labeled]

permissions:
  contents: read
  actions: read
  pull-requests: read

concurrency:
  group: db-perf-01-linux-measurement
  queue: max
  cancel-in-progress: false

jobs:
  measurement:
    if: >-
      github.repository == 'IzuSharp/Korda' &&
      github.event.pull_request.head.repo.full_name == 'IzuSharp/Korda' &&
      github.event.pull_request.head.ref == 'task/DB-Perf-01-linux' &&
      github.event.label.name == 'db-perf-01-run'
    runs-on: ubuntu-24.04
    timeout-minutes: 330
    env:
      CI: 'true'
      BASELINE_SHA: 771bc77cbd68d3f932b99ed2497c0697bbba5f02
      HARNESS_SHA: ${{ github.event.pull_request.head.sha }}
      DOTNET_NOLOGO: 'true'
      DOTNET_CLI_TELEMETRY_OPTOUT: '1'
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1
        with:
          ref: ${{ github.event.pull_request.head.sha }}
          fetch-depth: 0
          persist-credentials: false
      - uses: actions/setup-dotnet@a98b56852c35b8e3190ac28c8c2271da59106c68
        with:
          global-json-file: global.json
      - name: Verify prepared inputs and capture VM
        run: python3 benchmarks/Database/campaign/campaign.py preflight
      - name: Calibrate and freeze load
        run: python3 benchmarks/Database/campaign/campaign.py calibrate
      # Expand into eight sequential segment steps in this same job.
      # Upload each completed segment before starting the next segment.
      - name: Run all eight frozen segments
        run: python3 benchmarks/Database/campaign/campaign.py run --effective-seconds 1800
      - name: Validate totals and publish local summary
        run: python3 benchmarks/Database/campaign/campaign.py verify
      - name: Retain all evidence
        if: always()
        uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a
        with:
          name: db-perf-01-${{ github.run_id }}-${{ github.run_attempt }}
          path: artifacts/db-perf-01/
          if-no-files-found: error
          retention-days: 30
```

`queue: max` 与 `cancel-in-progress: false` 允许单个仓库级测量 group 排队并避免新提交取消四小时测量；运行内仍必须固定事件 SHA。官方当前支持该组合。来源：[Control workflow concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)。不要使用 8 项 job matrix：不同 hosted jobs 会获得不同 VM；`max-parallel: 1` 只保证顺序，不能保证同一机器。

## 执行阶段与 330 分钟预算

| 阶段 | 必须完成的动作 | 是否计入 240 分钟有效负载 |
| --- | --- | --- |
| 输入准备 | 固定 before/after 两 provider 包、共同普通 AOT 消费应用、直接 C++、Dapper.AOT；逐一校验 package/executable/native SHA；依赖及 compiler 锁定 | 否 |
| VM 资格记录 | 实际 runner image、CPU 型号与 flags、affinity/cgroup、RAM、内核、时钟、磁盘和数据库/driver 版本；检查可用预算、背景进程、空闲 CPU | 否 |
| 短正确性/噪声 | 共同 SQL/参数/结果及持久化断言；交错独立进程测噪声；固定到达负载及错误率/尾延迟门槛 | 否 |
| 八段混合 | 四列 × PostgreSQL/SQLite；每段一独立消费进程、连续至少 1800 秒 effective；串行占用同一套 affinity 与资源 | 是，仅各段实际有效区间 |
| 各段间处理 | 排空、连接/游标/租约及原生所有者检查；空闲保留观测；复位相同数据；暖机；上传刚完成的原始记录 | 否 |
| 收尾 | 总时长/计数守恒、错误分类、八段清单和所有输入哈希，压缩上传及 Plan 入口 | 否 |

建议优先复用已通过独立 provider runner 验证、且输入/产物身份完全匹配的包，再在计量 VM 上发布同一普通消费应用。若需重新构建四个 provider 候选，应在准备 jobs 中按 provider 独立运行，并传递哈希绑定的 artifact；测量 job 开始后完成输入检查便停止所有构建。不能并发复用现有 `candidate-sqlite` 名字写入不同 before/after 产物：当前 build workflow 会 overwrite 同名 artifact，必须按 baseline/final 和 provider 区分来源或 run ID。

PR CI 默认消费 merge commit，长测 harness 则显式 checkout head SHA；输入清单应分别记录 harness commit、候选 package 构建 commit/tree、各包实际 SHA 和 payload inputs。不得误把 PR head SHA 当成包构建 SHA；正常合并后再核对公开发布输入是否与接受的候选一致。

在第一段开始前计算剩余硬预算：必须仍容纳八个完整有效区间、明确的各段暖机/排空/空闲预算和上传余量。准备或校准过慢就停止并保存未开跑的原因，不缩短 1800 秒或把暖机算进去。建议用软截止时间比 job timeout 提前至少五分钟收束，避免平台强杀时来不及上传。

为断点恢复，实际 YAML 应把每段与紧随其后的 artifact 上传展开为独立 steps，全部位于同一 job。每段结束写原子完成标记及 SHA manifest；没有完成标记的区间只算尝试。VM 被销毁后新 attempt 的硬件不能假定相同，必须重新做环境匹配；原始证据可保留，不自动拼成“固定机器 8 段”。

## 计量 VM 的实际限制

- **资源规格有限。** 14 GB 磁盘需在准备阶段检查：Clang、SDK、四个包与 AOT 输出、两库 fixture 和时间序列可能不足。可保留可复现输入并在进入计量前删除可再生成的编译中间物；不在测量中清理、安装软件或压缩大型日志。
- **同 VM 不等于无噪声。** 记录 CPU steal、背景负载与空闲基线，按预先设定的污染判据接受/拒绝区间；不能靠固定 `taskset` 宣称物理宿主独占。只在同数据库的四列间使用一致 client/server/observer 核分配；PostgreSQL 服务端与客户端分开计量。
- **数据库状态要复位。** 混合包含写入/回滚/冲突，必须使每列开始的 schema、seed、索引、统计、耐久性、隔离级别与热度等价；两库不能共用已经被上个路线更改的状态而不检查。
- **中断恢复有边界。** 已上传日志和 manifest 是恢复入口；尚未完整运行的段不能补记。不同 VM、不同二进制、不同负载或编译配置的结果不能直接沿用。
- **连接能力不是执行成功。** 未实际提交 workflow、触发事件及取得 runner，不能把设计可行写成专用环境已经运行。若 Actions policy/approval 自动审核拒绝后续动作，应保留具体拒绝原因再选择正常可行入口。

## 普通 CI、正常合并及自动 preview

新增 workflow 与 campaign 路径必须登记在模块 ownership/check 路由；基线 `eng/ci/modules/repository.json` 使用 workflow 精确路径，不会自动认可任意新文件。普通 PR 只执行受影响的正确性、短分配回归和普通 AOT 包消费；四小时负载不进入每次 synchronize 的检查集合。以 committed diff 查看 impact，修正路由遗漏或无关扩大后再提交。

main 发布继续使用现有规则，不通过长测 job 发布：`ci.yml:90–109` 要求 main push、Verify success、releases 非空与 `NUGET_PUBLISH_ENABLED=true`；`release.yml:18–26` 再次限制 main push 并使用 nuget environment。`release.yml:54–70` 校验产物与最新 main 的 package inputs，之后才登录 NuGet；`:84–122` 下载实际 registry 包、校验签名/字节并执行公开包 Native AOT 消费。包输入没有变化时应记录 registry planner 的 skip 理由，不能为了得到新版本强行改变包输入。

当前用户已经授权正常 PR、审查、合并及自动 preview 跟进。完成实现与测量、修复短 CI、正常审查后可按仓库规则进行普通合并，无需再让用户为本批已授权动作重复确认；但本只读设计本身没有执行这些动作。
