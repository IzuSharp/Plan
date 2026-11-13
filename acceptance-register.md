# 接受登记与证据边界

当前真实状态由三图及Design registry计算，汇总见ledger/reviews/D32.md和verification/completion.json。历史10R partial/24R planned、4D partial/28D draft只是接管时登记，不能掩盖原有17个完整triplet与16规范，也不能自动把它们当作接受。

## 2026-11-13 正式研究设计接受

| 范围 | 当前状态 | 权威记录 |
| --- | --- | --- |
| R01–R34 | 34 accepted | research-graph.json、ledger/acceptance/R*.json |
| D01–D32 | 32 accepted | documentation-graph.json、ledger/acceptance/D*.json |
| 21 个 0.3.0 技术契约 | 21 accepted | 固定 Design 的 docs/contracts/registry.json、acceptance-index.json |
| A01–A24 / B01–B24 | 48 planned_candidate / not_authorized | delivery-graph.json、48 份 tasks、10 份 fragments |

Design 输入为已合并的 `08e3aaee73aad174620dcff18ed21b3b14c5e632`；Plan 任务语义和文件输入固定于 `c3947b378e0a251f8dfeaf7fd7d4acc636631974`。各任务的状态、接受记录本身与原始输入 Commit 分开，避免自引用哈希。正式 task index 为 [ledger/completion-acceptance.json](ledger/completion-acceptance.json)，三位实际独立执行者的最终确认在 [ledger/reviews/final-2026-11-13/](ledger/reviews/final-2026-11-13/)。

完整校验验证 840 个输入条目（契约 266、R/D 任务 574）、114 个 packet、10 个 fragment 和实际 review/attestation 链。被接受的是现有研究结论、详细设计和未来实施指导；没有将原生研究切片复制成产品验收结果。PR 和 exact-head CI 的最终外部记录见 [Design #10](https://github.com/IzuSharp/NativeWeave-Design/pull/10) 与 [Plan #8](https://github.com/IzuSharp/Plan/pull/8)。

## 接受语义

研究接受：问题已由固定源码和必要真实实验回答，异常/边界和适用范围清楚，并有独立技术审查。设计接受：接口/状态/所有权/错误/平台/实现验收可据以开发，与研究和其他规范一致。产品接受：实际实现、目标环境和发布组合的真实验收；当前48Delivery全部尚未执行/未授权。

接受manifest绑定当前task revision/node+packet hash、来源Commit、依赖接受hash和选择快照；契约绑定版本/spec hash/实际review。只有证据记录不足以认证人员身份，因此同时保留真实子代理审查报告的具体输入与finding修复。子代理不是另一个GitHub审批账号。

任何hash/版本/依赖改变需要复核受影响范围，不能改hash掩盖旧review。所有实验失败、平台未运行和未来生产义务保留原貌；当前阶段接受数必须从文件实际验证得出，不能手写凑数。
