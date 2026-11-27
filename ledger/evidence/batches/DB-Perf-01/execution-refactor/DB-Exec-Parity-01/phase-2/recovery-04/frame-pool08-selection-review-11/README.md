# frame-pool08 正式选择：Plan / Design 独立窄审

**未见阻断。两份正式文本完整保留已审的单一资源假设、硬条件、成本及有限验证边界，没有夹带其它方案。** 当前只选实施/验证，不宣称 adopted、安全实测或收益；基线仍2ea integrated05，tail06/07拒绝、长测取消。

核对12份原样来源/索引：原件与Plan拷贝 bytes/SHA一致；没有重复Git blob获取或大payload散列。Design旧Continuation09标题下的完整尾部逐字节不变，旧授权前言不变；新增11段覆盖关闭07及本次新选择，两entry README状态准确。

保留条件包括：只Seal且4096<size<=65536；首次eligible才建私有Create(65536,4)；原stack/Render/CTE/小大fresh路径不动；原分配位置/额度/错误序；单一Seal词法owner和Encode前finally、无heap lease、descriptor不Dispose；显式logicalLength和reserved写零；同步Compile/metadata/origin结束后同池一次clearReturn。完整tape复制/fixup/sidecar不变。

成本未遗漏：65560B冷数组及5056B增量、首次池元数据、实际65536B清理（桶满丢弃也清）、SpinLock、491520B缓存payload界限不是RSS/活动内存界限、四槽不是并发限额、静态无trim。没有把少分配直接宣布CPU/内存收益或text1000解决。

有限验证保持边界/dirty完整frame、获租后失败、native error/null、held借用、poison后真实plan执行、public snapshots及现有relation回归；metadata/origin人为故障可独立标识本地测试构建，不增加shipping全局callback、不强制OOM。计数和计时诊断仅本地，CI保持既有正确性/安全/AOT包路由，不含性能campaign。首轮预定12个related32短进程，后续mixed只为具体未解风险，无自动扩矩阵/长测。

Design当前Plan11 URL按root说明仍指任务branch；发布Plan后只替换这一处ref为精确remote SHA并另存link-only身份即可。本审查不替代发布/CI结果，也不授权审查者编辑产品。本目录封存，不会继续改写。
