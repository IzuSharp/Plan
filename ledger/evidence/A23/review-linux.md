# A23 independent Linux review

Root reviewed the final native adapter, managed ownership wrapper, callback/close
paths, actual cross-thread consumers and guide independently of the author.
The final source and 37 command output pairs were rehashed; all 82 final source
inputs match. The base native/sample rows are unchanged by the three-file managed
Completion refinement; their original receipt remains separate and unmodified.

The real Rc/Cell remains in owner-thread TLS. Wrong-thread read/pump rejects before
TLS access; cross-thread posting touches only the bounded Send/Sync control queue.
Only successful posts transfer creator ownership. Native command terminal outcomes,
A06 source/callback quiet, managed handler/control drain, callback-root release and
actual owner-thread destruction remain separately observable. A finalizer only
requests deferred release; absent owner progress stays ClosePending. A lost owner
retains bounded per-thread roots without claiming safe destruction.

Final actual JIT and Native AOT each passed 238 assertions and ended with zero live
affine objects, handles, observers and work; 15 owner-thread destructors executed.
The separate Completion path exposes original handler failure while retirement
records cleanup. Exact API/XML/reference checks report zero public runtime symbols.
No open finding remains for this finite Linux probe. No window/GPU/device, mobile,
static/WASM or Windows execution is claimed. This review is technical acceptance,
not a GitHub approval or performance/unbounded-load certification.
