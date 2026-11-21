# Candidate7 CI failure — observed

Run: https://github.com/IzuSharp/NativeWeave/actions/runs/44915077874

Attempt1 completed with failure, not cancellation, on source7e050cdd43cbddeed3cbad00007539c353d55a53 / tree53b9be35089c757c23709c533d0d92fe8e67bca1. Both uploaded source receipts match. All four security jobs succeeded; final Verify failed with the build gate.

The first failed stage is database-business in build job136878968260, step9. Reference consumer aot-resolve-candidate and aot-locked-restore both exited0, then the controller raised FileNotFoundError for consumers/aot/packages.linux-x64.aot.lock.json. This was not a NU1004 restore error. Its JIT build had succeeded, but no business runtime row had started. All four preceding lifecycle rows passed.

The copied Reference project hash matches candidate7 and its singular-only AOT lock selector. The already-reviewed local candidate8 adds the plural RuntimeIdentifiers fallback while retaining singular precedence and strict metadata/restore gates. This CI failure matches that known issue; no additional earlier failure was observed. Later-candidate acceptance remains separate.

Artifact14712148610 is1533615 bytes and matches GitHub sha256:e6c6be5bdf21503e9d64b4514f08cbe5ba102cffcb5799bbd2b3928f5ff26d26. The artifact contains a sanitized business progress wrapper, not its original command logs. The declared pre-export raw progress hash is retained separately from the verified uploaded-wrapper hash.

Safe review inputs: failure-observation.json and database-business-failure.sanitized.json. Original ZIP and extracted artifact remain preserved locally.
