# ORM-RENDER — implement the fixed pure renderer and atomic template protocol

Status: `planned_candidate`; product implementation is not authorized.

## Inputs, scope and dependency gate

Use contracts v0.2.0 and implementation-spec sections 3–6 at the immutable Design
commit in implementation-graph.json. Read jOOQ 3.21.10 commit
`3c58109e7ab69772de75e640852935ee7e284177`: DefaultRenderContext.visit0/scopeEnd0,
DefaultVisitContext, AbstractContext, Val.accept, ParamCollector.bindInternal,
SelectQueryImpl and SortFieldImpl. Port traversal, scope and occurrence semantics;
do not reuse a name dictionary as a substitute for ordered binding.

Start after Foundation. Accept the common pipeline against actual Types, shared
nodes and deterministic IDialectRules fakes. Actual four-dialect SQL acceptance
belongs to each dialect and Integration; a fake rules object cannot accept those
leaves. Foundation creates all project interfaces so these workers can compile in
parallel. Own `src/Orm/Rendering/` and `tests/Orm/Rendering/`; the common rules and
writer interfaces are Contracts-owned. Do not edit provider or dialect folders.

| File | Exact responsibility |
| --- | --- |
| SqlRenderer.cs | Query<T>, ReturningMutation<T> and Mutation Render/RenderAndBind overloads from the specification |
| RenderContext.cs | One StringBuilder, final occurrence/result builders, immutable profile, scope stack and precedence state per invocation |
| CoreSqlWriter.cs | Exhaustive shared NodeKind switch; dialect callback for specialized grammar; no ToString fallback |
| ScopeFrame.cs | RelationId/CTE bindings, parent capture policy, emitted names and projection alias context |
| SemanticValidation.cs | Ordered model/scope/grouping/type passes; aggregate contextual errors before emission |
| Capability.cs | Native/Lowered/Unsupported result with rule ID and checked preconditions |
| TemplateFingerprint.cs | Canonical binary encoding and SHA-256 algorithm below |
| TemplateBindingExtensions.cs | Frozen values, exact list cardinality and descriptor validation; creates a fresh invocation state |
| Tests | GoldenSqlTests, OccurrenceTests, ScopeTests, FingerprintTests, InvocationValueTests, ConcurrentRenderTests, NativeConsumer |

## Exact internal seams and call order

Contracts declares internal `IDialectRules.Lower(SqlNode,SqlProfile):SqlNode` and
`Write(SqlNode,ISqlWriter,int):void`. ISqlWriter exposes `SqlProfile Profile {get;}`,
`void Write(string)`, `void Visit(SqlNode,int parentPrecedence=0)`,
`void VisitCore(SqlNode,int parentPrecedence=0)`, `string Quote(SqlName)` and
`string NextParameter(SlotId,int elementIndex,SqlTypeDescriptor)`. Each Profile.Create attaches its immutable static rules to SqlProfile.Rules.
Rendering references only Contracts/Types/Language and calls that interface;
concrete dialects never reference Rendering. A metadata-only profile without Rules
is valid for SqlTemplates.Declare but Fluent Render fails KORM-DIALECT-001. Each
rules instance validates its family and fixed rules_version=0.2.0 setting.

1. Reject null/default collections, unknown tags, descriptor inconsistencies and
   malformed identifiers. Snapshot-owned collections are already frozen; do not
   copy them on every visited expression.
2. Validate lexical relation/CTE scopes, projection degree/aliases, grouping and
   function context. Alias equality in the common pass is Ordinal; each profile
   additionally rejects collisions under its actual quoted-identifier rules.
3. Invoke the profile's checked Lower. That implementation calls pure
   NestedLowering(root,profile) before its own dialect transform. Neither lowerer
   receives request values, a connection or a RenderContext.
4. Revalidate the lowered graph. Keep an immutable rule-ID list as template
   metadata for diagnostics; a missing or failed precondition produces no template.
5. Create RenderContext and traverse once for SQL, parameter occurrences and final
   physical result columns. Parameter order is the SQL text's final order, including
   repeated expressions introduced by a supported lowering.
6. Check profile limits, compute the canonical fingerprint, freeze SQL/layout/result
   arrays, copy profile metadata with Rules cleared and publish the template atomically. Any failure discards local builders.
7. RenderAndBind merges query captures and explicit values, snapshots each mutable
   value once, derives ListParam arities, calls Render and Bind. Bind on a reusable
   template does not visit the AST, regenerate SQL or enumerate a caller list again.

Visit delegates to rules.Write. A dialect override writes a special node or calls
VisitCore; VisitCore does not call that same override again. Its recursive children
use Visit. This avoids infinite callback recursion while preserving nested dialect
behavior. Common acceptance tests inject fixed rules through an internal test seam;
that seam is not a public plugin/reflection loader.

