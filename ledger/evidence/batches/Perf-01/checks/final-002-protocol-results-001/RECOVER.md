# Retrieving the complete numerical evidence

The readable report and coverage checklist are unchanged outputs of the validated
projection. Larger numeric JSON files are delivered as lossless `.json.gz` files.
`delivery-manifest.json` records both stored and decoded sizes and SHA-256 values;
`manifest.json` retains the original projector output hashes. Every compressed
file was decoded and checked byte-for-byte before publication.

For each compressed file, retrieve it and decode with `gzip -dc NAME.json.gz >
NAME.json`; verify the decoded SHA-256 against both manifests. The decoded JSON
contains the complete projected process rows, statistics, resource observations,
source/package/native identities and original classifications. It is not a claim
that the complete operational raw workload bundle has been published.

These synthetic numerical records are retained in Git while repository history
is retained. They remain evidence for the actual `0715` build and provide no
acceptance credit for later candidates. All long-duration evidence is separate.
