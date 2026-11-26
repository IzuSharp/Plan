# FFI overlay compilation failure and tool-only correction

`diagnostic-build.json`, `shim.log` and `probe.c` are the unchanged failed
candidate-SQLite diagnostic outputs. The generated shim sees 53 real exports.
The new pull `take` / `take_error` signatures contain an output parameter named
`result`; the shim generator also named its local return status `result`.
Clang rejected the duplicate declaration and consequent type errors under
`-Werror` before the overlay could be executed.

The product/package source remains public
`0f3816c4006488821f40afde91bbbd717d57ccd6`. This is a standalone diagnostic-tool
failure and grants no product-failure, performance or allocation observation.

The separate local tool commit7d6d5f8 changes only
`benchmarks/db-perf/cursor-diagnostics/build.py`. Its exact original/fixed
builder bytes and complete Git patch are retained under `tool-sources/` and
`tool-only-fix.patch`. The correction assigns a non-conflicting generated status
name; it does not modify the ordinary native image or provider package.
Later rebuilt overlays require their own receipts and are not inferred to
have succeeded from this patch alone.
