# Documentation Policy

D01–D21 own 21 detailed specifications; D22–D31 own 10 fragments elaborating existing Delivery tasks; D32 summarizes actual independent review and readiness. These are the existing 32 tasks, without a fourth graph. Research and Documentation proceed in parallel based on local evidence, without a global sequencing lock.

Specifications must clearly describe mature Rust native reuse, necessary C# interfaces, exact ABI/state machines/ownership/lifetimes, errors/cancellation/concurrency/resource release, platform limitations, implementation examples, and verifiable acceptance. Constraints include no Rust compilation for ordinary entities, no C# reimplementation of SQL/network engines, a small Core, and the mandatory Rust Server boundary.

Technical contract acceptance binds a nonempty specification, version, content hash, actual research evidence, and independent review. Complete product implementation and actual release/long-running-load/performance verification are separate Delivery obligations; they must not create a cycle that requires implementation before accepting the design that guides it. Illustrative code must be marked as uncompiled; claims of actual execution may cite only the corresponding source and logs.

A fragment only elaborates concrete steps, scope, interfaces, error behavior, and acceptance for its corresponding existing Delivery tasks; the three graphs remain the sole scheduling authority. During integration, verify that fragment content matches the graph, along with the 114 packet hashes, ownership conflicts, and local dependencies. Any content change invalidates the old review; historical records retain their original bytes and scope of applicability.
