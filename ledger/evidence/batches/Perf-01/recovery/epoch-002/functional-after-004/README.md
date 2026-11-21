# Epoch-002 actual selected after-004 B18 verification

The selected final candidate `2f40348c3db80a4fbee7a99e721b374a597b16df` completed the original B18 native component and assembled gRPC verification from `2026-11-21T04:45:11.063866+00:00` to `2026-11-21T04:58:01.056596+00:00`. Both outer owned commands exited zero and fully retired with no remaining owned process or owner child and no cleanup signal. The immutable before/common admission is unchanged.

The actual application and package consumers used Server SHA-256 `8b726c39ec30003479aeb5b28015fcb97ee5350246a9d7b1bcd7b4ee696f78c0` (**8815464 bytes**), from the [actual after-004 build](../built-after-004/README.md). This is B18 Linux x64 functional evidence. It grants **0 seconds of performance or formal 30-minute test credit**.

## Actual owned command results

| Owner command | Start UTC | End UTC | Seconds | Exit | Retired |
|---|---|---|---:|---:|---|
| native-component | 2026-11-21T04:45:12.776058+00:00 | 2026-11-21T04:54:08.570854+00:00 | 535.795 | 0 | yes |
| assembled-b18 | 2026-11-21T04:54:09.605319+00:00 | 2026-11-21T04:57:59.673981+00:00 | 230.069 | 0 | yes |

The native component verifier ran 11 original child commands. The assembled verifier ran 18, including the package probe; that probe records 25 child commands of its own. All child command exits and bound log hashes were rechecked.

## Component and assembled results

| Check | Actual result |
|---|---|
| leaf-debug | 12 passed; 0 failed; 0 filtered out |
| core-host-debug | 9 passed; 0 failed; 14 filtered out |
| leaf-release | 12 passed; 0 failed; 0 filtered out |
| core-host-release | 9 passed; 0 failed; 14 filtered out |
| JIT | 948 assertions; 577 managed retirements; dynamic code supported |
| Native AOT | 949 assertions; 580 managed retirements; dynamic code unsupported |
| ABI | 48 exports; 8 records; 103 offsets |
| Public API | 71 symbols; 5 compile-negative fixtures |

The component host commands select the gRPC tests; the 14 filtered tests are not claimed as executed by these B18 commands. The leaf commands also completed zero-test documentation targets. Full Server regression evidence remains a separate scope.

The separately built component Server library is `83b57ab59a43975c2396d069d782aeafe86c0ba2d0c94468fdf11800840f3388` (**8179240 bytes**). It is distinct from the supplied application Server library. The original assembled verifier accepted the component receipt with **11 matching gRPC source files** and independently checked the supplied role-bound asset. The component library is not substituted for the final application asset.

The actual assembled JIT and Native AOT logs confirm independent-client cancellation, the whole-call deadline after response headers, completed-call ownership release while TLS HTTP/2 connections remain reusable, and pressure-grant/partial-admission retirement to zero. Correctness assertions and retirement counts describe this fixture execution; they are not equal-work timing comparisons with the before version.

## Ordinary package consumers and native reuse

The original B18 package probe produced five `0.1.0-preview.1` component packages. This set is separate from the seventeen-package B24 candidate closure used by the performance applications.

| Package | Bytes | SHA-256 |
|---|---:|---|
| NativeWeave.Interop.Abi | 6218 | `aceee947224f1f003a2e1f8dbe610805a4bd13aa9364b9b81a8fd244786e9930` |
| NativeWeave.Core | 53618 | `9fb5921c953e86a48045a021a33bfc035ee21700a002b00ca8acf277f23e19cf` |
| NativeWeave.Server.Generator | 14516 | `cab5b717b3dc38acffa3127b9672597012cb98f62d0019f70e39a5baed5d3fbc` |
| NativeWeave.Server | 3303753 | `8c7afe76d463388b3b6e458da6cf8d1683301ae360eff3cadf7db202ec4e39fc` |
| NativeWeave.Server.Grpc | 53516 | `483c92bb761db10c293e0550f35a59434652f4ca370b7a8ffda403e85e3b2ad8` |

All eight ordinary consumer executions exited zero:

