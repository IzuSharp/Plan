# 并行文档编制与整合政策 v0.1（proposed）

D01–D21分别拥有独占Design规范；D22–D31分别拥有独占Plan领域fragment；D32执行独立交叉审查。每个作者可以在证据仍进入时写draft。草拟、review_ready和accepted是不同状态，不能把先写的候选变成未经审查的架构权威。

## 版本与唯一权威

Design的契约registry是契约ID、version、status和内容hash的唯一索引。初始21个契约为`0.1.0-draft / proposed`。每个消费任务固定版本，不使用“latest”。变更契约须列受影响Task/Adapter/测试，更新精确pin并重新验证；有界影响通过局部ADR解决。

研究输出、Design正文、Plan任务状态各在自己的图与文件保存。不要在三张图复制同一份进度。root README和图是整合者负责的共享小文件；topic作者在自己的fragment提交变更。整合操作可能需要局部排队以避免同一文件冲突，这不阻塞任何其他topic研究或编制。

## 规范内容

每份重要规范须覆盖需求与非目标、真实场景、固定源码证据、候选比较、决定/未决项、模块职责、C# API、Rust/adapter接口、ABI布局、正常/错误流程、所有权、并发状态机、安全不变量、样例/最小验证、构建与AOT、成本、平台差异、兼容性、测试/失败注入和开发任务映射。代码按实际验证状态标记，不能用漂亮伪代码替代编译与运行。

Plan fragment必须给具体模块/文件、候选类型、正常/异常/竞争路径、真实依赖和Windows/Linux验收。所有领域均需实质编制，阶段B不是“未来再做”的Epic。

## Draft与接受依赖

`start_dependencies=[]`允许当前全部D任务开始draft。`acceptance_dependencies`只包含该规范所必需的研究/设计输入。D01桌面核心平台不等待整个移动R33；D11基础Engine不等待整个GUI/GPU R32；D13基准方法不等待领域参考应用R31。它们保留reference-only输入，未来profile在D21独立接受。

跨领域存在多种候选时，清楚标proposed方案及条件，交叉审查反例和成本。不得复制同一接口到不同文档暗中形成双权威。

## 交叉Review

第一层核查源码与结论，第二层检查ABI/生成/所有权/async/数据库/server/build相互一致，第三层由非主作者进行整体对抗性审查，第四层检查能否交给独立Codex按任务实施。审查含finding_id、证据、严重度、处置、修复与复验。审查者必须检查当前packet/spec hash，旧Review不能接受改过的新内容。

Draft PR可独立提交和review；只有本地门禁和实质审查均满足才能接受。图校验无法认证审查者身份或证明命令真的执行，必须核对实际GitHub审查、源码和日志。


## Source-driven amendment (2026-11-12)

NativeWeave独立于ArcForges，ArcForges只参考格式。C#是应用开发层，正式消费必须Native AOT。Database底层必须Rust，managed驱动只作源码/基准对照；Rust Server可选且需证据。优先源码驱动深度复用；普通新实体使用预编译native能力，不默认Cargo/CI。自然typed Fluent优先，不要求完整IQueryable/EF，不在C#重写SQL AST/方言。SG可选生成static metadata/DTO，不是唯一查询路径。Core只提供可组合ABI/lifetime/buffer/error/async，无巨型runtime。保留严格安全和生产验收，不授权大规模产品实现。

读取source-driven-baseline.json、同ID新packet和Design ADR-0002。独立Review检查新hash、backend拒绝、fallible binder、无逐实体Cargo、Server body/retirement、三图和未完成验证。旧Review不接受新内容；不增加规划层。
