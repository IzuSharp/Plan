# Frame08 普通 Binding 实际结果：有限独立回读

**correctness-binding-01 的实际 Release Native AOT publish与runtime均exit0，结果绑定通过。** 源为e1f18255/tree77c4d8d，前后源稳定。557个总assertions、13个顶层cases；新增frame-rental每profile152个断言已经包含在总数中，不另外相加。最终Native owner/operation/buffer均为0。

独立核对实际log/result/receipt、相关测试和产品源在tracked输入中的身份，以及真正执行ELF与配套.dbg的SHA/BuildID。没有重新扫描整仓源码、构建或重跑测试。实际ELF SHA7e18da4a8e69e169d5570f04966e8f2cda3594bb90aab2c16953fff8d282376b，BuildID ac3ff38168e341faf47522115a1180b53e066a5c。

这份结果来自C++ ABI/decoder fixture的profile1/2，没有实际SQLite/PostgreSQL SQL执行。普通测试覆盖的exact boundaries、dirty rental、同步借用与错误恢复可获正确性信用；真实provider poison-plan验证属于尚独立调度的Relations。metadata/origin/post-rent synthetic故障仍是另一个local构建，不能由本次通过替代。DOTNET_PROCESSOR_COUNT=1只用于这次有限正确性构建/运行，不给普通性能、冷初始化或GC资源测量信用。
