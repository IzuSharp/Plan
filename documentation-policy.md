# Documentation policy

D01–D21 own 21 detailed specifications; D22–D31 own 10 implementation fragments elaborating existing Delivery tasks; D32 consolidates actual independent reviews and readiness. These are the existing 32 tasks, without adding a fourth graph. Research and Documentation proceed in parallel based on local evidence and require no global ordering lock.

Specifications must clearly state reuse of mature native Rust capabilities, the necessary C# surface, exact ABI/state machines/ownership/lifetimes, errors/cancellation/concurrency/resource release, platform restrictions, implementation examples and verifiable acceptance criteria. Ordinary entities without Rust compilation, no reimplementation of SQL/network engines in C#, a small Core and the mandatory Rust Server boundary are constraints.

Technical contract acceptance binds a nonempty spec, version, content hash, actual research evidence and independent review. Complete product implementation and actual release/sustained-load/performance validation are separate Delivery obligations; they must not create a cycle in which implementation must precede acceptance of the design that guides it. Illustrative code must be marked as uncompiled; actual execution may cite only the corresponding source and logs.

A fragment only elaborates concrete steps, scopes, interfaces, error behavior and acceptance criteria for its corresponding existing Delivery tasks; the three graphs remain the sole scheduling authority. During integration, validate fragment/graph content equality, 114 packet hashes, ownership conflicts and local dependencies. Any content change invalidates the old review; historical records retain their original bytes and scope of applicability.
