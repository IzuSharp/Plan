# 接受登记与证据边界

当前真实状态由三图及Design registry计算，汇总见ledger/reviews/D32.md和verification/completion.json。历史10R partial/24R planned、4D partial/28D draft只是接管时登记，不能掩盖原有17个完整triplet与16规范，也不能自动把它们当作接受。

研究接受：问题已由固定源码和必要真实实验回答，异常/边界和适用范围清楚，并有独立技术审查。设计接受：接口/状态/所有权/错误/平台/实现验收可据以开发，与研究和其他规范一致。产品接受：实际实现、目标环境和发布组合的真实验收；当前48Delivery全部尚未执行/未授权。

接受manifest绑定当前task revision/node+packet hash、来源Commit、依赖接受hash和选择快照；契约绑定版本/spec hash/实际review。只有证据记录不足以认证人员身份，因此同时保留真实子代理审查报告的具体输入与finding修复。子代理不是另一个GitHub审批账号。

任何hash/版本/依赖改变需要复核受影响范围，不能改hash掩盖旧review。所有实验失败、平台未运行和未来生产义务保留原貌；当前阶段接受数必须从文件实际验证得出，不能手写凑数。
