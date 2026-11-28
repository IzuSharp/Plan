# ORM-PARSER — Optional SQL parsing and translation module

Status: `planned_candidate`; product implementation is **not authorized**.
This optional follow-on module does not block the initial DSL/provider release.

## Objective

Implement an explicitly bounded SQL parser that produces the shared typed/query
model, with translation available only where the target renderer supports the
resulting semantics. Ordinary Fluent queries never round-trip through this parser.

## Design and source inputs

Read Design `docs/korda-orm/contracts.md`, `language-model.md`,
`dialects-and-generation.md`, and `upstream-policy.md` at the immutable handoff
revision; consume ORM-C01, ORM-C02, ORM-C03, and ORM-C06. Inspect jOOQ 3.21.10
commit `3c58109e7ab69772de75e640852935ee7e284177`, `ParserImpl` entry points,
token/context methods, `requireProEdition`, and `requireUnsupportedSyntax`.
Commercial-only bodies and undocumented grammar are not available implementation
evidence.

## Start and acceptance dependencies

Start: `ORM-FOUNDATION`. Acceptance: `ORM-QUERY`, `ORM-RELATIONAL`,
`ORM-EXPRESSIONS`, `ORM-DML`, and `ORM-RENDER`. Grammar research, tokenization,
diagnostics, and independently reviewed fixtures can begin against contracts;
final acceptance binds to the real node families and renderer.

## Scope and ownership

Own `src/Orm/Parser/` and matching tests. Shared AST nodes, dialect rules, schema
acquisition, execution, and root module registration have other owners. Parser
dependencies must point toward shared language contracts, never back from the
core DSL. Submit additions through shared owners.

## Implementation requirements

Publish the supported input grammar and source profiles before implementation.
Distinguish syntax acceptance, name/type resolution, and target render support.
Use explicit optional schema metadata; unknown names/types remain unresolved
diagnostics rather than fabricated strong typing. Preserve parameter occurrence
order, quoted identifiers, operator precedence, NULL semantics, and source spans.
Bound input size/depth and fail on unsupported clauses; do not ignore syntax to
claim successful translation. No runtime IL generation or arbitrary reflection
is permitted.

## Validation and acceptance

Test token/grammar positive and negative fixtures, comments and escaped quotes,
nested queries, malformed/deep inputs, ambiguous identifiers, parameter count/type
mismatches, and unsupported/commercial-only paths. Compare eligible queries with
the fixed Java reference, then verify semantic round trips rather than textual
identity. Publish and run a driver-free Native AOT consumer. Real-database cases
belong to independent target integration lanes. Profile bounded adversarial
parsing workloads for linearity/resource limits, not headline benchmark claims.

## Integration and stop

Deliver a precise supported-grammar inventory and documented unsupported cases.
Keep parser installation optional. Stop at the reviewed task PR; do not create a
universal translator claim, execute supplied SQL, implement migrations, merge,
publish, or block unrelated DSL/provider acceptance.