## Emission rules fixed before implementation

Precedence levels increase with binding strength: OR=10, AND=20, NOT=30,
comparisons/IS/IN/BETWEEN=40, concatenate=50, add/subtract=60, multiply/divide=70,
unary=80, atom/function=100. Parenthesize lower precedence; at equal precedence
parenthesize the right child of subtraction/division and mixed set operators.
Always preserve explicit child set grouping/local ORDER/LIMIT. Do not rely on
operator text to reconstruct precedence after emission.

Quote identifier segments separately, doubling the profile's quote character.
One segment `a.b` remains one identifier; it does not become two segments. Explicit
Literal (including explicit LimitLiteral) uses the profile's invariant literal encoder. Ordinary captured values
never reach that encoder. NULL equality is not rewritten; empty IN/NOT IN become
FALSE/TRUE. LIMIT and OFFSET accept Int32 public values, capture typed Int32 slots,
and emit in each profile's prescribed clause order. Hidden sentinel literals for
unsupported offset-only syntax are structural and included in the fingerprint.

NextParameter uses ordinal=occurrences.Count. PostgreSQL placeholder is `$` plus
ordinal+1 and Name is empty; other profiles use `@p` plus ordinal and Name `p` plus
ordinal. Append a new ParameterOccurrence every time, even for the same SlotId.
ElementIndex is -1 for scalar and the zero-based element for an expanded list.
Validate final physical count, not distinct logical slots, against max_parameters.
The same slot's descriptor must agree everywhere; equal user labels do not merge
slots. An unused value in a known superset is ignored; a missing used slot fails.

Fingerprint bytes use format version 1, little-endian fixed integers, UTF-8 strings
prefixed by a UInt32 byte count, and explicit null markers. Encode NodeKind and
ordered children, SQL type IDs/CLR assembly-qualified stable names/nullability/
facets/conversion IDs, literal value bytes, profile family/version/settings sorted
Ordinal, list cardinalities, result/nested shape and capability rule IDs. Renumber
relation/slot identities in first structural visit order; never hash process-local
IDs. Encode floating literals by IEEE bits, decimals by decimal.GetBits and strings
by UTF-8; preserve negative zero. Hash with SHA256 and lowercase hexadecimal.
Bound request values are excluded. A matching fingerprint does not permit binding
slots from another query instance: template.Parameters retain their real SlotIds.
There is no global cache, command preparation or pool in this task.

## Required cases and exact outcomes

| ID | Input | Expected |
| --- | --- | --- |
| RENDER-01 | PG select u.Id alias Id, predicate u.Id=slot1, ordered Id | `SELECT "u"."id" AS "Id" FROM "users" AS "u" WHERE "u"."id" = $1 ORDER BY "u"."id" ASC`; one ordinal0 occurrence |
| RENDER-02 | Same logical slot in two comparisons | Two placeholders/occurrences, both same SlotId; no dictionary deduplication |
| RENDER-03 | Two slots both labelled id bound to 1/2 | Separate physical parameters, values 1/2 |
| RENDER-04 | IS NULL versus = nullable slot | No occurrence versus one typed nullable occurrence |
| RENDER-05 | IN arity0/1/3 | FALSE / one / three occurrences; bind arity2 into arity3 fails KORM-BIND-003 |
| RENDER-06 | Lowering duplicates one parameter expression | Both final occurrences emitted in textual order |
| RENDER-07 | a-(b-c) | Required right parentheses preserved |
| RENDER-08 | Nonlateral sibling reference | KORM-SCOPE-001, no partial template |
| RENDER-09 | Segment a.b and embedded quote | Quoted as one segment with doubled quote |
| RENDER-10 | Render same shape with different values; Literal1 vs Literal2 | Same fingerprint for values; different fingerprint for literals |
| RENDER-11 | Change profile/facets/list arity/result order | Different fingerprints |
| RENDER-12 | Bind command twice from one template | Two independent unused invocation states; template remains value-free |
| RENDER-13 | Parallel render calls on one query | Byte-identical SQL/layout/fingerprint, no shared mutable builder |
| RENDER-14 | Final count exceeds profile limit by one | Explicit KORM-DIALECT diagnostic before template publication |
| RENDER-15 | Unknown node or unsupported lowerer | Deterministic diagnostic, no raw ToString SQL |

Run `python3 tests/Orm/Rendering/verify.py`; publish and execute the pure native
consumer, with no execution/provider/generator dependency. Register orm-render and
its actual project references in the existing module registry. Allocation probes
separate new rendering from explicit template reuse; they do not assert zero GC.
Stop after the common renderer gate; four database behavior lanes remain separate.
