# ORM-CUTOVER — execute the fixed coexistence and consumer migration procedure

Status: `planned_candidate`; product implementation, publication and cutover are
not authorized by this research plan.

## Gate, policy and bounded ownership

Start after accepted ORM-ACCEPTANCE. The accepted candidate's exact source/packages
and current authorization are required inputs. The policy is already selected:
new Korda.Orm package IDs coexist with existing Korda.Database provider products;
there is no in-place binary replacement, automatic compatibility facade through
the old native executor, or incidental database schema migration. This task does
not choose a different package strategy.

Initially own `docs/orm/migration/`, `samples/orm/migration/` and
`packaging/orm/release-metadata/`. Before touching an existing consumer/current-product
entry point, prepare the exact maintained file manifest below, update the reviewed
packet/graph scopes and obtain the required action authorization if it has not
already been supplied. The present graph does not authorize an unnamed directory
of production consumers. Retirement remains a separate task.

## Required files and exact content

| File | Content |
| --- | --- |
| docs/orm/migration/guide.md | Old/new API mapping table, semantic differences, package/runtime requirements, local build, rollout and rollback commands |
| docs/orm/migration/consumer-manifest.json | Version1 concrete consumer/file inventory, current package/version and target package/version, operation list, owner, status and validation case IDs |
| docs/orm/migration/rollout.md | Accepted candidate pins, exact authorized switch scope, preconditions, execution checkpoints, rollback and result |
| samples/orm/migration/{sqlite,postgres,mysql}/ | One independently restorable comparison app per provider; MariaDB is an explicit MySql app profile |
| packaging/orm/release-metadata/candidate.json | Seven exact package IDs/versions/fingerprints, accepted commits and permitted release action; no credentials or binaries |

consumer-manifest.json has `schemaVersion:1`, `candidateCommit`, `acceptedReport`,
`consumers[]`. Each consumer has `id`, `root`, `files[]`, `oldPackages[]`,
`newPackages[]`, `operations[]`, `owner`, `status` and `caseIds[]`. Each file entry
contains path, baseline Git blob ID, intended edit and rollback source commit.
Status is inventoried, authorized, converted, validated, switched or retained-old.
Unknown external consumers remain retained-old and do not become an excuse to
remove old package availability.

## Mechanical migration sequence

1. Verify acceptance record matches exact candidate source/package fingerprints.
   Record the currently deployed/published old versions. Inventory project refs,
   package refs, native loader calls and actual business entry points using rg and
   the existing package/project manifests. The inspected old product baseline is
   36bd5ba169b628ba4d61dd9fe260eaef5ff15599; it is a research input, not permission
   to assume the future repository has not changed.
2. For each selected consumer, fill the concrete manifest and its operation/case
   table before editing. Do not include unrelated old performance/native code.
3. Add the relevant new provider package plus generator when automatic DTO mapping
   is used. Preserve the old package reference until that consumer's scenarios
   pass; aliases/fully qualified namespaces may be used during side-by-side tests.
4. For stable catalog-backed entities use a reviewed version1 offline schema
   snapshot; for existing ad-hoc/derived declarations use handwritten typed metadata
   and record that classification in the manifest. This fixed rule avoids choosing
   a new metadata architecture during migration. Replace query expressions using the fixed
   Field/Query/DML API and add explicit unsupported-semantics decisions from the
   guide. Do not manufacture a lossy translation for an old behavior.
5. Replace DTO annotations with DbRow/DbConstructor/DbColumn/DbNested as needed and
   ensure the final application has the generator or explicit static registrations.
   Compile the generated projection helpers and native consumer, including generic
   facade/cross-assembly registration cases.
6. Replace old session/transaction ownership with explicit new provider sessions.
   Preserve externally supplied transaction boundaries. A failed commit remains an
   unknown outcome; do not introduce automatic retries as a migration convenience.
7. Run old and new reads on the same deterministic snapshot. Run writes in separate
   fresh databases or rolled-back transactions so one path cannot alter the other
   path's baseline. Compare row values/order/cardinality/errors/affected-row policy,
   not only SQL text or successful builds.
8. After validation, switch only authorized entry points and remove their now-unused
   old package references. Leave old implementation modules and other consumers
   untouched. Publish only if that exact action is separately authorized, using
   verified artifacts and the existing trusted release process.
9. Execute the recorded rollback rehearsal against a disposable deployment: restore
   prior package versions/configuration/entry-point commit, rebuild native output
   and run the baseline business scenarios. This task performs no schema/data change
   that would prevent that rollback. Any newly requested schema change is separate.

## Required migration mappings and cases

The guide contains one row per actual old API encountered: old symbol, new exact
symbol, semantic difference, required source edit, case ID and unsupported outcome.
At minimum cover connection ownership, transactions/savepoints, optional WHERE,
nullable fields, IN lists, known DTO/init/record mappings, joins, aggregate carrier
changes, RETURNING/affected-row conventions, cancellation, timeout and streaming.
Do not claim source compatibility where names/types/NULL semantics differ.

| ID | Scenario | Required observed outcome |
| --- | --- | --- |
| CUT-01 | Read users with optional age/name filters | Same intended IDs/order/DTO nullability under the documented semantics |
| CUT-02 | Insert/update/delete in a caller transaction, then rollback | Same original five users afterward; no implicit commit |
| CUT-03 | Early stream exit and following command | No leaked reader/lease; connection remains usable |
| CUT-04 | Pre-cancel/in-flight cancel/timeout | Documented provider behavior; errors not converted to empty success |
| CUT-05 | Old feature absent in new supported matrix | Explicit retained-old or approved application change; no silent clause omission |
| CUT-06 | Generated model change followed by clean local publish | No live database/Java/C++ query build required; native execution succeeds |
| CUT-07 | Both package families in one process during comparison | No assembly/native-asset identity collision or accidental old execution dependency |
| CUT-08 | Exact candidate package restoration | Correct versions/fingerprints; no substitution from a global cache |
| CUT-09 | Rollback rehearsal | Prior published product/entry point restored and baseline scenarios pass |
| CUT-10 | Switch manifest versus actual diff | Every modified existing file authorized and accounted for |

Each sample has `verify.py` with `--profile` and `--old-version`/`--new-version`
inputs; it uses disposable fixtures and isolated package caches. Keep detailed
logs/results temporary and record only concise maintained migration outcomes.
After the recorded switch, report remaining retained-old consumers. Stop without
legacy deletion; ORM-RETIRE requires its own proof and concrete authorized manifest.

The cancellation/timeout reproduction is provider-specific: PostgreSQL/MySQL/
MariaDB exercise actual in-flight cancellation and one-second execution timeout.
SQLite exercises pre-cancel and its declared busy-timeout behavior; it does not
claim an interrupt of an already-running sqlite3_step. Unsupported cancellation
capability is an explicit recorded outcome, not a fake Task.Run timeout test.
