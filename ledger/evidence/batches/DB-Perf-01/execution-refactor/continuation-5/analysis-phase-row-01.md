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
| sqlite-before-rows1 / fluent | 1 | 768 | 67.020 / 106.879 / 220.409 | 76.524 / 129.533 / 238.416 | 63.159 / 121.506 / 241.830 | 1.132 / 2.524 / 3.986 | 19,570.875 | 5/1/0 | 378.940 | 20865024 |
| sqlite-before-rows1 / prepared | 1 | 768 | 0.871 / 1.873 / 3.335 | 55.813 / 101.216 / 133.069 | 45.107 / 95.607 / 190.003 | 0.221 / 0.531 / 0.791 | 2,586.802 | 2/0/0 | 251.336 | 20926464 |
| sqlite-before-rows1 / host-sql | 1 | 768 | 23.856 / 38.377 / 85.237 | 74.641 / 142.978 / 330.137 | 56.124 / 120.450 / 297.743 | 0.321 / 0.701 / 0.941 | 8,128.333 | 3/0/0 | 323.625 | 20611072 |
| sqlite-before-rows100 / fluent | 100 | 768 | 65.988 / 107.660 / 166.969 | 101.070 / 162.762 / 208.811 | 213.969 / 328.309 / 486.425 | 1.051 / 2.454 / 3.616 | 26,656.594 | 8/1/0 | 671.237 | 20729856 |
| sqlite-before-rows100 / prepared | 100 | 768 | 1.132 / 2.714 / 4.467 | 89.303 / 130.435 / 169.953 | 190.343 / 283.482 / 438.488 | 0.290 / 0.611 / 1.151 | 9,767.781 | 4/0/0 | 576.712 | 20729856 |
| sqlite-before-rows100 / host-sql | 100 | 768 | 22.344 / 38.737 / 79.488 | 90.795 / 140.069 / 171.045 | 195.071 / 330.031 / 415.879 | 0.310 / 0.631 / 1.132 | 15,325.323 | 6/0/0 | 596.805 | 20729856 |
| sqlite-before-rows1000 / fluent | 1000 | 768 | 82.533 / 173.068 / 536.108 | 119.397 / 190.203 / 299.025 | 1,822.247 / 2,592.950 / 4,000.911 | 1.582 / 3.135 / 12.689 | 97,504.490 | 35/0/0 | 4,126.875 | 22179840 |
| sqlite-before-rows1000 / prepared | 1000 | 768 | 3.445 / 7.461 / 94.370 | 100.830 / 170.734 / 315.790 | 1,620.733 / 2,489.130 / 4,567.710 | 0.481 / 0.971 / 2.354 | 80,607.885 | 29/1/0 | 3,867.603 | 22179840 |
| sqlite-before-rows1000 / host-sql | 1000 | 768 | 35.383 / 59.058 / 124.606 | 112.598 / 178.441 / 251.965 | 1,685.560 / 2,191.193 / 2,749.848 | 0.501 / 0.932 / 1.312 | 86,342.823 | 32/0/0 | 3,871.039 | 22179840 |
| sqlite-candidate-rows1 / fluent | 1 | 768 | 60.480 / 95.692 / 273.207 | 62.423 / 114.656 / 144.956 | 47.090 / 97.425 / 126.494 | 1.031 / 1.682 / 1.963 | 19,577.917 | 6/1/0 | 326.449 | 20848640 |
| sqlite-candidate-rows1 / prepared | 1 | 768 | 0.651 / 1.753 / 2.934 | 48.051 / 94.962 / 156.374 | 39.719 / 94.496 / 136.403 | 0.181 / 0.511 / 0.641 | 2,587.375 | 1/0/0 | 233.362 | 20905984 |
| sqlite-candidate-rows1 / host-sql | 1 | 768 | 17.707 / 31.817 / 54.080 | 59.828 / 106.648 / 155.912 | 43.776 / 90.645 / 118.776 | 0.240 / 0.561 / 0.651 | 8,135.156 | 3/0/0 | 263.668 | 20598784 |
| sqlite-candidate-rows100 / fluent | 100 | 768 | 66.408 / 132.026 / 236.662 | 100.740 / 151.361 / 178.415 | 214.845 / 327.367 / 460.355 | 1.202 / 2.114 / 3.415 | 26,660.917 | 8/0/0 | 727.875 | 20561920 |
| sqlite-candidate-rows100 / prepared | 100 | 768 | 1.142 / 2.654 / 4.136 | 89.483 / 139.307 / 178.496 | 196.512 / 281.844 / 403.180 | 0.330 / 0.631 / 0.871 | 9,785.156 | 4/0/0 | 607.285 | 20598784 |
| sqlite-candidate-rows100 / host-sql | 100 | 768 | 24.777 / 34.481 / 57.415 | 92.091 / 152.307 / 224.234 | 188.115 / 297.653 / 510.665 | 0.340 / 0.611 / 0.832 | 15,342.125 | 6/1/0 | 612.876 | 20557824 |
| sqlite-candidate-rows1000 / fluent | 1000 | 768 | 82.774 / 183.243 / 739.601 | 110.965 / 179.978 / 319.245 | 1,678.578 / 2,344.655 / 3,903.448 | 1.602 / 2.604 / 4.587 | 97,491.104 | 33/4/0 | 3,949.909 | 22122496 |
| sqlite-candidate-rows1000 / prepared | 1000 | 768 | 2.984 / 6.740 / 412.715 | 101.901 / 181.751 / 379.015 | 1,589.671 / 2,443.067 / 3,306.066 | 0.440 / 0.902 / 1.413 | 80,615.031 | 31/0/0 | 3,753.536 | 22122496 |
| sqlite-candidate-rows1000 / host-sql | 1000 | 768 | 35.373 / 60.810 / 113.058 | 110.834 / 168.065 / 281.269 | 1,676.595 / 2,268.851 / 3,179.278 | 0.481 / 0.942 / 1.282 | 86,313.521 | 29/2/1 | 3,890.371 | 22122496 |
| sqlite-dapper-rows1 / dapper-aot | 1 | 768 | 0.060 / 1.573 / 3.606 | 5.788 / 10.586 / 27.431 | 0.992 / 1.202 / 1.552 | 0.030 / 0.040 / 0.041 | 2,131.365 | 1/0/0 | 9.727 | 16592896 |
| sqlite-dapper-rows100 / dapper-aot | 100 | 768 | 0.090 / 2.514 / 4.877 | 10.876 / 18.478 / 58.007 | 35.743 / 52.208 / 101.391 | 0.030 / 0.050 / 0.061 | 9,251.365 | 3/0/0 | 54.262 | 17952768 |
| sqlite-dapper-rows1000 / dapper-aot | 1000 | 768 | 0.561 / 1.232 / 42.503 | 13.009 / 32.098 / 115.361 | 349.900 / 537.500 / 844.387 | 0.040 / 0.110 / 0.230 | 79,810.188 | 29/1/0 | 399.620 | 18501632 |
| postgresql-before-rows1 / fluent | 1 | 768 | 67.350 / 128.562 / 201.450 | 202.502 / 284.102 / 507.495 | 53.344 / 96.954 / 128.421 | 1.001 / 1.683 / 2.213 | 19,546.208 | 5/1/0 | 355.428 | 19431424 |
| postgresql-before-rows1 / prepared | 1 | 768 | 0.781 / 1.893 / 2.984 | 137.324 / 212.657 / 357.612 | 39.774 / 86.103 / 107.716 | 0.211 / 0.501 / 0.641 | 2,567.656 | 2/0/0 | 232.671 | 19431424 |
| postgresql-before-rows1 / host-sql | 1 | 768 | 23.926 / 35.764 / 59.469 | 164.144 / 267.268 / 384.853 | 56.714 / 101.921 / 133.458 | 0.330 / 0.620 / 0.751 | 8,116.969 | 3/0/0 | 314.091 | 19431424 |
| postgresql-before-rows100 / fluent | 100 | 768 | 70.695 / 101.861 / 456.921 | 311.402 / 447.947 / 1,077.304 | 249.211 / 362.540 / 694.500 | 1.221 / 1.843 / 2.323 | 26,645.385 | 9/1/0 | 778.921 | 19533824 |
| postgresql-before-rows100 / prepared | 100 | 768 | 1.292 / 2.874 / 3.575 | 313.986 / 435.906 / 1,626.773 | 227.187 / 357.372 / 808.382 | 0.380 / 0.661 / 0.882 | 9,772.427 | 4/0/0 | 690.217 | 19533824 |
| postgresql-before-rows100 / host-sql | 100 | 768 | 26.920 / 37.515 / 75.231 | 311.001 / 422.936 / 745.814 | 221.548 / 320.885 / 463.977 | 0.401 / 0.701 / 0.851 | 15,315.083 | 5/0/0 | 695.628 | 19533824 |
| postgresql-before-rows1000 / fluent | 1000 | 768 | 76.925 / 138.446 / 564.730 | 336.420 / 505.733 / 965.950 | 2,087.893 / 2,924.783 / 3,967.431 | 1.332 / 2.273 / 3.335 | 97,450.948 | 35/0/0 | 4,274.719 | 20873216 |
| postgresql-before-rows1000 / prepared | 1000 | 768 | 2.934 / 4.857 / 27.030 | 332.404 / 455.028 / 772.064 | 2,042.420 / 2,687.201 / 3,049.189 | 0.471 / 0.891 / 1.262 | 80,580.781 | 30/0/0 | 4,179.219 | 20873216 |
| postgresql-before-rows1000 / host-sql | 1000 | 768 | 33.780 / 66.649 / 134.791 | 337.022 / 477.020 / 662.376 | 2,065.275 / 2,659.669 / 3,273.714 | 0.481 / 0.881 / 1.222 | 86,302.312 | 32/0/0 | 4,270.434 | 20873216 |
| postgresql-candidate-rows1 / fluent | 1 | 768 | 66.069 / 110.995 / 200.208 | 229.862 / 343.501 / 447.826 | 68.021 / 124.400 / 180.729 | 1.132 / 1.823 / 7.651 | 19,541.469 | 5/1/0 | 424.577 | 19558400 |
| postgresql-candidate-rows1 / prepared | 1 | 768 | 0.811 / 2.303 / 9.995 | 195.301 / 291.374 / 421.932 | 62.903 / 127.089 / 270.313 | 0.270 / 0.631 / 0.762 | 2,558.073 | 2/0/0 | 289.788 | 19558400 |
| postgresql-candidate-rows1 / host-sql | 1 | 768 | 25.418 / 36.103 / 63.314 | 199.827 / 296.381 / 450.986 | 74.772 / 123.344 / 188.805 | 0.370 / 0.671 / 0.831 | 8,110.458 | 3/0/0 | 387.746 | 19304448 |
| postgresql-candidate-rows100 / fluent | 100 | 768 | 68.973 / 130.875 / 303.962 | 292.015 / 411.973 / 550.689 | 240.067 / 359.670 / 502.528 | 1.122 / 1.773 / 2.504 | 26,634.990 | 8/1/0 | 728.600 | 19591168 |
| postgresql-candidate-rows100 / prepared | 100 | 768 | 1.162 / 2.694 / 3.745 | 292.680 / 406.816 / 621.235 | 228.641 / 373.025 / 767.412 | 0.340 / 0.701 / 0.962 | 9,740.688 | 5/0/0 | 605.897 | 19591168 |
| postgresql-candidate-rows100 / host-sql | 100 | 768 | 26.990 / 39.188 / 65.287 | 288.829 / 405.063 / 917.356 | 240.568 / 356.270 / 503.835 | 0.390 / 0.721 / 0.871 | 15,308.865 | 5/0/0 | 689.389 | 19521536 |
| postgresql-candidate-rows1000 / fluent | 1000 | 768 | 80.009 / 136.684 / 502.795 | 334.726 / 463.137 / 1,050.192 | 2,256.717 / 3,132.365 / 3,854.535 | 1.402 / 2.744 / 4.116 | 97,450.552 | 36/0/0 | 4,340.060 | 20541440 |
| postgresql-candidate-rows1000 / prepared | 1000 | 768 | 2.874 / 4.607 / 22.433 | 329.529 / 463.510 / 616.379 | 2,053.645 / 2,741.660 / 3,173.707 | 0.460 / 0.831 / 1.152 | 80,556.427 | 29/0/0 | 4,058.602 | 20848640 |
| postgresql-candidate-rows1000 / host-sql | 1000 | 768 | 33.029 / 54.531 / 129.172 | 330.662 / 462.248 / 791.724 | 2,143.583 / 2,909.213 / 3,299.074 | 0.471 / 0.862 / 1.272 | 86,266.385 | 31/0/0 | 4,116.447 | 20529152 |
| postgresql-dapper-rows1 / dapper-aot | 1 | 768 | 0.160 / 0.921 / 4.807 | 82.323 / 144.405 / 247.278 | 0.721 / 1.232 / 2.153 | 0.030 / 0.060 / 0.090 | 2,108.125 | 1/0/0 | 101.102 | 24530944 |
| postgresql-dapper-rows100 / dapper-aot | 100 | 768 | 0.231 / 28.062 / 40.681 | 138.475 / 242.159 / 428.525 | 21.401 / 68.841 / 175.029 | 0.050 / 0.081 / 0.110 | 9,243.344 | 2/1/0 | 157.363 | 28590080 |
| postgresql-dapper-rows1000 / dapper-aot | 1000 | 768 | 0.711 / 1.692 / 24.908 | 171.215 / 309.100 / 691.860 | 211.214 / 369.830 / 730.687 | 0.080 / 0.130 / 0.200 | 79,976.802 | 28/1/0 | 456.204 | 28803072 |

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
