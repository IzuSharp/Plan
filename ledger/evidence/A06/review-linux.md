# A06 independent Linux review

Reviewer: Task-04 root, independent of the callbacks implementation owner.
Reviewed final implementation b340601d20072385ba3ea61e447a6f955f250541,
its source predecessors and the linked actual failure/fix receipts.

## Scope and findings

Reviewed static nongeneric Cdecl UCO ABI, strong-cookie publication and setup races,
logical/physical native controls, copied dispatch bounds including active handlers,
exception containment, decision self-wait rejection, source/callback/handler drain,
preallocated scheduler retry and finite test limitations. Native subscription state
closes admission under its own mutex; arbitrary managed work executes outside it.
Root retirement follows native quiet plus managed leases and handlers, not Task or
callback completion alone. Coordinator rejection keeps roots and bounded retry state.

- A06-R1: an admitted decision callback crossing managed close returned OK without
  executing its decision. The native admission-gate regression failed before the fix;
  the fail-closed result passes in actual JIT/AOT. Notification discard semantics
  remain separately documented.
- A06-R2: an actual downstream cdylib exported all eleven callback fixture symbols.
  The opt-in conformance feature removes that fixture from default reuse. A real
  downstream link now exports only its intended probe entry; native tests/Clippy and
  existing JIT/AOT component/sample executables were revalidated with the new asset.

Both findings are resolved. No open release-blocking finding remains in A06's Linux
component scope. API/XML/generated reference and inaccessible-plumbing checks pass.
This is independent technical review, not a GitHub approval or whole-batch certification.

## Evidence interpretation

[acceptance-linux.json](acceptance-linux.json) preserves the exact original receipts.
The first composite run remains failed because of a later sample compile diagnostic;
its successful native/runtime inputs match the validated implementation. A clean
follow-up proves the fixed sample and remaining API/UCO gates. The later native feature
boundary has its own exact export and execution record. No execution is relabelled as
having run on a different full commit. Windows, pristine packaging, mature engines,
long-running load and performance claims are outside this component evidence.
