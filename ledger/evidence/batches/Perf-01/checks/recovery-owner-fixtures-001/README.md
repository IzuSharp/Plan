# Recovery build owner: actual finite checks

The actual three-case suite passed at the times in `summary.json`. Normal exit
completed without signalling. The two negative cases correctly retain failed
command receipts: timeout raised `TimeoutError`, and a zero-exit leader was
rejected because its detached child remained live. Both children were terminated
inside their original owner namespace and all three cases retired with empty
owned/adopted child sets. This is no product or performance acceptance.

The first invocation failed during admission before any test child was spawned,
because this executor omits the procfs `children` pseudo-file. Its failure is
preserved. The reviewed adaptation uses numeric procfs stat PPid enumeration;
it retains all admission, adoption and retirement gates. No recorded PID from a
separate execution namespace was used for signalling.

The source and independent review are in
`../../diagnostics/recovery-build-001/` and
`../../reviews/recovery-host-audit-001/build-owner-review.md`.
The original small receipts/logs remain task-local; this committed projection
contains all three intended outcomes and their hashes, with no claim that the
original operational namespace can be resumed from Git.
