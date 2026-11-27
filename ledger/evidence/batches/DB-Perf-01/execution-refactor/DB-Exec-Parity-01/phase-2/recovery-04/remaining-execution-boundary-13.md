# 剩余千行 CPU：优先补哪一个边界

**首选补“批次需求 → 执行器开始 → 完成发布/await 恢复 → 下一批需求”的请求级归因，把这条链与实际 ThreadPool 工作信号量等待配对。** 现有证据足以说明这值得观察，还不足以选择一个新的产品改法。本条没有新测量、构建或实现。

已证明：phase1 的热 Prepare 和 Host SQL 都保留千行 CPU 放大，PG额外托管分配只有约550 B，SQL工作和网络字节差异解释不了总差距；Worker-D 保持32批，将 native posts34→2，同时 C ABI调用104→136，说明改动针对线程交接，不能按FFI次数推成本。money1实际栈及机器码把9,350个样本核到 WaitSlow→Backoff→Thread.SpinWait→RhSpinWait：主要路径是ThreadPool取得工作信号量前的等待，不在decimal decoder内。旧同ELF spin0已有显著净CPU敏感性，重复它不会补齐请求归因。[1–3]

**仍未知：当前保留05的千行请求中，哪个批次/唤醒者使哪些线程进入这段等待、这些线程随后做了什么，以及其中多少CPU属于必要执行、闲置worker乐观自旋或重入/交棒。** money1是单行采样；phase1时间线属于旧执行身份；两者不能拼成当前05的排他CPU账。约33个managed offers也不是33次已证明的OS唤醒。06、07的结果已否定其具体EOF/局部队列策略，不能据此证明所有执行器调度成本都不可消除。[2–4]

若以后补这一边界，应只给同一request/batch/generation关联需求提出、offer、Execute起止、native run/ready/take、完成发布、consumer恢复与下一次Pull；记录两端TID、同TID线程CPU和计数。将“还有可运行工作”“等provider/consumer”“工作信号量等待”分开；内核park/wake不可见就留未知，重叠span不相加。目标是回答**每一批是否都重新唤起/闲置执行器，CPU是否真的集中在该往返**，而非再次给RhSpinWait一个百分比。

只有这条因果链成立，才值得评估**按查询保有的有界串行执行状态与需求合并**，改变执行器的唤醒/重新准入粒度。继续保留32行、按需取下一批、首调用never-inline、代际取消与唯一完成、mapper借用、EOF/安全关闭及公平让步；不恢复整体inline、单改queue locality或运行时spin开关旧方案。若主要CPU落在native逐行结果/解码，则按实测转向该段，不预设“调度一定解释全部”。当前合并和发布只交付已证实的05及独立所有权修复，不代表全面对齐。

依据（任务相对路径）：[1] Plan `phase-1/phase-1-measured-gate.md`；[2] Plan `phase-2/recovery-04/worker-counts-04.md`；[3] `experiments/sampler04/caller-findings-04.md`、`caller-findings-addendum-04.md`及`experiments/runtime-spin-dedup-08/README.md`；[4] 已封tail06 mixed与pull-local07 ordinary独立拒绝报告。Plan路径均位于本任务DB-Exec-Parity-01证据目录。
