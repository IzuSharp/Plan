# DB-Exec-02 执行路径测量分析

本报告只重算原始证据，不运行测量，不设置性能接受阈值。历史八段验收保持独立。

## 证据状态

| 观察 | 库 / cohort | 类型 | 状态 | timing credit |
|---|---|---|---|---|
| sqlite-before-rows1 | sqlite / before | phase | observed | True |
| sqlite-before-rows100 | sqlite / before | phase | observed | True |
| sqlite-before-rows1000 | sqlite / before | phase | observed | True |
| sqlite-candidate-rows1 | sqlite / candidate | phase | observed | True |
| sqlite-candidate-rows100 | sqlite / candidate | phase | observed | True |
| sqlite-candidate-rows1000 | sqlite / candidate | phase | observed | True |
| sqlite-dapper-rows1 | sqlite / dapper | phase | observed | True |
| sqlite-dapper-rows100 | sqlite / dapper | phase | observed | True |
| sqlite-dapper-rows1000 | sqlite / dapper | phase | observed | True |
| postgresql-before-rows1 | postgresql / before | phase | observed | True |
| postgresql-before-rows100 | postgresql / before | phase | observed | True |
| postgresql-before-rows1000 | postgresql / before | phase | observed | True |
| postgresql-candidate-rows1 | postgresql / candidate | phase | observed | True |
| postgresql-candidate-rows100 | postgresql / candidate | phase | observed | True |
| postgresql-candidate-rows1000 | postgresql / candidate | phase | observed | True |
| postgresql-dapper-rows1 | postgresql / dapper | phase | observed | True |
| postgresql-dapper-rows100 | postgresql / dapper | phase | observed | True |
| postgresql-dapper-rows1000 | postgresql / dapper | phase | observed | True |

Phase 未具备有效 timing 的格子：无

## 查询阶段

分位为原始样本的 nearest-rank，单位 μs；first execution 单独保存在 JSON。Dapper 可在 ReadComplete 内完成上游迭代器清理，Release 不能脱离 read+release 与总时间单独比较。

