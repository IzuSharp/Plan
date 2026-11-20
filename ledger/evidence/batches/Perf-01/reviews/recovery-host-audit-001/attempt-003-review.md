# Recovery epoch 001: attempt 003 runtime input review

**ACCEPT for the bounded runtime input change, subject to the declared
dependency-file admission.** This review read source and small controls only.
It did not import Python packages, run a constructor check, rehash installed
payloads, execute a producer or start a workload.

| Identity | SHA-256 |
| --- | --- |
| Actual attempt003 runtime input | `661e74d7bed97bee9a29dce6a699e06b681412c7199b1c07b551d49be380a013` |
| Preceding attempt002 runtime input | `8898e8c1fadcd97cd356c72dbc11e105ce7dbb458b2dd231a61e71c7d48be38d` |
| Unchanged accepted builder source index | `c7526f08d3c50c6d58f7336adae6ebab5fb82b606cce140108a48f6b54b3d0ab` |
| Fixed task-local Python HTTP/2 dependency manifest | `1584ba1bf4c27fda85a8054bfe0dc84a6330d52b10e4f74e8b022fd1104eaddb` |
| Actual failed attempt002 outer receipt | `a7fb57acb2d09f6df58390d6be3d6bb51a36aa3714d9d38d4e8ad18a3fb3dad4` |

The recursive input diff selects a fresh before checkout, fresh build/control
roots, `attempt=3`, and the actual prior failure descriptor. It adds one explicit
task-local `PYTHONPATH` and a separately hash-pinned `python_dependencies`
descriptor. Product commits and package versions, native and managed flags,
toolchain, boot/workload freeze, timing lock, operational free-space floors and
all original producer options remain unchanged. This is a complete fresh build;
the two completed producers from attempt002 are not reused as a prefix.

The preceding actual attempt completed the native and package commands, then
the reference controller failed on missing `h2` distribution metadata before
its application build commands. Its failed owner and child records remain
failed; no application, functional or performance acceptance follows from them.
Attempt001's separate unknown terminal outcome is not repaired by this event.

The repository requirement remains `httpx[http2]==0.28.1`. The new manifest
separately identifies the three wheels, 51 installed files, license files and
actual distribution versions. It describes a task-local installation and no
upgrade to a preinstalled distribution. The reviewer did not repeat the root's
installation or its retained failed/successful constructor-only checks.

The historical public control
`checks/postgresql-before-long-invalid-001/frozen-inputs.json`, SHA-256
`5b80cbdf194bf968bd406739f8bcf4e36e9cd2d145a25b76b899de4b33dda5d5`,
records all six corresponding versions:

| Distribution | Historical recorded version | New declared version |
| --- | --- | --- |
| httpx | 0.28.1 | 0.28.1 |
| httpcore | 1.0.9 | 1.0.9 |
| h11 | 0.16.0 | 0.16.0 |
| h2 | 4.4.1 | 4.4.1 |
| hpack | 4.2.0 | 4.2.0 |
| hyperframe | 6.1.0 | 6.1.0 |

This historical control establishes version observations only. It is not a
validity or timing result, and matching versions do not establish historical
binary equality. The repository's own transitive requirements are not rewritten.

The accepted builder consumes the explicit environment but does not implement
the newly declared bundle check itself. Root therefore retains responsibility
for the promised manifest and installed-file verification before each build
stage. Measurement admission must bind and verify the same complete bundle and
actual import locations, with the same environment for all compared roles.
The OFF caller and generic measurement preparation must be rebound from the
now obsolete attempt002 prerequisite to actual attempt003 identities before use.

All new producers, actual package/native bindings, functional gates, fresh noise
and ten current-epoch long segments remain outstanding requirements. This note
adds no build completion, measurement duration or performance credit.
