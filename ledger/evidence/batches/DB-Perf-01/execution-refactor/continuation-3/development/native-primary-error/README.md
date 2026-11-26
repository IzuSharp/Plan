# Primary-error precedence: development repro and correction

The accepted lazy request's original error must survive an exception while
cleaning up its admission gate. The one-line original repro failed this oracle:
[native-pull-primary-repro.log](native-pull-primary-repro.log). Its build log
contains two incremental compilation/link steps.

The repro used `host.cpp` from native development commit
`22a856a97850c1753a198a057087e61f73853109` with the `missing_pull_table` /
`prepare_failure` additions then present in an uncommitted streaming-test worktree.
Those test additions were subsequently committed in
`a781e51d23c2e858605fd9f4592c90ddc29129ed`. The source inputs are archived here;
this is **not** a claim that unmodified clean22a856a ran that new assertion.
The short original logs do not include their argv or a complete source/binary
receipt. That limitation is retained.

The fixed source is a781e51 (integrated by the root as be068ca and included in
public0f3816c). [native-pull-primary-fix-test.log](native-pull-primary-fix-test.log)
reports 4/4 ctest targets passed: transactions, streaming, database C ABI and
relations ABI, 0.97seconds total. Build and format logs are retained separately.
The prior handoff's 265 streaming-assertion number is not embedded in this ctest
log and is not attributed to this log as a recomputable total.

The following are equivalent recovery commands derived from the build layout
and target logs, not an original recorded argv. Use the locked toolchain and a
configured development build of the fixed source. No command was rerun while
archiving this evidence.

```sh
cmake --build artifacts/cmake/linux-x64-release --target \
  nw_streaming_tests nw_transaction_tests nw_database_abi_c nw_relations_abi_tests
ctest --test-dir artifacts/cmake/linux-x64-release \
  -R 'native\.(transactions|streaming|database\.abi|relations\.abi)$' \
  --output-on-failure
```

The complete source-bound real PostgreSQL development run at a781e51 is a
different evidence group under [native-pg-a781](../../native-pg-a781/summary.json).
Neither group is relabeled as the final public package's entire local suite.
