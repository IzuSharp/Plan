# B21 response golden-vector supplemental review

**Decision:** no open findings in the narrow response-vector delta. The original independent review remains sealed and its six resolved findings are unchanged.

## Exact binding

- Previous application/integration commit: `acb5be54f6a6af4e26048af6f98553a4ac7e41ad`.
- Reviewed integration commit: `11b7d27ba01f4b6e66d04d89d5a77984c393452b`.
- Source helper: `d491a8abdcc1c808da8aa24ad301418b100e5542`.
- Independent Python literals: `15ec950da1af5e8b52d50a6948fbd2f98c7b3072`.
- Changed-file manifest SHA-256: `7ad0f91e17458642ee0656b6b21628889b2b6099b2441ca7c1f593983dc40738`.
- Original review JSON SHA-256: `eb4bda5f41aa04d5e14a1f56d9ecdc548c68bdeea3e050f74a2c074b661bfbe9`.

The four-file manifest covers the helper, guide, independent Python expected bytes and fixture. All 18 other app/guide/sample files in the original manifest remain byte-identical. This manifest excludes itself and review artifacts. The reviewer did not author these changes; the separately reviewer-authored PostgreSQL oracle remains excluded from independent code approval.

## Review conclusions

The only application execution change is `Canonical.WriteGoldenVectors` plus a private output helper. The existing `--golden-vectors` early CLI path reaches it before configuration, native startup or database work. It invokes the existing source-generated `CreatedItem` and `AttachedItem` serializers, so the product output comes from actual response serialization rather than a replacement hand-built response. DTO declarations and serializer registrations did not change.

The Python expected bytes are fixed independent byte literals. They freeze response version, field order, numeric spelling and uppercase Unicode/surrogate escapes. The retained actual product output equals the complete independent fixture. Recomputed vectors are:

| Vector | Bytes | SHA-256 |
| --- | ---: | --- |
| Create | 196 | `1778781abef6361f7ea1d101e2e32844d10a4ef225c64f14f6ced4efa04023e5` |
| Attachment | 233 | `0bd1b41707f6e658b10c7f7688e4a641346e37225e2def5b949dbf624a240f57` |

The inspected build reports zero warnings and errors. Source hashes in the author-run validation record match the reviewed helper and guide. This reviewer recomputed equality from retained actual output; no whole-service matrix was rerun during this review.

HTTP dispatch/authentication, query/transaction semantics, retention, blob ownership, cleanup, package references and native modules are unchanged. The managed-edit probe changes `Item`, `ItemView` and list handlers; it does not change the constructors newly used by the CLI fixture. B21-R1 through B21-R6 therefore remain resolved without reopening or repeating that audit.

## Applicability of earlier matrix rows

There is no concrete acceptance risk requiring all sixteen earlier rows to rerun for this CLI-only delta. Preserve `final-001` rows with their actual `acb5be54` source and artifact/controller identities. The proposed `final-002` supplement—four baseline SQLite/PostgreSQL × JIT/AOT HTTP2-TLS rows using the final application and strengthened controller, plus actual final JIT/AOT golden output—covers the changed path, final compilation/AOT rooting and the new assertions.

Report the sixteen earlier applicable rows, this source-diff assessment and the four actual supplemental rows distinctly. A partial four-row supplement must not be described as a new 16/16 run, and earlier observations must not be relabeled with later executable hashes. This review approves that applicability argument; it does not mark still-running rows as passed.

Incoming controller boundary/retention changes outside the two golden files are outside this narrow supplement. B22/B23/B24 and other-platform acceptance remain separate.
