# Supplement05 alias mode 扩展：独立窄审

**最终 helper 279562ce / wrapper 5ad3c59b / manifest bc110a2e 未见阻断。** 实际六项全部有显式 mode：两个 ordinary native 为 0744，两个 correctness native 和两个包 cache 为 0644。四个 native 依赖来自已发布 archive04 的对应原 mode 成员；两个包来自本轮唯一 feed payload。相同 native 字节并未被误当成相同 mode。

对已审04的 helper 实际差异仅文案、可选 exact mode 检查、只允许 int 0644/0744（拒绝 bool/特殊位）、临时副本 chmod 后再核 mode/hash；旧 containment、no-follow、独立 inode、no-clobber、全部preflight和每文件安装语义不变。wrapper 仅导入新 helper、名称与 prior/current member mode 绑定；固定 streaming verifier b24e6dce 未变。

21 项合成 mode/链接/越界/不同既存字节控制全部过，源身份吻合；本审查未重跑。实际 check-only exit0、六项全部 verified-existing，绑定最终 helper/manifest、没有写任务文件。两个 prior expanded manifest 与 archive04 原文件和已发布回读 receipt 的 SHA/Git blob 一致；六个 alias 的 bytes/SHA/mode 都匹配其 selected 或 pinned prior 成员。

另回读现成 unified-stream-check：五组、748 members、2 current/4 prior aliases 全通过，未extract；package-path-closure 185项通过。它们的原始来源和当前 metadata 身份纳入本 validation。没有重读大 payload、重复压缩或实际恢复；不把check-only冒充完整空目录恢复。工具保持逐member而非wholearchive事务，不声称抗无关进程并发修改目的树。

可选 mode 为向后兼容，省略 mode 的旧条目沿用旧核验行为；此次六项都显式填写，不存在该模糊范围。依赖 archive04/既有 SDK/server/05/Dapper 的恢复顺序继续按原说明，05 本身不授予新性能或公共发布消费信用。本目录封存后不再改写。
