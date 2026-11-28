# ORM-ORACLE — build the fixed source-linked conformance corpus

Status: `planned_candidate`; product implementation is not authorized.

## Inputs, scope and dependency gate

Start and accept the harness after Foundation. Use graph-pinned Design validation,
language-model, dialects-and-generation, upstream-policy and implementation-spec;
contracts ORM-C01/C02/C03/C06. Pin jOOQ 3.21.10 source commit
`3c58109e7ab69772de75e640852935ee7e284177` and matching OSS Maven artifacts. An
upstream source symbol is evidence of inherited behavior; it is not a claim that
private jOOQ integration tests were obtained.

Own `tests/Orm/Conformance/` and `eng/orm-oracle/`. Author the corpus independently
of the Korda renderer. Do not implement a second SQL engine, edit product nodes to
make a case pass, fetch databases during ordinary test discovery or persist raw
oracle output. Ordinary consumers use maintained expectations offline; Java is
required only for the explicitly requested regeneration command.

| File | Exact deliverable |
| --- | --- |
| conformance.schema.json | Version1 case format below; reject unknown keys and duplicate IDs |
| cases/{truth,scope,sets,windows,dml,types,nested}/*.json | One maintained semantic case per file, with source symbol and intentional difference |
| CaseModel.cs / CaseJsonContext.cs | Closed typed model and source-generated System.Text.Json context; no Type.GetType |
| FixtureCatalog.cs | Canonical users/departments and node-construction switch keyed by known case ID |
| Comparison.cs | Parameter/result/SQL-token/row comparisons below; diagnostic output excludes secret values |
| NativeConsumer/ | Consumes actual Korda interfaces only when available; until then reports unexecuted implementation cells |
| eng/orm-oracle/pom.xml and src/main/java/.../OracleMain.java | Pinned jOOQ render runner using explicit typed factory cases |
| regenerate.py | Explicit process launcher, dependency/checksum verification, stdout parse, reviewed expectation diff |
| verify.py | Offline fixture-schema, mutation and pure-native checks; no automatic regeneration |

## Exact case schema and comparison contract

Each case contains `schemaVersion:1`, globally unique `id`, `family`, `profiles`,
`upstream:{commit,symbol,path}`, `construction` (one closed fixture key), `parameters`
(ordered logical ID, occurrence ordinal, elementIndex, SQL type, nullability),
`result` (ordered alias/type/nullability/nested shape), `expectedSql` per profile,
`expectedRows`, `expectedDiagnostic` or null, and `difference` or null. A difference
has `reason`, `ruleId`, `expectedKorda` and `upstreamBehavior`. Profile entries are
postgres-18, sqlite-3.45, mysql-8.4 and mariadb-11.8. Unknown case construction keys
fail instead of evaluating arbitrary JSON-supplied C# or SQL.

Represent expected values with a closed tagged union: null, boolean, int64 decimal
string, decimal invariant string, double IEEE bit string, text, bytes hexadecimal,
array of values and ordered row of values. This keeps integers beyond 2^53 and
SQL NULL distinct from JSON literal null. SQL/JSON envelopes follow ORM-NESTED.
Database expected-error entries carry the known category and allowed driver code
set; no blanket 'any exception' passes a semantic case.

SQL normalization is a tokenizer, not a whitespace regex: preserve quoted
identifiers, string/dollar-quoted literals, operator tokens, casts and parameter
occurrences. Ignore whitespace/comments only outside quoted regions. Convert a
placeholder to its recorded occurrence ordinal for comparison; do not renumber
independently of the actual layout. Never sort clauses, drop parentheses, replace
NULL predicates, erase DISTINCT/ORDER/LIMIT or merge repeated placeholders.
A formatting-only difference may pass the token comparison. A deliberate Korda
strictness difference must match its separate expected result and rule ID.

Every ordered fixture supplies an explicit unique tie-breaker and then compares
position/value. A case intentionally testing ties compares each equal-sort-key
group as a multiset; SQL does not promise order within that group. Rows without ORDER compare
multisets with multiplicity, never sets. Approximate float comparison requires an
explicit case tolerance and cannot apply to integer/decimal/identity/NULL cases.
Compare result shape and parameter layout separately from result rows. Matching
rows on an accidental small fixture do not excuse wrong layout or dropped clauses.

### Concrete fixture and dependency lock

The maintained case below fixes the JSON field spelling and scalar representation:

```json
{
  "schemaVersion": 1,
  "id": "ORACLE-NULL-01",
  "family": "truth",
  "profiles": ["postgres-18"],
  "upstream": {
    "commit": "3c58109e7ab69772de75e640852935ee7e284177",
    "symbol": "IsNull.accept",
    "path": "jOOQ/src/main/java/org/jooq/impl/IsNull.java"
  },
  "construction": "users-age-is-null-id",
  "parameters": [],
  "result": [{"ordinal": 0, "alias": "Id", "sqlType": "int64", "nullable": false, "nested": null}],
  "expectedSql": {"postgres-18": "SELECT \"u\".\"id\" AS \"Id\" FROM \"users\" AS \"u\" WHERE \"u\".\"age\" IS NULL ORDER BY \"u\".\"id\" ASC"},
  "expectedRows": [[{"kind": "int64", "value": "3"}]],
  "expectedDiagnostic": null,
  "difference": null
}
```

`eng/orm-oracle/dependencies.lock.json` records coordinates, canonical Maven Central
URL and SHA256. Fixed initial coordinates/checksums are:

| Coordinates | SHA256 |
| --- | --- |
| org.jooq:jooq:3.21.10 | e02139e3f7538b969fccc0173650462b16bf60d909732a42b6f45f48f31a90cd |
| org.reactivestreams:reactive-streams:1.0.4 | f75ca597789b3dac58f61857b9ac2e1034a68fa672db35055a8fb4509e325f28 |
| io.r2dbc:r2dbc-spi:1.0.0.RELEASE | a5846c59fea336431a4ae72ca14edbf5299b78486fa308eafb383f4ae0ea74e5 |

Derive URLs mechanically as `https://repo.maven.apache.org/maven2/` plus group
segments/artifact/version/artifact-version.jar. Regeneration checks bytes against
this lock before loading; no floating version or opaque cached jar is accepted.

## Mandatory first corpus

| ID group | Exact inputs and expected behavior |
| --- | --- |
| ORACLE-TRUTH-01..21 | Nine AND, nine OR and three NOT truth values including UNKNOWN |
| ORACLE-NULL-01..04 | Age=NULL returns none; IS NULL returns3; row(NULL,1) IS NULL=false, IS NOT NULL=false |
| ORACLE-LIST-01..04 | IN []/1/3 entries and NOT IN(1,NULL); exact occurrence order and UNKNOWN filtering |
| ORACLE-SCOPE-01..04 | Same table two aliases, illegal unbound alias, nonlateral sibling capture, legal correlated EXISTS |
| ORACLE-SET-01..04 | A UNION(B EXCEPT C), local versus outer LIMIT, duplicate-preserving UNION ALL, incompatible degree |
| ORACLE-CTE-01..03 | Numbers1/2/3 recursion; ordinary self-reference and forward-reference rejection |
| ORACLE-WINDOW-01..04 | ROW_NUMBER partitioned by department, ROWS preceding1/current, invalid RANGE order, unsupported QUALIFY |
| ORACLE-DML-01..05 | Row-major INSERT, rollback, profile-native RETURNING, explicit unsupported RETURNING, conflicting UPDATE assignments |
| ORACLE-AGG-01..04 | COUNT(empty)=0; SUM(empty)=NULL; integer SUM declared decimal conversion; SQLite exact-decimal AVG rejection |
| ORACLE-TYPES-01..05 | Typed NULL, JSON null versus SQL NULL, native PG array sequence, range empty/unbounded, decimal overflow |
| ORACLE-NESTED-01..06 | Absent child versus present all-null child; ordered and bag collections; empty []; duplicate retention; Maria budget guard |
| ORACLE-PARAM-01..04 | Same slot repeated, same label distinct slots, quoted user value, lowerer-introduced repeated occurrence |

Canonical seed: departments `(1,Engineering),(2,Operations)`; users
`(1,Alice,32,1,1),(2,Bob,18,1,1),(3,Carol,NULL,0,2),(4,Dana,44,1,2),
(5,Eve,18,1,NULL)`. Store initialization SQL separately per profile, with identical
logical values and appropriate provider types. Fixtures run in disposable databases;
no existing/user database is inferred from ambient configuration.

## Ordered execution and negative controls

1. Load and validate every case offline with CaseJsonContext. Duplicate IDs, unknown
   profile/key, broken upstream path or missing expected outcome fails the corpus.
2. The explicit Java regeneration runner constructs the pinned jOOQ query for each
   known case, sets dialect and bind mode, and returns SQL plus parameter/type data.
   It cannot rewrite maintained expectations automatically; present a review diff.
3. The Korda native runner constructs the same semantic query and compares the
   declared SQL/layout/result metadata without a driver dependency.
4. Independent provider lanes execute accepted shapes and compare owned values.
   A case unavailable in one profile is an explicit diagnostic cell, not a skip
   renamed success. Optional parser cases are separate from mandatory language cases.
5. Mutate copies of fixtures: swap two parameter occurrences, replace IS NULL by =,
   remove a requested clause, change result alias/order, delete a duplicate row and
   replace present-null by absent. Each mutation must fail the corresponding check.
6. For the empty-reader schema distinction, run a direct-reader oracle that inspects
   metadata even when no row exists. The selected Dapper runtime empty result remains
   successful without Tokenize; do not turn that known difference into a false pass
   or a demand to replace the mature loop.

Commands are `python3 tests/Orm/Conformance/verify.py` for ordinary offline work and
`python3 eng/orm-oracle/regenerate.py --case <id> --profile <profile> --output <scratch-dir>`
for explicit regeneration. The latter requires a user-selected scratch output and
never writes caches/logs/binaries into tracked case directories. Record concise
source-linked conclusions and maintained expectations only. Register orm-oracle;
Integration owns the later actual Korda/database matrix, not this harness task.
