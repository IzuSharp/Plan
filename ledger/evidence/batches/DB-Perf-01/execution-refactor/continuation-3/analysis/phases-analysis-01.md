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
| sqlite-before-rows1 / fluent | 1 | 768 | 118.396 / 516.969 / 4,960.898 | 217.383 / 11,576.286 / 16,866.820 | 186.818 / 12,220.838 / 20,035.245 | 1.663 / 3.636 / 25.268 | 22,447.917 | 8/1/0 | 1,307.858 | 21348352 |
| sqlite-before-rows1 / prepared | 1 | 768 | 5.018 / 11.988 / 200.378 | 232.797 / 11,981.146 / 19,427.344 | 188.496 / 11,934.436 / 19,906.091 | 0.491 / 1.302 / 1.962 | 6,040.781 | 2/0/0 | 948.400 | 21348352 |
| sqlite-before-rows1 / host-sql | 1 | 768 | 38.808 / 97.916 / 207.078 | 208.450 / 11,818.084 / 12,396.103 | 172.817 / 12,032.693 / 19,561.940 | 0.470 / 1.382 / 2.133 | 10,902.740 | 4/0/0 | 793.112 | 21331968 |
| sqlite-before-rows100 / fluent | 100 | 768 | 110.445 / 302.935 / 645.839 | 256.344 / 10,837.476 / 12,859.388 | 427.420 / 20,214.649 / 31,018.279 | 1.562 / 3.766 / 6.149 | 31,030.469 | 12/1/0 | 1,359.491 | 20897792 |
| sqlite-before-rows100 / prepared | 100 | 768 | 5.648 / 12.499 / 46.320 | 270.957 / 11,976.638 / 18,455.076 | 589.157 / 20,364.428 / 32,341.640 | 0.491 / 1.302 / 1.863 | 14,702.604 | 5/0/0 | 1,287.839 | 20897792 |
| sqlite-before-rows100 / host-sql | 100 | 768 | 36.715 / 90.595 / 156.586 | 248.765 / 11,768.483 / 18,599.967 | 423.555 / 20,157.080 / 32,058.478 | 0.400 / 1.142 / 1.983 | 19,589.198 | 7/0/0 | 1,172.038 | 20889600 |
| sqlite-before-rows1000 / fluent | 1000 | 768 | 189.383 / 565.657 / 1,622.080 | 308.913 / 11,833.483 / 19,167.324 | 47,192.494 / 109,368.103 / 148,679.184 | 3.115 / 5.508 / 117.313 | 116,151.115 | 43/3/1 | 6,659.730 | 20025344 |
| sqlite-before-rows1000 / prepared | 1000 | 768 | 13.110 / 160.792 / 456.858 | 318.805 / 11,961.718 / 17,900.868 | 40,135.263 / 109,522.343 / 138,950.252 | 0.881 / 1.693 / 3.145 | 99,809.073 | 37/3/0 | 6,457.695 | 20004864 |
| sqlite-before-rows1000 / host-sql | 1000 | 768 | 88.601 / 264.892 / 1,321.696 | 297.791 / 10,079.436 / 18,222.879 | 40,703.840 / 111,736.690 / 159,276.073 | 0.832 / 1.622 / 11.467 | 104,912.375 | 39/4/0 | 6,490.027 | 19890176 |
| sqlite-candidate-rows1 / fluent | 1 | 768 | 74.641 / 243.732 / 515.447 | 84.516 / 205.116 / 538.731 | 67.240 / 7,739.987 / 11,840.269 | 1.121 / 2.404 / 4.867 | 20,218.219 | 6/1/0 | 486.465 | 20488192 |
| sqlite-candidate-rows1 / prepared | 1 | 768 | 0.962 / 2.564 / 108.461 | 72.739 / 208.370 / 339.084 | 48.993 / 7,583.746 / 11,693.387 | 0.260 / 0.882 / 1.322 | 3,200.719 | 2/0/0 | 290.962 | 20488192 |
| sqlite-candidate-rows1 / host-sql | 1 | 768 | 24.757 / 54.010 / 156.473 | 80.700 / 199.422 / 389.830 | 52.228 / 8,014.656 / 11,999.797 | 0.281 / 1.001 / 1.422 | 8,765.521 | 3/0/0 | 333.544 | 20127744 |
| sqlite-candidate-rows100 / fluent | 100 | 768 | 78.136 / 174.380 / 452.483 | 129.057 / 252.105 / 448.167 | 259.927 / 7,939.875 / 11,575.669 | 1.222 / 2.764 / 3.986 | 27,226.333 | 9/1/0 | 867.641 | 20979712 |
| sqlite-candidate-rows100 / prepared | 100 | 768 | 1.171 / 3.625 / 152.406 | 113.789 / 239.076 / 581.385 | 251.194 / 3,471.109 / 10,850.941 | 0.300 / 0.791 / 1.272 | 10,237.583 | 3/0/0 | 720.331 | 20979712 |
| sqlite-candidate-rows100 / host-sql | 100 | 768 | 27.812 / 52.659 / 158.876 | 113.850 / 213.648 / 537.559 | 205.596 / 6,256.944 / 10,895.322 | 0.310 / 0.841 / 1.743 | 15,849.708 | 6/0/0 | 703.708 | 20979712 |
| sqlite-candidate-rows1000 / fluent | 1000 | 768 | 86.729 / 216.172 / 1,021.033 | 126.244 / 214.840 / 429.571 | 1,892.187 / 7,908.059 / 12,656.973 | 1.603 / 3.245 / 4.927 | 98,087.906 | 35/0/0 | 4,477.103 | 21684224 |
| sqlite-candidate-rows1000 / prepared | 1000 | 768 | 3.104 / 7.040 / 208.817 | 117.759 / 203.002 / 580.931 | 1,878.052 / 9,137.998 / 12,885.247 | 0.461 / 1.062 / 1.392 | 81,194.490 | 30/0/0 | 4,246.111 | 21688320 |
| sqlite-candidate-rows1000 / host-sql | 1000 | 768 | 35.454 / 92.220 / 316.499 | 117.561 / 208.160 / 317.106 | 1,775.731 / 8,302.937 / 12,768.585 | 0.491 / 1.182 / 1.723 | 86,886.896 | 32/0/0 | 4,309.323 | 21602304 |
| sqlite-dapper-rows1 / dapper-aot | 1 | 768 | 0.060 / 1.472 / 28.512 | 5.679 / 56.775 / 156.252 | 1.011 / 1.402 / 2.634 | 0.040 / 0.041 / 0.050 | 2,131.365 | 1/0/0 | 16.401 | 16658432 |
| sqlite-dapper-rows100 / dapper-aot | 100 | 768 | 0.100 / 2.384 / 16.464 | 10.986 / 29.955 / 125.779 | 36.174 / 124.927 / 223.465 | 0.040 / 0.060 / 0.090 | 9,251.365 | 3/0/0 | 67.701 | 18030592 |
| sqlite-dapper-rows1000 / dapper-aot | 1000 | 768 | 0.821 / 1.602 / 9.694 | 17.175 / 40.791 / 198.756 | 374.539 / 657.521 / 1,151.227 | 0.050 / 0.180 / 0.371 | 79,810.188 | 29/1/0 | 458.659 | 18657280 |
| postgresql-before-rows1 / fluent | 1 | 768 | 95.592 / 324.403 / 963.957 | 509.705 / 12,055.897 / 20,194.283 | 144.155 / 10,489.797 / 16,057.731 | 1.272 / 4.026 / 17.817 | 22,450.208 | 8/1/0 | 931.052 | 19853312 |
| postgresql-before-rows1 / prepared | 1 | 768 | 2.764 / 6.990 / 14.782 | 305.526 / 883.036 / 12,098.070 | 95.943 / 8,979.335 / 18,455.811 | 0.230 / 0.781 / 1.142 | 5,997.438 | 3/0/0 | 474.908 | 19853312 |
| postgresql-before-rows1 / host-sql | 1 | 768 | 25.117 / 76.314 / 300.648 | 368.780 / 10,258.863 / 12,449.408 | 99.108 / 10,895.436 / 12,775.103 | 0.271 / 0.931 / 1.302 | 10,861.615 | 3/0/0 | 601.956 | 19460096 |
| postgresql-before-rows100 / fluent | 100 | 768 | 110.513 / 260.224 / 936.053 | 566.056 / 12,285.961 / 15,951.337 | 464.466 / 20,217.458 / 30,119.495 | 1.533 / 3.886 / 12.358 | 31,026.531 | 10/0/0 | 1,340.557 | 19001344 |
| postgresql-before-rows100 / prepared | 100 | 768 | 5.438 / 15.293 / 139.127 | 597.618 / 12,684.257 / 20,297.167 | 3,629.011 / 20,744.694 / 32,374.746 | 0.431 / 1.111 / 2.875 | 14,700.406 | 6/1/0 | 1,282.624 | 19095552 |
| postgresql-before-rows100 / host-sql | 100 | 768 | 43.944 / 98.897 / 427.596 | 559.407 / 12,410.936 / 19,574.354 | 569.397 / 20,134.951 / 30,051.593 | 0.450 / 1.062 / 1.803 | 19,604.396 | 8/1/0 | 1,321.698 | 18997248 |
| postgresql-before-rows1000 / fluent | 1000 | 768 | 194.690 / 413.465 / 1,870.773 | 855.503 / 12,411.680 / 20,023.141 | 37,035.203 / 87,212.260 / 101,928.920 | 3.435 / 5.137 / 113.389 | 116,148.094 | 42/2/0 | 7,006.156 | 19824640 |
| postgresql-before-rows1000 / prepared | 1000 | 768 | 12.108 / 55.192 / 344.462 | 748.192 / 12,465.678 / 16,644.984 | 19,985.028 / 86,683.961 / 99,119.854 | 0.731 / 1.513 / 2.023 | 99,814.146 | 37/3/1 | 6,078.595 | 19824640 |
| postgresql-before-rows1000 / host-sql | 1000 | 768 | 86.739 / 195.380 / 1,029.161 | 766.891 / 11,282.107 / 19,066.521 | 30,107.270 / 86,831.251 / 108,629.441 | 0.781 / 1.553 / 2.313 | 104,924.771 | 40/3/0 | 6,494.348 | 19820544 |
| postgresql-candidate-rows1 / fluent | 1 | 768 | 66.459 / 173.629 / 469.565 | 201.641 / 410.081 / 1,247.170 | 36.815 / 6,544.903 / 11,419.875 | 0.962 / 2.103 / 3.165 | 19,922.865 | 6/1/0 | 371.098 | 19550208 |
| postgresql-candidate-rows1 / prepared | 1 | 768 | 1.211 / 2.815 / 15.342 | 215.752 / 425.634 / 998.949 | 58.823 / 9,362.856 / 11,521.094 | 0.350 / 0.991 / 1.522 | 3,235.635 | 1/0/0 | 364.909 | 19554304 |
| postgresql-candidate-rows1 / host-sql | 1 | 768 | 25.307 / 52.478 / 90.404 | 205.737 / 424.338 / 994.402 | 40.851 / 9,588.333 / 11,849.674 | 0.310 / 1.091 / 1.703 | 8,543.562 | 3/0/0 | 339.195 | 19333120 |
| postgresql-candidate-rows100 / fluent | 100 | 768 | 72.388 / 141.090 / 345.636 | 334.790 / 561.998 / 1,683.431 | 192.598 / 444.764 / 6,748.962 | 1.182 / 1.933 / 23.805 | 27,108.510 | 8/1/0 | 646.089 | 19562496 |
| postgresql-candidate-rows100 / prepared | 100 | 768 | 1.162 / 2.944 / 8.513 | 314.409 / 488.569 / 1,058.919 | 196.153 / 1,806.885 / 9,988.539 | 0.321 / 0.731 / 1.282 | 10,056.625 | 4/0/0 | 617.051 | 19562496 |
| postgresql-candidate-rows100 / host-sql | 100 | 768 | 26.399 / 47.771 / 95.583 | 321.860 / 614.056 / 1,887.791 | 189.332 / 691.342 / 7,168.127 | 0.321 / 0.631 / 0.951 | 15,705.781 | 6/0/0 | 602.788 | 19562496 |
| postgresql-candidate-rows1000 / fluent | 1000 | 768 | 86.247 / 148.220 / 563.280 | 378.828 / 631.793 / 1,391.497 | 2,336.704 / 7,623.552 / 11,784.358 | 1.563 / 2.654 / 3.496 | 97,934.771 | 36/0/0 | 4,670.143 | 20287488 |
| postgresql-candidate-rows1000 / prepared | 1000 | 768 | 2.964 / 5.989 / 63.544 | 380.375 / 713.375 / 2,408.200 | 2,160.130 / 5,798.758 / 10,508.507 | 0.421 / 0.841 / 1.161 | 81,149.594 | 31/0/0 | 4,178.355 | 20291584 |
| postgresql-candidate-rows1000 / host-sql | 1000 | 768 | 38.256 / 79.237 / 221.957 | 390.105 / 681.925 / 2,476.701 | 2,460.507 / 7,327.252 / 11,949.288 | 0.481 / 1.092 / 1.473 | 86,710.062 | 31/0/0 | 4,717.969 | 19992576 |
| postgresql-dapper-rows1 / dapper-aot | 1 | 768 | 0.131 / 0.511 / 4.627 | 101.792 / 144.966 / 190.364 | 0.591 / 1.282 / 2.153 | 0.030 / 0.050 / 0.061 | 2,108.125 | 1/0/0 | 98.539 | 25059328 |
| postgresql-dapper-rows100 / dapper-aot | 100 | 768 | 0.201 / 4.997 / 40.269 | 163.163 / 211.825 / 283.061 | 21.912 / 56.865 / 143.043 | 0.040 / 0.061 / 0.090 | 9,243.344 | 2/1/0 | 144.964 | 29630464 |
| postgresql-dapper-rows1000 / dapper-aot | 1000 | 768 | 0.911 / 1.803 / 4.967 | 202.909 / 290.598 / 380.235 | 231.461 / 425.768 / 672.822 | 0.090 / 0.130 / 0.210 | 80,005.906 | 28/1/0 | 492.816 | 29474816 |

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
