# Archive06：共同所有权修复与已拒绝 frame08 的有限增量

本目录当前是**元数据选择、空间预算及小源码 bundle**。尚未冻结文件集合，未压缩归档、上传或执行恢复；没有新增构建、数据库、业务、剖析或性能测量。此处仅关闭 frame08 候选，DB-Exec-Parity-01 的正常交付与其余有证据的优化问题由根代理继续处理。

## 选择和身份

根代理已接受独立普通短测审查，拒绝将 frame08 作为当前双库统一产品合入。12 个业务进程、24,576 次成功业务及另列的两个初始化进程均完成；正确性失败不是拒绝原因。四个配对的分配减少约60.8KB/业务（11.77%–11.78%），但 SQLite 第一轮 CPU +22.796%、p99 +29.480%，反向轮次没有重复净收益；四对五秒 idle 后 RSS 均增加。保留全部两轮原始数据，不追加 mixed、有利轮次、provider 分叉或长测。用户已经取消本轮所有长测，并不存在等待补长测的验收门。

| 身份 | 提交 | 用途 |
|---|---|---|
| 已测 ownership05 | `69b2383dadc280f1a81de592592a1442069eed0c` | integrated05 加独立 owner cleanup，两普通基线包的实际源 |
| 当前选中、已发布 PR 源 | `106fe68b6f6c2537f478daf65a71ab97cc4b15ff` | 与69b相同 tree `f7660759bba43ae83324620e2fb731efd479c3b5` |
| 已拒绝普通 frame08 | `13b25de2b67d858d8b6524f615e3a84b4c541817` | 共同 cleanup 加 Seal 私有 frame pool 与普通正确性测试 |
| 独立 local03 诊断 | `c429effc45c6fcd946c999553d0420b71369abfe` | 真故障位置及资源边界插桩，仅诊断，不入普通包或 CI |

`source-snapshots.json` 记录一个20,528B的已验证 thin bundle、四个 tip、基线2ea前置依赖及净 patch。没有复制整仓库，也没有修改源分支或共享 refs。原 pool-only749、cleanup cherry-pick b0a6、测试e1f/13b 均由 bundle 的提交链保留。

## 选择范围和预算

`selection-budget-01.json` 是可重算的当前草案；以其各文件 stat 清单和更新时间为准。六组分别保存闭合08证据、四个实际普通消费者、四个新 provider nupkg及构建回执、当前正确性编译产物元数据、支持记录和小源码快照。真实 ELF/DBG、生成C#、源/工程/还原身份、命令、原始结果、独立审查和失败 Relations01 都保留。

初次排除运行时副本后的草案约202.3MB expanded。压缩55–85MB仅是规划估计，尚无实际压缩数据；保守 tar 预算另列，不能把估计当实际大小。未来由根代理授权后才使用已经审查的单线程流式 writer，以 part 为单位保存，不另建完整 tar.xz 或解包副本。仍须实际校验每个 part、完整压缩/tar 流、展开成员及恢复路径闭包后，才能宣称归档闭合。

排除物包括可再建物理 PG/SQLite 文件、已批准删除的中间物、原 SDK/运行时的 bin DLL副本和旧候选载荷。现场未因本选择而删除任何文件。选中的 Korda 项目 DLL/PDB、obj响应/还原/生成文件和真实发布产物均单列；原运行时/编译器由已发布的前置归档提供。活跃的 `experiments/recovery/public-package-verification-13` 不在本轮冻结范围，根代理稍后单独保存真实发布结果。

## 前置归档和独立复制

`alias-source-plan-01.json` 保留原准备身份；`alias-mode-addendum-01.json` 纠正其中两项来源，最终以 `restore-alias-manifest.json` 为准。六个 unchanged native 目的路径复用 archives04 的 exact native04 字节；四个新 feed nupkg 独立复制到各自 raw cache 路径。普通 out 的源/目的 mode均为0744；Relations publish 改用 archive04 correctness-negative06 的原 publish 成员，源/目的均为0644。原严格 wrapper/helper 同时校验源与目的权限，完全不放宽；不把0744源误当可直接创建0644目的的已审路径。不硬链接，也不覆盖不同内容。

Binding fixture 已在 archives01 的原路径：`experiments/relations-recovery-03/fixture/build/fixtures/libkorda_query_binding_fixture.so`，1,220,120B，SHA `304912b696e96e673e9920fe04d70a80ff3f6c29d559b0b2f57c1490b83680a5`。旧 manifest 没有 mode 字段；本次不冒称其 mode已被该 manifest 验证。恢复沿原 tar 的权限，不新增猜测 mode 的 alias。

`package-path-closure-06.json` 将四消费者的16个实际包引用分成四个新 provider archive 和三个唯一的既有 compiler archive；后者绑定 archives04 实际远端回读的 expanded manifest。这里对照的是已封回执中的 SHA/路径，未重读大 payload。`dapper-dependency-closure-01.json` 已将两条 Dapper 各84个实际成员（包括ELF/DBG、17源、52生成文件及构建输入）匹配 archives01 的 matched-g-foundation03，并绑定当前实际命令与已过输入快照。SQLite实际加载的6,795,896B原生库也在该旧组；PG使用Npgsql，不声称Dapper加载libpq。这些成员未重新收大payload，也未凭目录名推定身份。

恢复顺序仍是前置 Stage1、archives01/02/03/04（依各自说明），再本次有限增量及显式 native/package aliases。archives05 的拒绝07历史已独立封存，不能当本次08源码，也不重复收其二进制。最终独立 archive06 恢复入口和完整验证仍待压缩授权之后生成。

## 历史生成文件的精确边界

普通 Binding01 在e1f构建，后续同工作树 Relations02 的13b测试修正重建覆盖了三个 AssemblyInfo 文件。Binding 原清单共30条：27条当前文件完全相同；另3条只在 `AssemblyInformationalVersion` 中含提交字符串差异。按一个精确行替换13b→e1f后，三个 sidecar 均严格匹配旧清单的完整 SHA256 与字节长度。独立审查已回读这三项。

这些文件单独保存在 `historical-generated/binding-e1f/`，标记 **reconstructed-byte-identical**：现在重构出与已封旧哈希相同的字节，不声称一直独立保留了当时原副本。当前13b源路径和 Binding原回执均未修改。`historical-generated-closure-01.json` 同时绑定原清单、当前输入SHA、精确替换及历史输出身份；Relations02 的66条、local03的30条当前源全匹配。以后查看旧build必须使用独立身份视图，不能让历史内容静默覆盖当前共享工作树路径。

## 信用与停止边界

Binding557断言/13 case（两 semantic profile ABI）、Relations1244断言/133 retirement（真实两库）、local03十个故障/102断言及资源99断言各自保留，不相加成统一业务计数。local03没有 CPU、延迟或 RSS信用；清零327,680B是实际长度与实现的清零范围加全零读回，不是硬件写带宽测量。普通短测审查2470项通过，不提供原生分配归因、开放到达率拒绝点或全面 Dapper 对齐结论。

源级确认的 inherited owner cleanup 风险已单独修复；旧 unsafe ABA没有运行复现。归档闭合与本轮拒绝08都不会把这个修复或整个任务取消。
