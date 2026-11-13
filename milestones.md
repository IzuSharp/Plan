# 既有任务的并行里程碑

当前里程碑是完成34R/32D及成熟48Delivery说明，不执行产品。研究实际顺序：核心ABI/所有权/async与平台；并行数据库和Rust服务器源码/实验；继而跨领域性能/打包/未来Engine/整体审查。此顺序只是现有任务执行排序，不是一张新图或全局串行锁。

未来得到产品阶段授权后：

| 可并行工作 | 后续解锁 | 验收归属 |
| --- | --- | --- |
| A01布局、A19模型、A21基准工具、B01共享Data seam | Core局部模块、原生provider和查询绑定 | 各组件真实代码/证据 |
| A03–A12局部Interop/生成；B02/B03/B05/B06/B07/B09 | A17/A18真实Engine、B04 Host、B11/B12/B13 | 真实原生/AOT组合 |
| B15 C#应用、B16流组件、B17 Rust Host | B18 Tonic、B19 rmcp、B20诊断 | 原生网络/协议/释放 |
| A14/A15平台与A16包；B21完整参考服务 | B22故障/soak、B23性能、B24领域发布 | 独立NuGet、clean no-Rust、双OS、实际DB/网络与长期资源 |

以delivery-graph.json精确边为准。A/B不是必须全阶段串行完成的墙；未使用某个可选Core能力的Engine不启动该runtime。GUI/GPU/mobile边界按D21，不把未来硬件/平台认证压到普通Windows/Linux开发前。
