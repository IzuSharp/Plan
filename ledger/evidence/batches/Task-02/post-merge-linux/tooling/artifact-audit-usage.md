# Task-02 retained release artifact audit

`audit-release-artifacts.py` reads the downloaded **candidate** and **publication** ZIPs from the normal existing HelloWorld release workflow. It does not run tests, publish, access credentials, use the network, extract archives or change a repository. Run it only after obtaining the actual merge SHA and the version allocated by the release identity job.

```bash
python3 audit-release-artifacts.py \
  --candidate /absolute/path/nativeweave-linux-RUN-PRODUCER_ATTEMPT.zip \
  --publication /absolute/path/nativeweave-publication-RUN-PUBLISH_ATTEMPT.zip \
  --merge ACTUAL_MERGED_MAIN_COMMIT_SHA \
  --version ALLOCATED_PREVIEW_VERSION \
  --output /absolute/path/new-audit-directory
```

The output directory must not already exist. A failed or incomplete audit is retained rather than overwritten. Exit 0 means the supplied artifact records are consistent; exit 1 means a missing record, mismatched identity, unsafe archive or failed evidence check. Invalid arguments and an existing output directory stop before an audit. The artifact producer and publisher attempt numbers may differ after a failed-job rerun.

## Checks and retained evidence

- Candidate `SHA256SUMS` binds exactly the package and external manifest. The external and embedded manifests agree; package/RID/version match `NativeWeave.HelloWorld`, `linux-x64` and the requested version. The candidate is clean and identifies the supplied actual merge SHA. The native asset's actual bytes match the manifest's SHA-256.
- Publication status is exactly `published-and-consumed`, its version matches, and `signatureVerified`, `unsignedPayloadEntriesEqual` and `registryPackageJitAndAotExecuted` are actual JSON `true` values. The upload hash matches the retained candidate nupkg.
- The registry consumer's package/RID, package hash and native hash agree with the release records. All five current execution/isolation flags are true. `pristineMachine` is explicitly false, as declared by the existing registry-consumer schema; this does not claim a pristine registry host.
- Both HelloWorld runtime logs contain the exact greeting, and both InteropTests runtime logs contain the existing exact PASS summary. The two AOT publish logs contain native-generation and published-output markers. The successful publisher receipt and current `eng/build.py` implementation supply the command-success and actual-executable context; raw logs alone are not a fresh execution.

`audit.json` preserves input ZIP identities, observed member paths, check results, scope and limitations. `raw/` preserves the selected JSON, checksum and six log files byte for byte under fixed safe filenames. `SHA256SUMS` binds every output file except itself. ZIP members are read directly; unsafe paths, ambiguous bundle records, duplicate members, symlinks and encrypted entries are rejected. A 256 MiB per-member local reader bound protects this review utility; it does not change product acceptance limits.

The candidate package hash **does not need to equal** the signed registry package hash. The registry consumer hash must equal `publication.registrySha256`; the candidate nupkg hash must equal `publication.uploadSha256`. These are separate checks because NuGet signing may change ZIP bytes. The audit also hashes each outer artifact ZIP independently; those outer hashes are not nupkg hashes.

## Scope that remains with normal closeout

Confirm the GitHub artifact ID/digest, run event and exact merge SHA, successful CI/security/publication jobs, and the publishing job's actual `dotnet nuget verify --all` result using the existing workflow evidence. These are not established by standalone artifact contents. The publication ZIP does not include the downloaded registry nupkg, so signature verification and unsigned-payload comparison remain publisher-attested results; this utility does not independently repeat them.

The candidate's separate Rust-free container evidence is not part of the two supplied ZIPs and must not be relabeled as registry pristine-machine verification. The audit covers the normally published HelloWorld preview only; it makes no claim that Task-02 component packages or other platforms were published.

`artifact-audit-source-bindings.json` records the inspected current workflow/publisher/consumer source and exact console-output sources. `artifact-audit-selfcheck.json` is only a synthetic parser/cross-record check of this utility, never a Task-02 publication or package-consumption receipt.
