# Candidate 4 correction evidence export

This directory contains development evidence for the input-admission correction
after product candidate `3e49cee95d206468a32c94f0a3b98e923f02acbf` (tree
`f696ce6db636a3371ccf52ec777f710afa8c2a55`). It is not formal acceptance of the
next candidate, its packages, or CI. The original failed managed assertion and
the source-3 public-ABI differences remain recorded.

## Contents

- `receipt.json`: frozen five-file source hashes, patch hash, Release/ASan
  results, independent evidence references and explicit validation limits.
- `negative-controls.json`: two external mutants fail for the intended reasons.
  Their failure exit codes are expected evidence, not passing product commands.
- `codec-replay.json` and `codec-logs/`: unchanged, already-built C# JIT/AOT
  programs with newly built C++ provider execution. Each mode completed 120
  scalar roundtrips, 24 original fallibility refusals and 4,189 malformed-input
  refusals. No managed build or embedded asset hash was patched.
- `public-abi/`: eight fixed public-ABI results and their independent old-Rust
  references. `source3/` retains the actual rejected-candidate differences.
- `ci-wiring.json`: the new PostgreSQL Host mode ran in isolated real clusters
  in Release and ASan/UBSan. This records local execution and committed-intent
  wiring; it is not a successful GitHub CI run receipt.
- `git-transport/`: shallow bundle checkout preserved HEAD/tree but failed
  history integrity; a full-history bundle passed clone, fsck and traversal.
  This only validates Git transport. It does not establish a clean container
  build, packaging, runtime, or Rust-free acceptance.
- `review.md`: the independent reviewer report, exported byte-for-byte.
- `advisory-lock-mitigation.md`: report wording and fixed source references.

## Export and verification

JSON evidence follows the existing `eng/build.py::export_fixture_results`
envelope: `sanitized`, `source_artifact_sha256`, and `data`. Raw argv and private
configuration keys are removed. Database URIs and unnecessary Git-author
contact addresses are redacted. The original result files were not modified.
Small stdout summaries appear once; identical JIT/AOT native output and
identical Release/ASan PostgreSQL output are referenced by their shared hash.
No database files, libraries, executables, Git bundles, package archives,
credentials, server logs or full compiler logs are included.

`manifest.json` records the exported bytes and each original source hash.
Run `python3 verify-export.py` from any working directory to check inventory,
export hashes, wrapper/original links, source identity, all eight Rust/fix
comparisons, expected negative outcomes and the Git-transport contrast.

Local ASan/UBSan used `detect_leaks=0`; CI retains its `detect_leaks=1` gate.
The unchanged Orm.Relations assertion, complete regression suite, ordinary
NuGet JIT/AOT comparison and final CI must be rerun on the next committed
candidate. Passing source-3 package evidence is not transferred to it.