| Consumer | PASS observations | Four cardinalities | HTTP/2 + TLS | Actual Native AOT | Bounded owner close |
|---|---:|---|---|---|---|
| consumer-jit-minimal | 4 | not this run | not this run | not this run | yes |
| consumer-jit-advanced-clear | 13 | yes | not this run | not this run | yes |
| consumer-jit-advanced-tls | 13 | yes | yes | not this run | yes |
| consumer-aot-minimal | 5 | not this run | not this run | yes | yes |
| consumer-aot-advanced-clear | 14 | yes | not this run | yes | yes |
| consumer-aot-advanced-tls | 14 | yes | yes | yes | yes |
| edited-jit-execute | 13 | yes | yes | not this run | yes |
| edited-aot-execute | 14 | yes | yes | yes | yes |

The advanced consumers exercised unary, server streaming, client streaming with explicit input half-close, and duplex response before input half-close. Their logs confirm binary metadata, explicit status/error trailers and the native whole-call deadline after response headers. The TLS consumers used real HTTP/2 with rustls. AOT consumers explicitly observed dynamic code disabled.

Package-reference-only consumption used an isolated NuGet cache with no accessible Rust toolchain, no parent-repository imports and no root descriptors or trim suppressions; the Rust trap did not fire. Two statically generated protobuf services were consumed. Ordinary proto/DTO/handler edits changed the managed JIT and Native AOT executable identities while all four selected SDK output identities retained the same Server native hash.

| Consumer executable | SHA-256 |
|---|---|
| jit | `be24ad860248b445548fbabef62972ac32edd68e3a5784cfe0e71e5c25e9bb63` |
| aot | `2098783e16e4698eae89de4a274d3ab557098a74c3441ea4c054ad0f9975ea1e` |
| edited_jit | `ef6b64ba6a4e6df3379ec526ad6fc62c7d8bac345c625fe051dff3495fcc30bd` |
| edited_aot | `201aedb5550cf3612209f3f8b4098b27fc6e2e62a9a4455a5dff969fdb10039d` |

The intentional edited build replaced the initial JIT output. Its immutable source/lock snapshot and before-execution hash receipt are retained by the original verifier; this projection does not claim that the overwritten initial output still exists. The edited JIT executable/dependencies/native inputs remain bound independently of the sibling AOT compilation directory.

## Preserved invocation preflight rejection

Before the successful functional stage, one invocation supplied an incomplete admission SHA-256 argument. The immutable-baseline admission check rejected it with exit code 1 **before any fixture or output was created**. The operator corrected the argument to the already frozen admission hash; admission and caller source were not changed. The local record filename is `functional-after004-preflight-001.json`, SHA-256 `778308e197697d55c55c47bbe1cf901778e59a4f3680beac7f3caff7c83b1d03`. Its record does not provide an actual timestamp. This is a preserved invocation preflight rejection, not an executed B18 fixture failure, and it carries zero performance credit.

## Provenance and readback

- Functional execution: `ce45385d9e5727840b38912404099cd6eb02f731357f3a2161494312bb9f3ac1`.
- Functional binding: `d1a43a319701c8fadb64ae01f10299a80067e7e4d27e835dc3e008a8ab2bc003`.
- Final after/before admission descriptor: `8f8616f2932dd1c033309e177efa63429829f9ffa2b728a182406d943efdfa8d`.
- Actual native component result: `79a36155a8b7b5160a775b356eed1eafc0527fc14ba85050ad3f9a8c22c28ab7`.
- Actual assembled result: `f4ab2131b3488a814820b55462ff985820175e75933df194f8eba6c471a72935`.
- Actual package summary: `6a25aa8645ceedf2631969f3b83ab1a2ac68b834abc32579ff35bcc3f9d02118`.

This curation rehashed **342 bound files / 86524160 bytes**, all **54 original child-command logs**, and all **4 outer-owner output logs**. [projection.json](projection.json) includes the exact observations, identities and command/log hashes. The source tree is `7f803d4f9e57fef1d8cfdef69c505d67f84614c9` and the locked Design commit is `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.

Operational maps, absolute workspace paths, process identifiers, command environments and TLS material remain outside the public projection. No new archive or durable readback is claimed. This curation launched no build, fixture, profile or workload. Other module regressions, performance comparisons, capacity, public package release and the required before/after 30-minute tests remain separate actual-evidence gates.
