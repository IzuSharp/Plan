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
| sqlite-before-rows1 / fluent | 1 | 768 | 71.806 / 103.865 / 185.165 | 81.091 / 131.800 / 189.787 | 64.125 / 115.557 / 163.944 | 1.272 / 2.363 / 3.595 | 19,559.031 | 5/1/0 | 378.987 | 20631552 |
| sqlite-before-rows1 / prepared | 1 | 768 | 1.041 / 2.303 / 3.606 | 66.019 / 103.134 / 130.514 | 56.083 / 110.950 / 161.850 | 0.320 / 0.621 / 0.782 | 2,594.594 | 2/0/0 | 275.297 | 20692992 |
| sqlite-before-rows1 / host-sql | 1 | 768 | 23.915 / 39.349 / 72.167 | 71.066 / 116.814 / 177.364 | 55.393 / 107.540 / 161.034 | 0.350 / 0.671 / 0.862 | 8,130.240 | 3/0/0 | 306.908 | 20488192 |
| sqlite-before-rows100 / fluent | 100 | 768 | 75.553 / 166.528 / 353.335 | 117.495 / 197.319 / 366.134 | 247.618 / 404.050 / 675.178 | 1.302 / 2.043 / 11.968 | 26,649.083 | 8/1/0 | 853.717 | 20459520 |
| sqlite-before-rows100 / prepared | 100 | 768 | 1.292 / 2.924 / 3.555 | 103.845 / 174.920 / 296.141 | 220.002 / 358.993 / 656.086 | 0.321 / 0.651 / 0.891 | 9,747.688 | 4/0/0 | 630.051 | 20496384 |
| sqlite-before-rows100 / host-sql | 100 | 768 | 28.703 / 44.186 / 75.913 | 115.541 / 192.787 / 296.611 | 240.463 / 396.013 / 712.753 | 0.400 / 0.741 / 0.961 | 15,328.990 | 6/0/0 | 727.478 | 20455424 |
| sqlite-before-rows1000 / fluent | 1000 | 768 | 83.895 / 145.936 / 586.551 | 117.885 / 186.147 / 287.467 | 1,703.189 / 2,398.361 / 3,653.700 | 1.562 / 2.814 / 4.136 | 97,506.979 | 35/0/0 | 4,061.934 | 21741568 |
| sqlite-before-rows1000 / prepared | 1000 | 768 | 2.925 / 5.478 / 77.345 | 99.478 / 176.892 / 368.488 | 1,555.785 / 2,150.729 / 3,711.697 | 0.421 / 0.741 / 1.212 | 80,588.688 | 30/0/0 | 3,515.182 | 21741568 |
| sqlite-before-rows1000 / host-sql | 1000 | 768 | 33.289 / 50.045 / 111.346 | 109.142 / 169.681 / 265.554 | 1,622.820 / 2,147.689 / 3,056.694 | 0.470 / 0.841 / 1.022 | 86,360.594 | 33/0/0 | 3,801.908 | 21741568 |
| sqlite-candidate-rows1 / fluent | 1 | 768 | 70.475 / 110.554 / 168.020 | 85.557 / 136.653 / 170.393 | 66.814 / 122.642 / 176.463 | 1.172 / 2.594 / 3.415 | 19,553.167 | 5/1/0 | 392.417 | 20893696 |
| sqlite-candidate-rows1 / prepared | 1 | 768 | 1.172 / 2.704 / 4.246 | 74.395 / 112.988 / 149.007 | 65.237 / 114.525 / 165.451 | 0.330 / 0.711 / 0.971 | 2,582.521 | 2/0/0 | 312.754 | 20951040 |
| sqlite-candidate-rows1 / host-sql | 1 | 768 | 25.167 / 43.034 / 62.463 | 84.365 / 130.975 / 245.435 | 71.817 / 125.461 / 172.386 | 0.360 / 0.772 / 1.092 | 8,136.323 | 3/0/0 | 354.238 | 20660224 |
| sqlite-candidate-rows100 / fluent | 100 | 768 | 75.382 / 137.905 / 257.403 | 113.318 / 184.695 / 252.265 | 233.848 / 376.831 / 622.626 | 1.322 / 1.932 / 2.353 | 26,674.792 | 8/0/0 | 770.526 | 20754432 |
| sqlite-candidate-rows100 / prepared | 100 | 768 | 1.392 / 3.004 / 3.646 | 103.344 / 155.381 / 215.445 | 214.675 / 332.435 / 558.586 | 0.351 / 0.631 / 0.791 | 9,778.354 | 4/0/0 | 666.608 | 20762624 |
| sqlite-candidate-rows100 / host-sql | 100 | 768 | 27.881 / 47.481 / 106.057 | 111.856 / 192.066 / 342.980 | 219.716 / 376.921 / 681.018 | 0.370 / 0.671 / 0.781 | 15,325.167 | 6/1/0 | 681.212 | 20717568 |
| sqlite-candidate-rows1000 / fluent | 1000 | 768 | 80.280 / 130.545 / 574.044 | 107.801 / 170.764 / 310.532 | 1,666.970 / 2,197.436 / 2,651.026 | 1.562 / 2.724 / 3.956 | 97,483.104 | 32/0/0 | 3,866.216 | 22081536 |
| sqlite-candidate-rows1000 / prepared | 1000 | 768 | 2.994 / 5.448 / 25.357 | 104.765 / 163.142 / 228.099 | 1,609.861 / 2,313.645 / 2,968.147 | 0.431 / 0.801 / 1.142 | 80,584.156 | 31/1/1 | 3,499.927 | 22126592 |
| sqlite-candidate-rows1000 / host-sql | 1000 | 768 | 32.929 / 64.225 / 124.776 | 110.074 / 185.606 / 303.060 | 1,576.347 / 2,252.313 / 4,120.919 | 0.441 / 0.811 / 1.392 | 86,305.292 | 31/1/0 | 3,536.783 | 22065152 |
| sqlite-dapper-rows1 / dapper-aot | 1 | 768 | 0.070 / 0.291 / 4.036 | 5.778 / 11.267 / 38.427 | 0.982 / 1.222 / 2.423 | 0.030 / 0.041 / 0.050 | 2,131.365 | 1/0/0 | 10.812 | 16588800 |
| sqlite-dapper-rows100 / dapper-aot | 100 | 768 | 0.090 / 2.343 / 4.486 | 10.736 / 17.976 / 36.444 | 35.513 / 50.405 / 96.504 | 0.040 / 0.050 / 0.070 | 9,251.365 | 3/0/0 | 52.775 | 17891328 |
| sqlite-dapper-rows1000 / dapper-aot | 1000 | 768 | 0.781 / 1.522 / 2.724 | 13.931 / 35.553 / 57.916 | 356.070 / 609.648 / 1,426.324 | 0.041 / 0.141 / 0.251 | 79,810.188 | 29/1/0 | 433.635 | 18620416 |
| postgresql-before-rows1 / fluent | 1 | 768 | 73.339 / 152.967 / 364.402 | 238.905 / 392.534 / 1,147.774 | 58.137 / 128.531 / 211.821 | 1.252 / 1.953 / 3.325 | 19,548.250 | 5/1/0 | 417.169 | 19562496 |
| postgresql-before-rows1 / prepared | 1 | 768 | 1.192 / 2.294 / 3.725 | 189.162 / 313.737 / 467.846 | 53.865 / 121.555 / 296.832 | 0.310 / 0.651 / 0.781 | 2,573.885 | 2/0/0 | 298.943 | 19562496 |
| postgresql-before-rows1 / host-sql | 1 | 768 | 27.741 / 45.678 / 92.938 | 222.121 / 412.284 / 866.651 | 60.791 / 107.210 / 199.337 | 0.381 / 0.701 / 0.831 | 8,119.281 | 3/0/0 | 348.922 | 19316736 |
| postgresql-before-rows100 / fluent | 100 | 768 | 63.325 / 100.330 / 321.859 | 294.141 / 397.767 / 506.790 | 177.514 / 346.640 / 444.622 | 1.072 / 1.752 / 2.234 | 26,630.812 | 8/1/0 | 609.414 | 19791872 |
| postgresql-before-rows100 / prepared | 100 | 768 | 1.182 / 2.784 / 3.826 | 307.120 / 375.509 / 490.857 | 195.962 / 318.789 / 488.908 | 0.300 / 0.671 / 0.831 | 9,764.021 | 5/0/0 | 583.901 | 19791872 |
| postgresql-before-rows100 / host-sql | 100 | 768 | 28.383 / 46.439 / 78.376 | 302.754 / 428.368 / 825.809 | 214.123 / 371.768 / 518.737 | 0.381 / 0.701 / 0.821 | 15,305.198 | 5/0/0 | 677.905 | 19791872 |
| postgresql-before-rows1000 / fluent | 1000 | 768 | 81.411 / 126.718 / 419.525 | 352.975 / 507.786 / 844.096 | 2,143.143 / 2,973.358 / 4,383.591 | 1.502 / 3.015 / 12.979 | 97,444.375 | 36/0/0 | 4,176.283 | 20508672 |
| postgresql-before-rows1000 / prepared | 1000 | 768 | 3.075 / 4.707 / 91.876 | 333.887 / 499.673 / 747.863 | 2,102.432 / 3,009.541 / 4,527.048 | 0.461 / 0.862 / 1.161 | 80,535.292 | 29/0/0 | 4,134.874 | 20508672 |
| postgresql-before-rows1000 / host-sql | 1000 | 768 | 36.504 / 70.014 / 173.187 | 366.335 / 605.280 / 1,418.285 | 2,206.858 / 3,157.578 / 4,654.499 | 0.531 / 1.172 / 1.883 | 86,302.750 | 33/0/0 | 4,345.931 | 20508672 |
| postgresql-candidate-rows1 / fluent | 1 | 768 | 69.944 / 148.250 / 570.239 | 225.015 / 329.621 / 566.643 | 49.979 / 111.026 / 215.881 | 1.221 / 1.793 / 2.233 | 19,547.833 | 5/1/0 | 395.438 | 19697664 |
| postgresql-candidate-rows1 / prepared | 1 | 768 | 1.151 / 2.504 / 3.555 | 174.995 / 289.831 / 612.326 | 54.086 / 102.593 / 172.231 | 0.300 / 0.591 / 0.731 | 2,556.562 | 1/0/0 | 345.156 | 19701760 |
| postgresql-candidate-rows1 / host-sql | 1 | 768 | 25.117 / 48.432 / 107.364 | 188.460 / 303.386 / 428.647 | 44.532 / 96.865 / 169.092 | 0.331 / 0.651 / 0.761 | 8,116.802 | 3/0/0 | 310.098 | 19345408 |
| postgresql-candidate-rows100 / fluent | 100 | 768 | 68.823 / 150.725 / 482.248 | 324.577 / 490.735 / 741.965 | 255.013 / 471.773 / 1,017.114 | 1.202 / 1.843 / 9.414 | 26,642.708 | 8/1/0 | 774.970 | 20127744 |
| postgresql-candidate-rows100 / prepared | 100 | 768 | 1.292 / 2.934 / 3.465 | 295.209 / 416.234 / 560.134 | 222.364 / 353.987 / 698.505 | 0.370 / 0.651 / 0.801 | 9,747.656 | 5/0/0 | 668.254 | 20127744 |
| postgresql-candidate-rows100 / host-sql | 100 | 768 | 26.079 / 44.346 / 66.930 | 316.291 / 446.484 / 669.757 | 229.261 / 345.374 / 500.325 | 0.361 / 0.631 / 0.771 | 15,287.458 | 5/0/0 | 647.514 | 20127744 |
| postgresql-candidate-rows1000 / fluent | 1000 | 768 | 78.577 / 138.807 / 318.944 | 342.310 / 508.197 / 1,103.422 | 2,087.035 / 2,868.328 / 4,693.355 | 1.402 / 2.193 / 4.727 | 97,459.198 | 35/4/1 | 4,349.216 | 21176320 |
| postgresql-candidate-rows1000 / prepared | 1000 | 768 | 3.405 / 5.508 / 74.421 | 333.656 / 469.299 / 1,095.310 | 2,129.184 / 2,846.797 / 4,092.961 | 0.491 / 0.831 / 1.652 | 80,551.448 | 30/1/0 | 4,252.697 | 21176320 |
| postgresql-candidate-rows1000 / host-sql | 1000 | 768 | 33.960 / 60.650 / 307.698 | 342.880 / 515.498 / 1,046.117 | 2,094.417 / 2,775.358 / 4,297.031 | 0.481 / 0.821 / 1.062 | 86,211.781 | 27/3/0 | 4,157.624 | 21176320 |
| postgresql-dapper-rows1 / dapper-aot | 1 | 768 | 0.160 / 0.500 / 7.151 | 95.482 / 168.541 / 328.669 | 0.711 / 2.263 / 2.724 | 0.040 / 0.070 / 0.120 | 2,112.781 | 1/0/0 | 105.837 | 24711168 |
| postgresql-dapper-rows100 / dapper-aot | 100 | 768 | 0.200 / 29.725 / 45.167 | 153.028 / 235.531 / 319.736 | 32.438 / 67.290 / 96.704 | 0.040 / 0.080 / 0.091 | 9,241.844 | 2/1/0 | 154.194 | 29085696 |
| postgresql-dapper-rows1000 / dapper-aot | 1000 | 768 | 0.972 / 1.792 / 5.768 | 219.066 / 276.461 / 440.916 | 249.491 / 355.579 / 688.485 | 0.090 / 0.130 / 0.210 | 80,111.865 | 28/1/0 | 492.936 | 29388800 |

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
