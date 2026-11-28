# 02 Dapper PostgreSQL：业务窗口有效，释放后idle存在实际偏差

## 结论

本轮由 `/root` 与 `/root/baseline_recovery` 两个助手分别读取原始证据并复核。**原冻结runner的strict状态继续保持failed，原因仍是released_idle。** 仅对绑定下列精确Hash的这条证据，派生 `business-valid/idle-deviation` 分类：1800秒业务窗口可作描述性比较，释放后内存必须按实际14.997119729秒标注，不能写成满15秒。

这不是新的用户人工批准，也没有更改原规则或为其他格加入毫秒容差。未来其他格若出现同类偏差，需另行逐条核实并保留各自原状态。

| 证据 | SHA-256 |
| --- | --- |
| 原result.json | `61f45dae1a6a687298e87e81bdae689fa26a9aae88cd25a60d62e8368de6a50c` |
| 原cell-status.json | `9576fc157dbcc8acae8b4515f78ec1f5fe901be8e7379f9d7203d73da32e82c4` |
| 本条结构化评审 | `ef2ea3d6f6d7c6afcdab6f64476b45f1d4ff6e84eab45a8e70cb5a2da604d44d` |

## 真实时间与严格判定

| 时间字段 | 原值或精确计算 |
| --- | --- |
| 请求idle | 15秒 |
| Stopwatch实测idle | 14.997119729秒 |
| 严格15秒短缺 | 0.002880271秒＝2.880271毫秒 |
| UTC起点 | 2026-11-28T09:35:42.5668336+00:00 |
| UTC终点 | 2026-11-28T09:35:57.5639753+00:00 |
| UTC经过时间 | 14.9971417秒 |
| UTC比单调时长多 | 21.971微秒 |

两种时钟均显示未满15秒，远大于JSON数值显示舍入误差；不能把ObservedSeconds直接改为15。冻结runner要求RequestedSeconds=15且ObservedSeconds≥15，原判定确实命中。

Dapper原始实现先完成业务计时与worker/session/source drain，再记录idle起点，执行一次 `await Task.Delay(TimeSpan.FromSeconds(options.IdleSeconds))`，随后记录Stopwatch终点。它没有按Stopwatch截止时刻再次等待补足。现有证据只能确认Task.Delay返回后，该Stopwatch区间实际少2.880271毫秒；**没有对runtime/OS定时器机制开展测量，不能断言具体误差原因。**

## 业务验收独立成立

结构化JSON中的34项检查全部通过，覆盖精确到达数、完整drain、零业务/Oracle错误、35类与原manifest预期oracle、直方图人口、每秒/每类计数、monotonic窗口、连接归还、fixture恢复、PG正常退出及Hash绑定。

| 业务项 | 实际值 |
| --- | ---: |
| 请求业务时长 | 1800秒 |
| EffectiveSeconds | 1800.004439463 |
| Planned／Attempted | 6,480,000／6,480,000 |
| Succeeded | 6,470,481 |
| Rejected | 9,519 |
| Failed／OracleFailures | 0／0 |
| 客户端退出／observer错误 | 0／0 |
| 连接归还、全部持久数据恢复 | true／true |
| 原消费者TimingComparisonEligible | true |

这段idle在业务CPU/分配与耗时边界之后；因此不会把1800秒计时缩成1799.997秒。原始idle RSS Before=36,454,400B、After=36,499,456B，必须连同实际idle时长报告；无强制GC，不据此判断泄漏或无泄漏。PG整库steady进程枚举缺口仍按单独覆盖政策保留null，不被本条评审豁免。

## 最小处理与恢复位置

保留原result、status、命令回执、退出码和严格失败事实；不改冻结runner/matrix、客户端或历史结果，不为该2.88毫秒偏差重跑30分钟。以原冻结runner的 `--only` 入口依次继续后六段，每段仍执行原严格判定。

离线分析器只通过这条精确case名＋result/status Hash＋本review文件Hash识别上述分类；若出现任何额外业务/证据错误，或任何Hash变化，不给予分类信用。全八格结束后再生成综合分析，严格状态与业务比较资格分开显示。
