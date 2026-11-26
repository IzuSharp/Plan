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
| sqlite-before-rows1 / fluent | 1 | 768 | 73.010 / 214.953 / 550.897 | 99.339 / 209.144 / 401.372 | 71.968 / 9,755.992 / 11,971.685 | 1.092 / 2.965 / 4.356 | 20,109.115 | 6/1/0 | 495.232 | 20451328 |
| sqlite-before-rows1 / prepared | 1 | 768 | 0.851 / 2.424 / 3.255 | 72.579 / 160.932 / 248.814 | 45.018 / 7,750.136 / 11,899.126 | 0.221 / 0.841 / 1.162 | 3,002.760 | 1/0/0 | 246.764 | 20451328 |
| sqlite-before-rows1 / host-sql | 1 | 768 | 26.350 / 53.931 / 110.365 | 93.190 / 170.816 / 291.658 | 65.389 / 11,675.060 / 12,094.239 | 0.320 / 1.131 / 1.532 | 8,704.010 | 3/0/0 | 350.824 | 20303872 |
| sqlite-before-rows100 / fluent | 100 | 768 | 74.421 / 159.558 / 422.130 | 119.348 / 197.945 / 263.643 | 251.485 / 9,054.492 / 11,739.212 | 1.202 / 2.864 / 3.886 | 27,214.344 | 9/1/0 | 802.824 | 20746240 |
| sqlite-before-rows100 / prepared | 100 | 768 | 1.101 / 2.884 / 6.639 | 101.261 / 182.241 / 326.456 | 201.230 / 6,107.481 / 11,429.435 | 0.271 / 0.881 / 1.272 | 10,245.146 | 4/0/0 | 587.023 | 20746240 |
| sqlite-before-rows100 / host-sql | 100 | 768 | 27.151 / 84.786 / 236.913 | 107.770 / 220.990 / 521.607 | 212.396 / 8,010.555 / 11,862.666 | 0.341 / 0.961 / 1.382 | 15,904.219 | 6/0/0 | 758.548 | 20746240 |
| sqlite-before-rows1000 / fluent | 1000 | 768 | 81.201 / 123.434 / 480.046 | 110.415 / 180.439 / 363.417 | 1,694.059 / 7,481.801 / 12,011.853 | 1.423 / 2.483 / 3.315 | 98,006.833 | 34/1/0 | 3,948.592 | 22040576 |
| sqlite-before-rows1000 / prepared | 1000 | 768 | 2.844 / 5.097 / 9.495 | 109.173 / 178.986 / 219.567 | 1,729.999 / 6,443.609 / 12,963.907 | 0.401 / 0.821 / 1.252 | 81,092.365 | 31/0/0 | 3,904.392 | 22048768 |
| sqlite-before-rows1000 / host-sql | 1000 | 768 | 34.261 / 53.259 / 138.867 | 116.844 / 185.126 / 357.994 | 1,766.548 / 6,437.064 / 10,446.930 | 0.410 / 0.772 / 1.152 | 86,824.250 | 32/0/0 | 3,958.895 | 21909504 |
| sqlite-candidate-rows1 / fluent | 1 | 768 | 61.933 / 97.536 / 193.570 | 58.438 / 131.397 / 175.323 | 46.189 / 107.622 / 160.201 | 0.941 / 1.502 / 1.812 | 19,548.875 | 5/1/0 | 308.074 | 20725760 |
| sqlite-candidate-rows1 / prepared | 1 | 768 | 0.611 / 1.733 / 2.834 | 51.256 / 107.311 / 196.555 | 38.533 / 102.910 / 188.122 | 0.200 / 0.540 / 0.691 | 2,575.969 | 2/0/0 | 223.562 | 20783104 |
| sqlite-candidate-rows1 / host-sql | 1 | 768 | 20.330 / 34.953 / 86.029 | 62.419 / 123.585 / 235.363 | 51.848 / 114.232 / 191.197 | 0.290 / 0.571 / 0.781 | 8,123.188 | 3/0/0 | 287.836 | 20537344 |
| sqlite-candidate-rows100 / fluent | 100 | 768 | 71.267 / 108.321 / 453.786 | 115.432 / 190.904 / 348.540 | 253.893 / 395.058 / 753.192 | 1.152 / 2.463 / 3.064 | 26,642.052 | 8/0/0 | 852.983 | 20623360 |
| sqlite-candidate-rows100 / prepared | 100 | 768 | 1.172 / 3.115 / 35.102 | 109.693 / 180.539 / 325.410 | 239.156 / 392.755 / 540.376 | 0.360 / 0.732 / 1.191 | 9,749.219 | 4/0/0 | 708.508 | 20664320 |
| sqlite-candidate-rows100 / host-sql | 100 | 768 | 29.254 / 49.594 / 94.420 | 119.883 / 184.796 / 251.665 | 242.897 / 360.757 / 495.518 | 0.410 / 0.842 / 1.162 | 15,347.094 | 6/1/0 | 790.379 | 20602880 |
| sqlite-candidate-rows1000 / fluent | 1000 | 768 | 79.859 / 131.976 / 596.237 | 112.197 / 177.153 / 237.008 | 1,743.449 / 2,321.909 / 2,846.325 | 1.382 / 2.463 / 3.315 | 97,492.438 | 35/1/0 | 4,082.167 | 22077440 |
| sqlite-candidate-rows1000 / prepared | 1000 | 768 | 3.064 / 5.037 / 8.472 | 108.036 / 174.450 / 228.470 | 1,756.518 / 2,548.902 / 3,328.087 | 0.470 / 0.832 / 1.302 | 80,587.000 | 30/0/0 | 3,938.168 | 22089728 |
| sqlite-candidate-rows1000 / host-sql | 1000 | 768 | 35.102 / 61.071 / 320.176 | 117.775 / 192.857 / 306.856 | 1,784.175 / 2,269.637 / 3,558.609 | 0.481 / 0.861 / 1.232 | 86,343.260 | 32/0/0 | 4,136.216 | 21782528 |
| sqlite-dapper-rows1 / dapper-aot | 1 | 768 | 0.060 / 0.300 / 3.776 | 5.568 / 11.848 / 60.912 | 0.962 / 1.342 / 2.373 | 0.030 / 0.040 / 0.050 | 2,131.365 | 1/0/0 | 10.997 | 16543744 |
| sqlite-dapper-rows100 / dapper-aot | 100 | 768 | 0.101 / 2.454 / 5.008 | 10.776 / 17.637 / 43.074 | 35.473 / 56.515 / 135.321 | 0.040 / 0.050 / 0.090 | 9,251.365 | 3/0/0 | 55.049 | 18104320 |
| sqlite-dapper-rows1000 / dapper-aot | 1000 | 768 | 0.631 / 1.352 / 2.754 | 13.640 / 32.479 / 81.321 | 351.933 / 544.290 / 928.842 | 0.040 / 0.100 / 0.240 | 79,810.188 | 29/1/0 | 406.177 | 18657280 |
| postgresql-before-rows1 / fluent | 1 | 768 | 67.440 / 155.962 / 275.420 | 206.858 / 394.283 / 553.704 | 33.370 / 7,440.910 / 11,624.516 | 1.021 / 2.544 / 3.976 | 19,870.521 | 6/1/0 | 377.301 | 19517440 |
| postgresql-before-rows1 / prepared | 1 | 768 | 1.212 / 2.734 / 3.745 | 185.076 / 369.310 / 494.115 | 59.393 / 7,825.014 / 11,535.136 | 0.331 / 0.922 / 1.302 | 3,156.719 | 1/0/0 | 332.042 | 19521536 |
| postgresql-before-rows1 / host-sql | 1 | 768 | 26.340 / 51.447 / 97.215 | 202.832 / 374.474 / 504.812 | 55.092 / 7,780.334 / 11,551.273 | 0.341 / 0.982 / 1.442 | 8,627.531 | 3/0/0 | 355.371 | 19144704 |
| postgresql-before-rows100 / fluent | 100 | 768 | 69.073 / 127.380 / 537.320 | 321.459 / 448.768 / 751.870 | 231.755 / 6,294.234 / 11,137.275 | 1.171 / 2.093 / 2.944 | 27,164.646 | 10/0/0 | 753.971 | 19529728 |
| postgresql-before-rows100 / prepared | 100 | 768 | 1.182 / 2.604 / 4.356 | 294.759 / 421.919 / 738.214 | 227.769 / 729.306 / 9,794.029 | 0.280 / 0.701 / 1.162 | 10,236.708 | 3/0/0 | 600.311 | 19529728 |
| postgresql-before-rows100 / host-sql | 100 | 768 | 25.217 / 45.758 / 193.067 | 286.005 / 454.687 / 886.060 | 175.211 / 2,197.142 / 9,789.017 | 0.290 / 0.711 / 1.161 | 15,600.344 | 6/1/0 | 581.643 | 19517440 |
| postgresql-before-rows1000 / fluent | 1000 | 768 | 84.576 / 196.503 / 725.580 | 366.095 / 585.250 / 1,466.062 | 2,261.167 / 7,117.691 / 11,820.675 | 1.532 / 2.904 / 22.264 | 97,953.844 | 36/0/0 | 4,401.221 | 20283392 |
| postgresql-before-rows1000 / prepared | 1000 | 768 | 3.014 / 5.237 / 24.726 | 356.853 / 518.732 / 746.606 | 2,297.551 / 4,992.699 / 11,885.928 | 0.421 / 0.991 / 1.493 | 81,086.729 | 30/0/0 | 4,077.911 | 20287488 |
| postgresql-before-rows1000 / host-sql | 1000 | 768 | 33.941 / 68.482 / 424.373 | 357.853 / 524.679 / 671.299 | 2,185.847 / 5,896.495 / 11,324.554 | 0.421 / 0.851 / 1.342 | 86,728.458 | 31/0/0 | 4,100.462 | 20144128 |
| postgresql-candidate-rows1 / fluent | 1 | 768 | 69.863 / 219.865 / 569.292 | 229.359 / 459.089 / 3,592.445 | 57.205 / 143.332 / 297.811 | 1.142 / 2.183 / 3.556 | 19,547.281 | 5/1/0 | 526.861 | 19505152 |
| postgresql-candidate-rows1 / prepared | 1 | 768 | 1.092 / 2.043 / 3.345 | 189.846 / 314.846 / 447.652 | 63.193 / 112.476 / 190.021 | 0.311 / 0.580 / 0.711 | 2,569.969 | 2/0/0 | 329.230 | 19513344 |
| postgresql-candidate-rows1 / host-sql | 1 | 768 | 24.286 / 35.562 / 84.675 | 171.063 / 271.382 / 353.684 | 54.721 / 105.932 / 153.597 | 0.331 / 0.641 / 0.791 | 8,115.896 | 3/0/0 | 327.492 | 19501056 |
| postgresql-candidate-rows100 / fluent | 100 | 768 | 66.009 / 101.932 / 351.323 | 297.078 / 416.951 / 555.862 | 226.487 / 324.383 / 497.550 | 1.122 / 1.653 / 2.163 | 26,623.792 | 8/0/0 | 739.305 | 19554304 |
| postgresql-candidate-rows100 / prepared | 100 | 768 | 1.241 / 3.104 / 22.553 | 291.945 / 521.731 / 1,516.118 | 217.772 / 374.037 / 759.306 | 0.371 / 0.651 / 0.892 | 9,748.625 | 4/0/0 | 665.319 | 19554304 |
| postgresql-candidate-rows100 / host-sql | 100 | 768 | 28.092 / 43.124 / 92.368 | 303.271 / 457.141 / 869.391 | 233.766 / 378.293 / 982.473 | 0.400 / 0.681 / 0.921 | 15,309.375 | 6/1/0 | 755.816 | 19550208 |
| postgresql-candidate-rows1000 / fluent | 1000 | 768 | 85.898 / 183.012 / 748.089 | 357.810 / 555.325 / 1,168.252 | 2,298.227 / 2,905.628 / 5,200.079 | 1.582 / 2.804 / 3.996 | 97,430.260 | 32/3/0 | 4,869.999 | 21045248 |
| postgresql-candidate-rows1000 / prepared | 1000 | 768 | 3.435 / 5.648 / 105.677 | 368.046 / 630.883 / 2,440.858 | 2,471.955 / 3,301.118 / 5,195.478 | 0.531 / 0.951 / 1.482 | 80,552.156 | 31/0/0 | 4,907.936 | 21045248 |
| postgresql-candidate-rows1000 / host-sql | 1000 | 768 | 36.314 / 63.665 / 105.606 | 353.013 / 503.002 / 661.761 | 2,314.136 / 2,933.800 / 3,373.892 | 0.551 / 1.062 / 1.422 | 86,283.906 | 31/0/0 | 4,755.458 | 21045248 |
| postgresql-dapper-rows1 / dapper-aot | 1 | 768 | 0.410 / 0.551 / 6.620 | 130.573 / 161.939 / 192.515 | 2.204 / 2.523 / 9.063 | 0.060 / 0.080 / 0.120 | 2,108.125 | 1/0/0 | 119.062 | 25649152 |
| postgresql-dapper-rows100 / dapper-aot | 100 | 768 | 0.130 / 3.165 / 26.530 | 126.499 / 228.661 / 463.010 | 15.152 / 39.258 / 109.202 | 0.030 / 0.060 / 0.130 | 9,240.875 | 2/1/0 | 121.751 | 29802496 |
| postgresql-dapper-rows1000 / dapper-aot | 1000 | 768 | 0.741 / 1.853 / 29.223 | 185.946 / 280.857 / 433.704 | 220.588 / 417.400 / 753.991 | 0.081 / 0.130 / 0.210 | 79,914.479 | 29/1/0 | 475.806 | 29945856 |

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