| 观察 / route | 行数 | 次数 | 构造 p50/p95/p99 | 首行 p50/p95/p99 | 余行 p50/p95/p99 | 释放 p50/p95/p99 | 总 B/op | GC0/1/2 | CPU μs/op | 峰值 RSS B |
|---|---:|---:|---|---|---|---|---:|---|---:|---:|
| sqlite-before-rows1 / fluent | 1 | 768 | 65.307 / 138.635 / 268.939 | 78.817 / 138.235 / 197.153 | 82.747 / 132.326 / 179.927 | 1.192 / 2.203 / 3.004 | 19,556.719 | 6/1/0 | 398.458 | 20623360 |
| sqlite-before-rows1 / prepared | 1 | 768 | 0.911 / 2.063 / 3.285 | 61.236 / 109.743 / 165.010 | 61.692 / 113.444 / 192.085 | 0.290 / 0.561 / 0.781 | 2,583.865 | 1/0/0 | 289.059 | 20680704 |
| sqlite-before-rows1 / host-sql | 1 | 768 | 22.474 / 35.413 / 94.200 | 67.911 / 132.331 / 261.428 | 69.783 / 112.287 / 177.608 | 0.320 / 0.621 / 0.922 | 8,137.958 | 3/0/0 | 321.345 | 20447232 |
| sqlite-before-rows100 / fluent | 100 | 768 | 67.260 / 100.680 / 297.572 | 107.139 / 175.110 / 210.192 | 224.929 / 366.418 / 473.693 | 1.092 / 1.752 / 11.207 | 26,647.479 | 10/1/0 | 713.165 | 20664320 |
| sqlite-before-rows100 / prepared | 100 | 768 | 0.991 / 2.504 / 3.294 | 87.876 / 155.726 / 188.349 | 177.534 / 302.689 / 406.553 | 0.230 / 0.531 / 0.641 | 9,710.542 | 4/0/0 | 486.413 | 20668416 |
| sqlite-before-rows100 / host-sql | 100 | 768 | 21.642 / 35.863 / 55.162 | 102.843 / 168.731 / 222.480 | 187.078 / 327.025 / 510.588 | 0.260 / 0.591 / 0.782 | 15,257.906 | 4/0/0 | 545.296 | 20627456 |
| sqlite-before-rows1000 / fluent | 1000 | 768 | 77.345 / 156.362 / 604.137 | 107.850 / 186.248 / 280.372 | 1,656.329 / 2,245.393 / 3,138.547 | 1.432 / 2.764 / 3.956 | 97,487.750 | 35/0/0 | 3,930.914 | 21815296 |
| sqlite-before-rows1000 / prepared | 1000 | 768 | 2.854 / 4.857 / 36.384 | 102.191 / 184.264 / 404.986 | 1,600.154 / 2,291.797 / 4,188.782 | 0.451 / 0.801 / 1.062 | 80,581.250 | 30/0/0 | 3,774.289 | 21815296 |
| sqlite-before-rows1000 / host-sql | 1000 | 768 | 34.882 / 55.393 / 109.823 | 117.494 / 185.350 / 299.731 | 1,805.847 / 2,323.716 / 3,225.758 | 0.481 / 0.822 / 1.132 | 86,339.750 | 33/0/0 | 4,077.822 | 21815296 |
| sqlite-candidate-rows1 / fluent | 1 | 768 | 65.147 / 119.698 / 458.431 | 75.381 / 142.492 / 234.358 | 63.719 / 132.116 / 201.078 | 1.061 / 2.394 / 3.745 | 19,570.156 | 5/1/0 | 365.199 | 20815872 |
| sqlite-candidate-rows1 / prepared | 1 | 768 | 0.811 / 2.103 / 3.766 | 62.773 / 114.881 / 188.095 | 54.786 / 113.398 / 208.950 | 0.220 / 0.581 / 1.021 | 2,592.156 | 2/0/0 | 263.665 | 20873216 |
| sqlite-candidate-rows1 / host-sql | 1 | 768 | 23.715 / 39.368 / 81.240 | 77.526 / 148.020 / 313.545 | 58.116 / 120.157 / 231.343 | 0.281 / 0.671 / 1.162 | 8,128.938 | 3/0/0 | 320.672 | 20291584 |
| sqlite-candidate-rows100 / fluent | 100 | 768 | 75.091 / 113.909 / 239.325 | 123.483 / 194.418 / 290.436 | 261.213 / 389.428 / 1,037.149 | 1.212 / 2.644 / 6.209 | 26,619.052 | 8/0/0 | 754.440 | 20660224 |
| sqlite-candidate-rows100 / prepared | 100 | 768 | 1.402 / 3.675 / 89.403 | 112.577 / 192.080 / 304.046 | 260.652 / 419.733 / 779.401 | 0.400 / 0.791 / 1.112 | 9,749.302 | 4/0/0 | 735.957 | 20660224 |
| sqlite-candidate-rows100 / host-sql | 100 | 768 | 24.536 / 52.639 / 142.402 | 122.012 / 199.836 / 383.710 | 248.288 / 401.466 / 820.413 | 0.331 / 0.831 / 1.332 | 15,297.156 | 6/1/0 | 650.974 | 20660224 |
| sqlite-candidate-rows1000 / fluent | 1000 | 768 | 81.101 / 165.456 / 599.361 | 111.355 / 185.035 / 459.242 | 1,672.058 / 2,373.857 / 4,212.952 | 1.442 / 2.514 / 11.017 | 97,504.469 | 36/0/0 | 3,809.371 | 22077440 |
| sqlite-candidate-rows1000 / prepared | 1000 | 768 | 3.245 / 6.710 / 74.081 | 113.189 / 194.190 / 464.283 | 1,811.086 / 2,622.030 / 4,924.882 | 0.501 / 1.052 / 1.522 | 80,613.750 | 31/0/0 | 3,982.262 | 22077440 |
| sqlite-candidate-rows1000 / host-sql | 1000 | 768 | 36.525 / 65.728 / 126.209 | 119.368 / 176.913 / 238.549 | 1,767.641 / 2,357.743 / 2,991.969 | 0.531 / 1.031 / 1.352 | 86,326.438 | 31/0/0 | 3,894.773 | 22077440 |
| sqlite-dapper-rows1 / dapper-aot | 1 | 768 | 0.090 / 0.180 / 3.515 | 5.708 / 9.935 / 26.570 | 0.952 / 1.152 / 1.352 | 0.030 / 0.040 / 0.040 | 2,131.365 | 1/0/0 | 9.526 | 16547840 |
| sqlite-dapper-rows100 / dapper-aot | 100 | 768 | 0.080 / 2.453 / 5.588 | 10.826 / 25.739 / 89.693 | 35.513 / 86.108 / 130.003 | 0.031 / 0.050 / 0.060 | 9,251.365 | 3/0/0 | 58.690 | 18006016 |
| sqlite-dapper-rows1000 / dapper-aot | 1000 | 768 | 0.591 / 1.151 / 24.777 | 13.860 / 35.893 / 105.597 | 358.202 / 551.820 / 1,133.284 | 0.040 / 0.110 / 0.231 | 79,810.188 | 29/1/0 | 413.585 | 18587648 |
| postgresql-before-rows1 / fluent | 1 | 768 | 61.612 / 143.589 / 185.944 | 209.651 / 302.763 / 467.114 | 56.589 / 106.588 / 147.499 | 1.082 / 1.622 / 2.004 | 19,549.333 | 5/1/0 | 391.435 | 19472384 |
| postgresql-before-rows1 / prepared | 1 | 768 | 1.022 / 2.454 / 3.755 | 159.117 / 265.255 / 404.608 | 54.163 / 97.244 / 130.629 | 0.270 / 0.511 / 0.691 | 2,573.573 | 2/0/0 | 297.046 | 19476480 |
| postgresql-before-rows1 / host-sql | 1 | 768 | 23.035 / 39.128 / 82.616 | 185.696 / 304.062 / 428.345 | 56.877 / 113.078 / 178.814 | 0.311 / 0.591 / 0.741 | 8,118.396 | 3/0/0 | 332.518 | 19197952 |
| postgresql-before-rows100 / fluent | 100 | 768 | 63.194 / 158.546 / 264.433 | 305.274 / 417.562 / 503.479 | 231.228 / 342.831 / 514.465 | 1.051 / 1.692 / 9.324 | 26,641.219 | 9/1/0 | 719.413 | 19566592 |
| postgresql-before-rows100 / prepared | 100 | 768 | 1.482 / 3.145 / 3.696 | 290.663 / 382.700 / 512.253 | 250.618 / 376.751 / 560.274 | 0.401 / 0.631 / 0.901 | 9,750.833 | 4/0/0 | 724.439 | 19570688 |
| postgresql-before-rows100 / host-sql | 100 | 768 | 24.406 / 39.238 / 60.650 | 282.430 / 430.580 / 690.007 | 209.256 / 344.333 / 551.731 | 0.340 / 0.601 / 0.801 | 15,270.229 | 4/0/0 | 629.276 | 19562496 |
| postgresql-before-rows1000 / fluent | 1000 | 768 | 78.227 / 119.969 / 322.431 | 345.265 / 474.413 / 716.426 | 2,104.919 / 2,833.477 / 3,364.412 | 1.392 / 2.094 / 2.764 | 97,426.979 | 37/0/0 | 4,178.596 | 20856832 |
| postgresql-before-rows1000 / prepared | 1000 | 768 | 2.965 / 4.707 / 44.387 | 335.560 / 454.348 / 625.893 | 2,144.378 / 2,863.043 / 3,678.676 | 0.441 / 0.721 / 0.972 | 80,530.010 | 29/0/0 | 4,358.165 | 20856832 |
| postgresql-before-rows1000 / host-sql | 1000 | 768 | 32.658 / 56.594 / 183.624 | 343.262 / 489.240 / 1,029.735 | 2,081.790 / 2,844.342 / 4,166.173 | 0.411 / 0.691 / 0.962 | 86,271.729 | 33/0/0 | 3,978.553 | 20856832 |
| postgresql-candidate-rows1 / fluent | 1 | 768 | 66.869 / 129.022 / 307.578 | 242.661 / 317.552 / 513.940 | 63.425 / 103.749 / 139.177 | 1.131 / 1.752 / 2.114 | 19,546.198 | 5/1/0 | 398.909 | 19505152 |
| postgresql-candidate-rows1 / prepared | 1 | 768 | 1.011 / 2.103 / 3.285 | 158.506 / 238.114 / 336.130 | 64.496 / 101.581 / 161.120 | 0.291 / 0.571 / 0.721 | 2,574.365 | 2/0/0 | 292.281 | 19505152 |
| postgresql-candidate-rows1 / host-sql | 1 | 768 | 24.236 / 35.192 / 52.958 | 195.051 / 276.651 / 361.919 | 63.825 / 102.322 / 120.159 | 0.330 / 0.681 / 0.831 | 8,119.479 | 3/0/0 | 323.939 | 19378176 |
| postgresql-candidate-rows100 / fluent | 100 | 768 | 69.814 / 142.552 / 197.444 | 279.957 / 382.770 / 562.628 | 235.600 / 331.228 / 621.354 | 1.112 / 1.673 / 1.943 | 26,665.521 | 10/1/0 | 770.276 | 19546112 |
| postgresql-candidate-rows100 / prepared | 100 | 768 | 1.262 / 2.904 / 3.636 | 286.726 / 385.483 / 505.512 | 243.016 / 356.340 / 654.324 | 0.401 / 0.731 / 0.901 | 9,749.729 | 4/0/0 | 682.741 | 19546112 |
| postgresql-candidate-rows100 / host-sql | 100 | 768 | 28.052 / 49.784 / 89.764 | 291.914 / 439.404 / 833.721 | 240.433 / 375.529 / 674.394 | 0.451 / 0.741 / 0.902 | 15,288.125 | 4/0/0 | 751.861 | 19476480 |
| postgresql-candidate-rows1000 / fluent | 1000 | 768 | 79.128 / 136.524 / 612.374 | 335.740 / 448.808 / 1,181.569 | 2,078.970 / 2,880.829 / 4,382.615 | 1.402 / 2.845 / 4.376 | 97,470.917 | 34/1/0 | 4,370.854 | 20869120 |
| postgresql-candidate-rows1000 / prepared | 1000 | 768 | 3.074 / 4.677 / 43.565 | 327.507 / 455.010 / 620.834 | 1,992.047 / 2,704.136 / 3,578.898 | 0.451 / 0.861 / 1.142 | 80,576.740 | 30/0/0 | 4,129.116 | 20869120 |
| postgresql-candidate-rows1000 / host-sql | 1000 | 768 | 34.191 / 67.070 / 218.536 | 346.176 / 486.046 / 970.410 | 2,100.375 / 2,869.833 / 3,772.511 | 0.501 / 1.082 / 1.683 | 86,278.104 | 30/3/1 | 4,142.042 | 20856832 |
| postgresql-dapper-rows1 / dapper-aot | 1 | 768 | 0.101 / 0.430 / 25.638 | 77.726 / 116.233 / 173.659 | 0.501 / 1.052 / 2.294 | 0.030 / 0.040 / 0.061 | 2,108.125 | 1/0/0 | 93.730 | 24629248 |
| postgresql-dapper-rows100 / dapper-aot | 100 | 768 | 0.140 / 2.794 / 15.753 | 113.199 / 157.835 / 227.859 | 15.072 / 38.066 / 53.230 | 0.030 / 0.050 / 0.120 | 9,240.875 | 2/1/0 | 107.172 | 29167616 |
| postgresql-dapper-rows1000 / dapper-aot | 1000 | 768 | 0.631 / 3.365 / 18.828 | 166.789 / 287.809 / 606.293 | 194.970 / 449.920 / 693.773 | 0.070 / 0.130 / 0.160 | 79,982.406 | 28/1/0 | 467.083 | 28774400 |

