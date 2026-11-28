# Documentation policy

The existing D01–D21 tasks define specifications; D22–D31 elaborate existing
Delivery tasks through ten fragments; D32 summarizes review/readiness. The three
graphs are the scheduling authority. Research and documentation may proceed in
parallel according to their explicit dependencies.

Describe interfaces, ownership, lifetime/state transitions, errors, cancellation,
threading, platform constraints and verifiable acceptance. Explain native reuse
and ordinary C# consumer behavior. Mark illustrative code as uncompiled when it
has not been built. Product execution, release and performance acceptance are
separate from design acceptance.

Record substantive review findings against the changed source/contract revision.
Preserve the meaning of accepted historical decisions while making later changes
explicit. Keep final documents in Git; leave intermediate outputs, copied source
snapshots and recovery state on the execution machine. Register every added or
moved document as described in [AGENTS.md](AGENTS.md).
