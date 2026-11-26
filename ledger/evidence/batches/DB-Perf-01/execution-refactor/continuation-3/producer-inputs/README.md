# Final public-source native build inputs

The two `candidate-native-*` directories contain unchanged native-producer
manifests and command logs. Both bind public source
`0f3816c4006488821f40afde91bbbd717d57ccd6`, tree
`9935773d28b3043618285cf0ecd5c476539b2f8c`, and configure/build/install exit0.
Each producer uses its own independent provider profile. The manifests retain
dependency, toolchain, command and output-image hashes; binary images are not
duplicated into this archive.

| Profile | Produced image SHA-256 |
| --- | --- |
| SQLite | `139512bac39ce301c5bddc5af8eaa6e8adfc6a1d11d7469411d4432270992d9c` |
| PostgreSQL | `bb5f31a2e23a55dc8fbc8b1e8512837e9c8d4f5c4821bf02db59c4bf741ea6d5` |

The four ordinary final candidate consumer build receipts in
[consumer-inputs](../consumer-inputs.README.md) record successful local
PackageReference Native AOT compilation against the independent provider
packages. They bind the package archives and native images used by each
consumer. This archive grants compilation credit only, without claiming those
executables ran the full correctness suite or measured a query.

`candidate-freeze-source.json` is the unchanged source-freeze observation. Its
`finalPublicCi: pending` field is historical. The later independent final CI
observation is [0f3816c-ci-45734731584-final.json](../public-ci/0f3816c-ci-45734731584-final.json).
