# Recovery 04 — one private relation capacity hypothesis

The actual two-provider deep diagnostic at source `5b330a24b55332fbbd463b146acd228ae7acbc14` records 128 checked related32 requests/provider, 523,296 bounded records/provider, zero loss, same-thread controls, one SQL, original 53-row digest and zero native owners. It has no ordinary timing credit. Original artifacts are in `experiments/relations-recovery-04` and are awaiting the next immutable archive append.

After the already measured private clone removal, every SelectParent branch grows 256 -> 512 -> 1024 -> 2048. The root also grows to4096 and8192 during Combine. Exactly98 growth allocations use129,328 managed B/business and copy63,488 old-capacity B. Final graph allocation60,504 B is a distinct, unmodified cost. New scope machine code and matching ELF/debug identities are retained. This direct observation justifies one more isolated resource hypothesis before freeze.

## Proposed bounded experiment, not measured benefit

Reserve capacity only for a fresh private LoadRelatedAsync branch, using the first fully constructed branch's actual capacity, capped at2048. Only apply a hint when the next immutable key has the same encoded component lengths as the first key, so an unusually wide first key cannot cause extra reservation for short later keys. Retain the ordinary fallback for differing lengths, oversized commands and unsupported/nonempty builder state. Do not cache user data, share a mutable command, use a global initial-size change, pool buffers or change public From/Combine.

Preserve the existing input snapshot, complete key/projection validation, per-record quotas, error order, geometric growth fallback, admission gates and ownership. The reserve operation must not add an early resource-limit exception or claim protocol bytes from buffer capacity. Run under the existing private admission gate. Any source-observed obstacle to these boundaries rejects this hypothesis rather than weakening a gate.

For the existing equal-size case, keeping the original256-byte initial arrays and reserving31 *2048 predicts98 ->36 allocations,129,328 ->80,224 B, and63,488 ->7,936 copied B if empty reserve copies no bytes. The predicted49,104 B saving is not a measured result and excludes any new helper overhead. If From already emits bytes, measure actual used-byte copying instead of asserting zero.

Required controls: parent count1/2/32; wide-first/narrow-rest and narrow-first/wide-rest keys; equal-size nonidentical immutable keys; duplicate positions; empty input; envelope/node/depth limits; public Combine reuse; original row/digest, SQL, protocol, generated-reader and ownership checks. Diagnose counts/bytes with unchanged scopes, then run matched reversed ordinary related32 and public union-all controls on both providers. Retain only a repeatable resource benefit without correctness or meaningful mixed regression. Do not fold the separate GraphFrame allocation into this experiment.