## 混合负载

吞吐覆盖已接受请求至 drain；offered 分位与 service 分位使用不同边界。失败和拒绝原样保留；start delay 包含生产者调度与排队，不能称为纯队列驻留时间。

| 观察 | 成功 / 失败 / 拒绝 | offered 目标 rate | 实际 attempted rate | 成功 op/s | 总 B/成功 | GC0/1/2 | CPU s | 峰值 RSS B | idle RSS B |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|

| 观察 | population / boundary | 样本数 | p50 μs upper | p95 μs upper | p99 μs upper |
|---|---|---:|---:|---:|---:|

## SQL 与业务结果等同性

- Phase sqlite-before-rows1 ↔ sqlite-candidate-rows1：可比较记录契约=True；检查={"sameRecordedHost": true, "sameRawTemplate": true, "kordaRenderedSqlByteEqual": true, "sameRows": true, "databaseVersionEqual": true, "bothTimingEligible": true}。
- Phase sqlite-before-rows1 ↔ sqlite-dapper-rows1：可比较记录契约=True；检查={"sameRecordedHost": true, "sameRawTemplate": true, "kordaRenderedSqlByteEqual": null, "sameRows": true, "databaseVersionEqual": true, "bothTimingEligible": true}。
- Phase sqlite-before-rows100 ↔ sqlite-candidate-rows100：可比较记录契约=True；检查={"sameRecordedHost": true, "sameRawTemplate": true, "kordaRenderedSqlByteEqual": true, "sameRows": true, "databaseVersionEqual": true, "bothTimingEligible": true}。
- Phase sqlite-before-rows100 ↔ sqlite-dapper-rows100：可比较记录契约=True；检查={"sameRecordedHost": true, "sameRawTemplate": true, "kordaRenderedSqlByteEqual": null, "sameRows": true, "databaseVersionEqual": true, "bothTimingEligible": true}。
- Phase sqlite-before-rows1000 ↔ sqlite-candidate-rows1000：可比较记录契约=True；检查={"sameRecordedHost": true, "sameRawTemplate": true, "kordaRenderedSqlByteEqual": true, "sameRows": true, "databaseVersionEqual": true, "bothTimingEligible": true}。
- Phase sqlite-before-rows1000 ↔ sqlite-dapper-rows1000：可比较记录契约=True；检查={"sameRecordedHost": true, "sameRawTemplate": true, "kordaRenderedSqlByteEqual": null, "sameRows": true, "databaseVersionEqual": true, "bothTimingEligible": true}。
- Phase sqlite-candidate-rows1 ↔ sqlite-dapper-rows1：可比较记录契约=True；检查={"sameRecordedHost": true, "sameRawTemplate": true, "kordaRenderedSqlByteEqual": null, "sameRows": true, "databaseVersionEqual": true, "bothTimingEligible": true}。
- Phase sqlite-candidate-rows100 ↔ sqlite-dapper-rows100：可比较记录契约=True；检查={"sameRecordedHost": true, "sameRawTemplate": true, "kordaRenderedSqlByteEqual": null, "sameRows": true, "databaseVersionEqual": true, "bothTimingEligible": true}。
- Phase sqlite-candidate-rows1000 ↔ sqlite-dapper-rows1000：可比较记录契约=True；检查={"sameRecordedHost": true, "sameRawTemplate": true, "kordaRenderedSqlByteEqual": null, "sameRows": true, "databaseVersionEqual": true, "bothTimingEligible": true}。
- Phase postgresql-before-rows1 ↔ postgresql-candidate-rows1：可比较记录契约=True；检查={"sameRecordedHost": true, "sameRawTemplate": true, "kordaRenderedSqlByteEqual": true, "sameRows": true, "databaseVersionEqual": true, "bothTimingEligible": true}。
- Phase postgresql-before-rows1 ↔ postgresql-dapper-rows1：可比较记录契约=True；检查={"sameRecordedHost": true, "sameRawTemplate": true, "kordaRenderedSqlByteEqual": null, "sameRows": true, "databaseVersionEqual": true, "bothTimingEligible": true}。
- Phase postgresql-before-rows100 ↔ postgresql-candidate-rows100：可比较记录契约=True；检查={"sameRecordedHost": true, "sameRawTemplate": true, "kordaRenderedSqlByteEqual": true, "sameRows": true, "databaseVersionEqual": true, "bothTimingEligible": true}。
- Phase postgresql-before-rows100 ↔ postgresql-dapper-rows100：可比较记录契约=True；检查={"sameRecordedHost": true, "sameRawTemplate": true, "kordaRenderedSqlByteEqual": null, "sameRows": true, "databaseVersionEqual": true, "bothTimingEligible": true}。
- Phase postgresql-before-rows1000 ↔ postgresql-candidate-rows1000：可比较记录契约=True；检查={"sameRecordedHost": true, "sameRawTemplate": true, "kordaRenderedSqlByteEqual": true, "sameRows": true, "databaseVersionEqual": true, "bothTimingEligible": true}。
- Phase postgresql-before-rows1000 ↔ postgresql-dapper-rows1000：可比较记录契约=True；检查={"sameRecordedHost": true, "sameRawTemplate": true, "kordaRenderedSqlByteEqual": null, "sameRows": true, "databaseVersionEqual": true, "bothTimingEligible": true}。
- Phase postgresql-candidate-rows1 ↔ postgresql-dapper-rows1：可比较记录契约=True；检查={"sameRecordedHost": true, "sameRawTemplate": true, "kordaRenderedSqlByteEqual": null, "sameRows": true, "databaseVersionEqual": true, "bothTimingEligible": true}。
- Phase postgresql-candidate-rows100 ↔ postgresql-dapper-rows100：可比较记录契约=True；检查={"sameRecordedHost": true, "sameRawTemplate": true, "kordaRenderedSqlByteEqual": null, "sameRows": true, "databaseVersionEqual": true, "bothTimingEligible": true}。
- Phase postgresql-candidate-rows1000 ↔ postgresql-dapper-rows1000：可比较记录契约=True；检查={"sameRecordedHost": true, "sameRawTemplate": true, "kordaRenderedSqlByteEqual": null, "sameRows": true, "databaseVersionEqual": true, "bothTimingEligible": true}。

混合负载 SQL 的历史文本差异不会因业务结果 digest 相同而被抹去。FFI 次数和必须等待的协议回复未在这些 receipts 中序列化；SQL 执行与 protocol submission 的实测计数在 JSON 单独保留，不推算 RTT。

## 当前四段 1800 秒记录

四个原始证据完整：False；同机且含已记录 idle 无重叠：False。

- sqlite / candidate：missing；观察=[]。
- sqlite / dapper：missing；观察=[]。
- postgresql / candidate：missing；观察=[]。
- postgresql / dapper：missing；观察=[]。

## 缺项、失败与限制


总 B/op 包括业务对象、字符串/JSON、harness、框架与驱动；GC 按进程计数。该报告不扣除业务结果或 empty-driver，不据此声明框架 0 B。峰值 RSS 是进程生命周期 high-water，idle RSS 是实际 post-drain 观测。
