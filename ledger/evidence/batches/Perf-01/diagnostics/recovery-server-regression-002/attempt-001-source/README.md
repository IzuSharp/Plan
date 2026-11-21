# Perf-01 epoch002 selected Server managed regressions

**Local control source only; not executed by this preparation.** This caller
adds the remaining B17/B19 managed fixture checks against the actual selected
`ccff42c0df4141984ef9de497af7cd768753704a` Server asset. It does not replace the
21 native regression tests, full B18, current CI, API or package evidence.
It is not either module's complete native-producing verifier.

## Exact scope

| Module | Original fixture | Runtime checks |
|---|---|---|
| B17 | `tests/Server.Native/Server.Native.Tests.csproj`, unchanged `Program.cs` and retirement fixture | Release JIT and Linux x64 AOT; original90s runtime limit; four HTTP/1.1 / HTTP/2 clear/TLS transport markers, the final-lease retirement marker, and complete PASS B17 counters with the correct dynamic-code value. Historical105checks/43dispatches are observations, not newly imposed constants. |
| B19 | `tests/Protocols.Mcp/Protocols.Mcp.Tests.csproj`, complete default `Program.cs` path | Release JIT and Linux x64 AOT; original verifier600s bound; JIT>=230assertions, AOT assertion count equal to JIT, positive retirement observations in both, correct dynamic-code values. No early-return fixture selector is passed; layout, lifecycle, undecided and managed-tail cases stay in the default suite. |

Each project receives six managed commands: locked JIT restore, Release build,
original JIT run, locked AOT restore, Release AOT publish and original AOT run.
B19 command shapes and count rules follow its original verifier. B17 retains
its original fixture and90s bound while using the explicitly requested
Release/locked-restore preparation instead of the original verifier's implicit
Debug build. Build/publish use the existing `NativeWeaveServerAssetPath`
property; AOT keeps the original project's Linux x64 flags. No new fixture,
MSBuild target, native ABI, product source or acceptance marker is introduced.
The B17 build/publish bounds remain 300/900 seconds; the newly separated locked
restores receive the corresponding bound. B19 retains 600 seconds per command.

## Actual identities and finite ownership

The canonical measurement `Context` is reused with the immutable actual
baseline/common admission and separate explicit final binding. It validates
the reviewed build caller, complete after build/B18 receipts, selected commit,
paired package closure, toolchain, dependencies and source. The original
build source index remains `268d10b6…`; the canonical measurement interface is
`a71deb12…`. This scope has its own source index and changes neither one.

The same existing exclusive reservation is acquired before expensive admission
reads. `Run.command` delegates every child to unchanged `recovery-build-001`
ownership, with terminal exit, log hashes and descendant retirement retained.
The root caller stays on CPU8; managed commands use CPUs2,3. A process is never
signalled from a remembered PID. Interruptions preserve failure receipts and
partial output; another attempt needs a new label.

There are two additional owned setup commands, one detached worktree per
module at the exact selected commit. The original `build.freshness` helper
checks that project bin/obj directories are absent. Worktrees preserve normal
Git/MSBuild source identity and remain available for diagnosis. A fresh NuGet
cache belongs to each module; its sequential JIT/AOT commands share only that
new cache. Original source cleanliness is checked around managed commands.

The actual after binding's `engineId=server` file is copied to new input space
and hashed. `cargo`, `rustc` and `rustup` traps prevent accidental component
rebuilds. Existing shared-compilation/node-reuse disabling flags are retained.
Generated facade asset metadata and every runtime Server copy must match the
selected hash. Actual JIT DLL/AOT executable identities are recorded before
and after each fixture.

During the four runtime commands only, a read-only observer reuses the original
`src/Benchmarks.Domain/common.py::mapping_sample`. It waits for the actual
original owner's worker record, checks PID plus procfs start ticks before and
after reading/hash verification, and requires one expected Server native
mapping. It does not infer RSS or allocation from virtual mappings, and does
not control process lifetime. Missing or contradictory mapping proof fails
this subset caller even if the fixture exits zero. There is no performance
credit and no new timing/statistics algorithm.

B17 mode-specific `NW_SERVER_EVIDENCE` directories and temporary directories
are new and separate. The caller uses a private umask so fixture-generated
test TLS keys stay private. B19 receives its unmodified default arguments.
No B24 native manifest is fed into B19's different composed-build verifier
schema; this subset consumes the asset through the original project property.

## Root-only execution interface

The following variables are actual operator inputs. No completed after
descriptor or future receipt is supplied by this source preparation:

```bash
taskset --cpu-list 8 "$PERF01_PYTHON" "$PERF01_SERVER_REGRESSION_CALLER" \
  --root "$PERF01_ROOT" \
  --admission "$PERF01_ADMISSION" \
  --admission-sha256 "$PERF01_ADMISSION_SHA256" \
  --final-binding "$PERF01_FINAL_BINDING" \
  --final-binding-sha256 "$PERF01_FINAL_BINDING_SHA256" \
  --source-index-sha256 "$PERF01_SERVER_REGRESSION_INDEX_SHA256" \
  --label selected-server-001
```

Outputs use a fresh `server-regression-001` sibling of the formal output root.
Do not overlap any formal/noise timing or producer build. The original owner
retains actual argv and local evidence paths; the outer record separately
records the narrowly scoped per-command environment overrides used by the
unchanged `Run.command`. Those control records, caches and TLS files stay
local. Root may curate the completed subset outcome/source/native identities
for project evidence after actual execution and review. Do not publish these
private runtime maps as a performance bundle or claim complete B17/B19
acceptance from these managed subsets.
