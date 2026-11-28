# ORM-EXPRESSIONS: Port the fixed expression and SQL truth algorithms

Status: `planned_candidate`; product implementation remains unauthorized.

Use the immutable Design commit in `../implementation-graph.json`, contracts v0.2.0,
and `docs/korda-orm/implementation-spec.md`. The packet fixes implementation work;
contradictions return to the contract owner before changing an interface or policy.

## Gate, source and owned files

Start after Foundation; accept against actual Types. Own
`src/Orm/Language/Expressions/` and `tests/Orm/Expressions/`; consume shared node
contracts. Inputs ORM-C01/C02/C03/C06, implementation-spec and jOOQ commit
`3c58109e7ab69772de75e640852935ee7e284177`.

| File | Source symbols and concrete operation set |
| --- | --- |
| `FieldOperations.cs` | `Eq`, `Ne`, `Gt`, `Ge`, `Lt`, `Le`, `IsDistinctFrom`: typed value/Param/Field overloads |
| `ConditionOperations.cs` | `And`, `Or`, `Not`, `TrueCondition`, `FalseCondition`, `NullCondition` |
| `Membership.cs` | `InList`, `NotInList`, `In`, `Between`: scalar/list/subquery membership |
| `Rows.cs` | `RowImpl1..8`, `RowIsNull`, row comparison and degree validation |
| `NumericFields.cs`, `TextFields.cs` | arithmetic, ABS, COALESCE, NULLIF, LIKE with explicit escape, concatenation, lower/upper/length |
| `Aggregates.cs`, `CaseExpressions.cs` | COUNT/SUM/MIN/MAX/AVG, searched/simple CASE; typed nodes with explicit nullability |
| `ExpressionValidator.cs` | context/type/degree/volatility preconditions consumed by Rendering |

## Fixed type and truth rules

Comparisons require the same generic carrier or an explicit Cast; equal CLR carriers
with different SQL domains still require a declared conversion. Numeric overloads
are concrete for short/int/long/float/double/decimal and nullable counterparts;
there is no `object` catch-all. COUNT returns nonnull Int64. SUM(short/int/long)
returns Field<decimal?>, including nullable inputs; preserve native SUM and use a
closed checked result conversion from the provider native bigint/numeric/decimal
representation. SUM(decimal) returns decimal? and SUM(float/double) returns double?.
AVG(short/int/long/decimal) returns decimal?; AVG(float/double) returns double?.
SQLite rejects exact-decimal SUM/AVG and exact integer AVG with KORM-TYPE-004;
callers wanting approximation explicitly cast the operand to Double. Integer SUM
on SQLite is allowed: its native Int64 result converts exactly to decimal, and
server integer overflow remains an error. PG/MySQL/Maria numeric results outside
CLR decimal range fail KORM-TYPE-005 with the original overflow cause. Never CAST
AS SIGNED, clamp, truncate a fractional result or infer a result type from one row.
Use conversion IDs aggregate.int-sum.decimal, aggregate.decimal-sum.decimal,
aggregate.numeric-avg.decimal and aggregate.floating.double for those respective
result families; ordinary decimal column codecs must not widen their accepted
storage representations to implement aggregates. MIN/MAX preserve the operand SQL type with nullable output. This complete overload
and codec policy replaces the earlier unspecified 'safe range' decision.

NULL equality is a CompareNode with a NULL-valued parameter and retains UNKNOWN.
It is never rewritten to IsNull. IsNull and null-safe distinctness are separate
nodes. Boolean operations retain SQL UNKNOWN; C# bool short-circuiting does not
implement SQL conditions. The initial simplifier folds only pure literal truth
nodes and never removes/duplicates a volatile expression.

## Mechanical public overload surface

All methods below belong to the existing Language assembly in namespace Korda.Orm.
FieldOperations and ConditionOperations keep their existing names; helper files
may contain internal implementation classes. Public Sql facade fragments are
partial only in this one assembly. Foundation owns the data handles/records in
Contracts. The mechanical patterns below are a finite generation specification,
not open-ended runtime generic dispatch or a choice for the implementer.

### Comparison, membership, cast and nullability

For each name in `Eq, Ne, Lt, Le, Gt, Ge, IsDistinctFrom, IsNotDistinctFrom`, emit
the following three FieldOperations overloads, substituting only the method name:

```csharp
public static Condition Eq<T>(this Field<T> left, T right);
public static Condition Eq<T>(this Field<T> left, Param<T> right);
public static Condition Eq<T>(this Field<T> left, Field<T> right);
public static Condition IsNull<T>(this Field<T> value);
public static Condition IsNotNull<T>(this Field<T> value);
public static Condition In<T>(this Field<T> value, IEnumerable<T> values);
public static Condition In<T>(this Field<T> value, ListParam<T> values);
public static Condition In<T>(this Field<T> value, Query<T> values);
public static Condition NotIn<T>(this Field<T> value, IEnumerable<T> values);
public static Condition NotIn<T>(this Field<T> value, ListParam<T> values);
public static Condition NotIn<T>(this Field<T> value, Query<T> values);
public static Field<TTarget> Cast<TSource,TTarget>(this Field<TSource> value,
    SqlType<TTarget> target);
public static Field<T?> Nullable<T>(this Field<T> value) where T : struct;
public static Field<T?> NullableReference<T>(this Field<T> value) where T : class;
```

Subquery membership requires the same one-Scalar-member carrier check as Scalar;
one-column DTO/Row carriers are rejected with KORM-QUERY-002. Reference annotations
alone are not overload identities. Nullable/NullableReference are explicit metadata
lifts: they preserve SQL identity/facets/conversion ID and emit the child unchanged,
but set the result descriptor/carrier to the nullable counterpart. They never add
COALESCE or a SQL cast. Cast is an explicit registered SQL conversion; a nullable
input cannot be cast to a NonNull result descriptor. Casting has no authority to
remove nulls or to reinterpret a domain as its base identity implicitly.

An explicit Cast whose target is built-in int16/short (or short?) attaches
`cast.int16.checked`; target int32/int (or int?) attaches `cast.int32.checked`.
The IDs are identical across profiles and are copied into ResultColumn.ConversionId.
PostgreSQL emits SMALLINT/INTEGER and uses its matching native short/int getter.
SQLite emits INTEGER; MySQL/Maria emit SIGNED; those profiles read native Int64
and perform checked narrowing only in these named converters. A NULL result follows
the target nullability; required NULL is KORM-MAP-003. Overflow in the converter is
KORM-TYPE-005, preserving the cause; unknown ID/wrong closed result carrier or
unsupported physical representation is KORM-MAP-002. No converter trusts a cast ID
to accept unrelated TEXT/REAL or an arbitrary SQL domain. An ordinary int32 column
does not gain permissive Int64 reading. Native SQL cast errors remain server errors.
Int64/Float64 widening casts have null ConversionId. Explicit decimal casts require
declared precision/scale when their SQL spelling requires it; the no-p/s arithmetic
result descriptor is not a default lossy DECIMAL cast request.

For each of Between and NotBetween, emit exactly nine overloads: receiver Field<T>,
lower and upper independently selected from `T`, `Param<T>`, `Field<T>`. All return
Condition. For example:

```csharp
public static Condition Between<T>(this Field<T> value, T lower, T upper);
public static Condition Between<T>(this Field<T> value, Param<T> lower, Field<T> upper);
public static Condition NotBetween<T>(this Field<T> value, Field<T> lower, Param<T> upper);
```

Capture ordinary operands independently using the receiver's SQL type. Both bounds
must have compatible identity/facets/nullability. Store one BetweenNode with
Negated=false/true and emit native inclusive BETWEEN/NOT BETWEEN; do not lower it
into two visits to the left operand. SYMMETRIC and implicit bound reordering are
not initial operations. Unknown comparison/type categories fail KORM-TYPE-004;
same CLR type alone is not proof that JSON/array/domain values are orderable.

### Numeric promotion and concrete overload generation

| Input carrier N | Promoted carrier P | SQL result identity |
| --- | --- | --- |
| short | long | int64 |
| int | long | int64 |
| long | long | int64 |
| float | double | float64 |
| double | double | float64 |
| decimal | decimal | decimal, no Precision/Scale facets on the arithmetic result |

In NumericFields, generate Add/Subtract/Multiply for all six rows. For each name
and N, generate the four operand nullability pairs `(N,N)`, `(N?,N)`, `(N,N?)`,
`(N?,N?)`; the receiver is Field of the first carrier and the right operand has
three forms: value, Param, Field of the second carrier. Return Field<P> for the
first pair and Field<P?> for the other three. Thus each name has exactly 72
overloads (six carriers × four pairs × three RHS forms). These examples are
literal declarations from that mechanical set:

```csharp
public static Field<long> Add(this Field<int> left, int right);
public static Field<long> Add(this Field<int> left, Param<int> right);
public static Field<long> Add(this Field<int> left, Field<int> right);
public static Field<long?> Add(this Field<int?> left, int right);
public static Field<long?> Add(this Field<int> left, Param<int?> right);
public static Field<long?> Add(this Field<int?> left, Field<int?> right);
public static Field<double> Multiply(this Field<float> left, Field<float> right);
public static Field<decimal?> Subtract(this Field<decimal?> left, decimal right);
```

Generate Negate/Abs for Field<N>→Field<P> and Field<N?>→Field<P?>, twelve overloads
per name. Generate IntegerDivide/Modulo only for short/int/long, with the same
four operand pairs and three RHS forms, always Field<long?>: 36 overloads per name.
Generate Divide only for float/double/decimal with those pairs/forms, always
Field<P?>: 36 overloads. There is no integer Divide that accidentally produces a
fraction, no floating remainder, no UInt64 arithmetic, and no mixed-N overload.
Callers explicitly Cast to choose a common input carrier before an operation.
The generated nullable operand pairs compare SQL identity/facets while deliberately
ignoring their differing nullability; result nullability follows the table above.

Before binary/unary integer operations, construct explicit Int64 operand casts;
before floating operations construct Float64 operand casts. Do this even when a
small physical column might otherwise cause PostgreSQL to use a narrower operator.
Use BIGINT/DOUBLE PRECISION in PostgreSQL, INTEGER/REAL in SQLite, and
SIGNED/DOUBLE in MySQL/MariaDB. Decimal operands remain decimal and have compatible
input facets, while the output descriptor deliberately has no inferred p/s: an
implementation must not inherit the input scale for multiplication or guess an
engine-specific result precision. Output precision/range is checked by the existing
closed decimal reader; no blanket Convert.ChangeType or arithmetic result narrowing
is introduced. Unknown-facet decimal results are not themselves a request to emit
`CAST AS DECIMAL` with the server's lossy default precision/scale.

Add/Subtract/Multiply/Negate use native operators; Abs uses native ABS. IntegerDivide
emits `/` on PG/SQLite and `DIV` on MySQL/Maria; Modulo emits `%`. Floating/decimal
Divide emits `/`. A zero divisor preserves the server's own error/NULL behavior;
the nullable result type permits NULL but does not guarantee the server avoids an
error. Never inject NULLIF. Integer overflow is a server error where native; a
SQLite overflow may produce REAL, which the strict per-row INTEGER reader rejects
with KORM-MAP-002 instead of truncating with GetInt64. Results that reach a known
closed conversion but exceed its range fail KORM-TYPE-005; a required DBNull alone
fails KORM-MAP-003. Nonfinite floating policy is the selected type/provider's policy.

SQLite exact-decimal arithmetic remains KORM-TYPE-004 because decimal transport is
TEXT. This is a deliberate C# result-carrier adaptation of jOOQ's arithmetic nodes:
the native operand/result categories must align with fixed AOT reader delegates.
Do not describe the promotion as jOOQ's unchanged same-input-type API. ArithmeticNode
stores the final ResultType and ConversionId explicitly; ordinary promoted numeric
operations use null ConversionId and the existing Int64/Double/Decimal reader.

### Text, null helpers and aggregates

In TextFields, emit these nonnullable declarations. Like/NotLike and Concat each
have three right-operand forms, substituting string, Param<string>, Field<string>:

```csharp
public static Condition Like(this Field<string> value, string pattern, char escape);
public static Condition NotLike(this Field<string> value, string pattern, char escape);
public static Field<string> Concat(this Field<string> left, string right);
public static Field<string> Lower(this Field<string> value);
public static Field<string> Upper(this Field<string> value);
public static Field<long> Length(this Field<string> value);
```

Generate a second explicitly named set LikeNullable/NotLikeNullable/ConcatNullable/
LowerNullable/UpperNullable/LengthNullable, using Field<string?> receivers and
string?/Param<string?>/Field<string?> operands; returns are Condition, Field<string?>
and Field<long?> respectively. These distinct names avoid illegal overloads that
differ only by reference nullability and avoid warnings in typed DTO projection
helpers. Use NullableReference() to lift a nonnullable field when mixing operands.
The nonnullable methods require NonNull SQL descriptors. Nullable methods preserve
a nullable result descriptor even if a caller supplied a conservatively lifted value.

Escape is one non-NUL, nonsurrogate UTF-16 character, encoded as one quoted SQL
character literal and included in the fingerprint. Pattern/value inputs remain
parameters. LIKE uses the database's declared collation/case behavior. Concat emits
`||` on PG/SQLite and `CONCAT(left,right)` on MySQL/Maria, preserving NULL if either
operand is NULL; it never depends on PIPES_AS_CONCAT. Lower/Upper use native functions
and do not promise a portable Unicode case-fold algorithm. Length means native
character length: CHAR_LENGTH on PG/MySQL/Maria, LENGTH on SQLite, explicitly cast
to the profile's signed Int64 representation. In particular, SQLite's native TEXT
length stops at embedded NUL; this function is not the input facet's Rune-count
validator. Profile fixtures state that difference instead of silently removing NUL.

```csharp
// Sql facade: all inputs have one common declared SQL identity/facet set
public static Field<T> Coalesce<T>(params Field<T>[] values);
// FieldOperations: nonnull fallback gives a nonnullable value result
public static Field<T> Coalesce<T>(this Field<T?> value, Field<T> fallback) where T : struct;
public static Field<T> CoalesceReference<T>(this Field<T?> value, Field<T> fallback) where T : class;
// Each fallback also has T and Param<T> forms.
public static Field<T?> NullIf<T>(this Field<T> value, Field<T> other) where T : struct;
public static Field<T?> NullIf<T>(this Field<T?> value, Field<T?> other) where T : struct;
public static Field<T?> NullIfReference<T>(this Field<T> value, Field<T> other) where T : class?;
// Each NullIf RHS also has the corresponding value and Param forms.

// Sql facade: count and ordered aggregates
public static Field<long> Count();
public static Field<long> Count<T>(Field<T> value);
public static Field<long> CountDistinct<T>(Field<T> value);
public static Field<T?> Min<T>(Field<T> value) where T : struct;
public static Field<T?> Min<T>(Field<T?> value) where T : struct;
public static Field<T?> Max<T>(Field<T> value) where T : struct;
public static Field<T?> Max<T>(Field<T?> value) where T : struct;
public static Field<T?> MinReference<T>(Field<T> value) where T : class?;
public static Field<T?> MaxReference<T>(Field<T> value) where T : class?;
```

Sql.Coalesce requires at least two fields. Its result keeps T; nullable value-carrier
T remains SQL Nullable. For reference T, mark NonNull only when some argument is
declared NonNull; otherwise Nullable. The dedicated fallback overloads require a
NonNull fallback descriptor and return its nonnullable carrier/descriptor. NULLIF
uses native equality and always returns a nullable copy of the left SQL type; a
NULL comparison is not converted to null-safe distinctness. Native COALESCE/NULLIF
preserve the engine's evaluation rules; no repeated-expression CASE expansion.

For each N in short/int/long/decimal/float/double, emit `Sql.Sum(Field<N>)`,
`Sql.Sum(Field<N?>)`, `Sql.Avg(Field<N>)`, `Sql.Avg(Field<N?>)` with exactly the
result types/conversion IDs in the fixed type table above (24 methods total).
MIN/MAX require a registered orderable SQL identity. COUNT(*) has no argument,
COUNT(field) ignores NULL, and COUNT DISTINCT has one argument and Distinct=true;
there is no untyped multi-column aggregate argument list. All aggregate nodes
store their final result descriptor/conversion ID and an aggregate-context flag.

### Searched/simple CASE and row expressions

Contracts owns immutable CaseBuilder<TResult>, SimpleCaseBuilder<TValue,TResult>
and RowExpression<T1,...,TN> handles (N=1..8), each with an internal node/captures
constructor. These are SQL construction handles; RowExpression is not IField and
does not pretend to be a provider composite scalar. Row<T1,...,TN> remains the
existing result/value record family. Public CASE methods are:

```csharp
// Sql facade
public static CaseBuilder<T> Case<T>(SqlType<T> resultType);
public static SimpleCaseBuilder<TValue,TResult> Case<TValue,TResult>(
    Field<TValue> value, SqlType<TResult> resultType);
// CaseOperations; each result operand also has TResult / Param<TResult> forms
public static CaseBuilder<T> When<T>(this CaseBuilder<T> c, Condition condition, Field<T> result);
public static Field<T> Else<T>(this CaseBuilder<T> c, Field<T> result);
public static SimpleCaseBuilder<TValue,TResult> When<TValue,TResult>(
    this SimpleCaseBuilder<TValue,TResult> c, Field<TValue> match, Field<TResult> result);
public static Field<TResult> Else<TValue,TResult>(
    this SimpleCaseBuilder<TValue,TResult> c, Field<TResult> result);
public static Field<T?> End<T>(this CaseBuilder<T> c) where T : struct;
public static Field<T?> End<T>(this CaseBuilder<T?> c) where T : struct;
public static Field<T?> EndReference<T>(this CaseBuilder<T> c) where T : class?;
public static Field<TResult?> End<TValue,TResult>(
    this SimpleCaseBuilder<TValue,TResult> c) where TResult : struct;
public static Field<TResult?> End<TValue,TResult>(
    this SimpleCaseBuilder<TValue,TResult?> c) where TResult : struct;
public static Field<TResult?> EndReference<TValue,TResult>(
    this SimpleCaseBuilder<TValue,TResult> c) where TResult : class?;
```

For simple CASE When, independently choose the match from TValue/Param<TValue>/
Field<TValue> and result from TResult/Param<TResult>/Field<TResult>: exactly nine
overloads. Searched When has three result forms; each Else has three result forms.
When appends in declaration order. Else/End require at least one branch and return
a Field, closing the builder. Validate branch identity/facets against the explicit
resultType; use the explicit nullable field lifts when a nullable result was chosen.
Else preserves that result type; End creates the nullable counterpart and omits
ELSE in SQL. Simple CASE stores the base expression once; matching NULL retains
ordinary SQL equality/UNKNOWN and is not rewritten to IS NULL. Do not infer a
common numeric type from runtime branch values.

For each arity N=1..8 generate `Sql.Row<T1,...,TN>(Field<T1> f1,...,Field<TN> fN)`
returning RowExpression<T1,...,TN>. In RowOperations generate Eq/Ne/Lt/Le/Gt/Ge
with the same-arity RowExpression RHS and with Row<T1,...,TN> RHS, returning
Condition. The value overload captures one typed value per component in left-to-
right order. IsNull/IsNotNull take only the row receiver. In/NotIn take a matching
Query<Row<T1,...,TN>> for N=2..8; for N=1 the query parameter is Query<T1>, matching
the single-field Select contract. Require flat Scalar members of matching component
types; nested/DTO carriers are not reflected into SQL row components. Example:

```csharp
public static RowExpression<T1,T2> Row<T1,T2>(Field<T1> first, Field<T2> second);
public static Condition Eq<T1,T2>(this RowExpression<T1,T2> left, RowExpression<T1,T2> right);
public static Condition Eq<T1,T2>(this RowExpression<T1,T2> left, Row<T1,T2> right);
public static Condition In<T1,T2>(this RowExpression<T1,T2> left, Query<Row<T1,T2>> right);
public static Condition IsNull<T1,T2>(this RowExpression<T1,T2> row);
public static Condition IsNotNull<T1,T2>(this RowExpression<T1,T2> row);
```

For N>=2 emit native row constructors/comparisons and row-subquery IN on the four
profiles; for N=1 emit the scalar operation without a one-element SQL tuple. Row
IS NULL is the ordered conjunction of component IS NULL; row IS NOT NULL is the
conjunction of component IS NOT NULL. Each component occurs once in either form.
Do not lower lexicographic comparisons to a repeated-prefix OR tree, which would
change volatile evaluation/parameter occurrences. Row-list parameters, row scalar
projection, row ordering distinctness and componentwise implicit widening have no
public operation in this baseline.

## Exact expression data records

These complete the compact node names in Design. They are shared Contracts data;
Captured values stay solely in public handles. All nullable optional fields have
the stated invariant, and every array is copied before storage.

```csharp
public enum ComparisonKind { Eq, Ne, Lt, Le, Gt, Ge, IsDistinctFrom, IsNotDistinctFrom }
public enum BooleanKind { And, Or }
public enum ArithmeticKind { Add, Subtract, Multiply, Negate, Abs, IntegerDivide, Divide, Modulo }
public enum CaseKind { Searched, Simple }
internal enum FunctionId {
    Count, Sum, Min, Max, Avg, Coalesce, NullIf, Concat, Lower, Upper, Length,
    RowNumber, Rank, DenseRank
}
internal sealed record BetweenNode(SqlNode Value, SqlNode Lower, SqlNode Upper,
    bool Negated) : SqlNode(NodeKind.Between);
internal sealed record ArithmeticNode(ArithmeticKind Operation, SqlNode Left,
    SqlNode? Right, SqlTypeDescriptor ResultType, string? ConversionId)
    : SqlNode(NodeKind.Arithmetic);
internal sealed record FunctionNode(FunctionId Function, ImmutableArray<SqlNode> Arguments,
    SqlTypeDescriptor ResultType, string? ConversionId, bool Distinct)
    : SqlNode(NodeKind.Function);
internal sealed record CastNode(SqlNode Value, SqlTypeDescriptor ResultType,
    string? ConversionId) : SqlNode(NodeKind.Cast);
internal sealed record NullabilityNode(SqlNode Value, SqlTypeDescriptor ResultType,
    string? ConversionId) : SqlNode(NodeKind.Nullability);
internal sealed record CaseBranchNode(SqlNode Test, SqlNode Result);
internal sealed record CaseNode(CaseKind CaseKind, SqlNode? Operand,
    ImmutableArray<CaseBranchNode> Branches, SqlNode? Else,
    SqlTypeDescriptor ResultType, string? ConversionId) : SqlNode(NodeKind.Case);
internal sealed record LikeNode(SqlNode Value, SqlNode Pattern, char Escape,
    bool Negated) : SqlNode(NodeKind.Like);
internal sealed record RowValueNode(ImmutableArray<SqlNode> Items,
    ImmutableArray<SqlTypeDescriptor> Types) : SqlNode(NodeKind.RowValue);
internal sealed record RowCompareNode(ComparisonKind Comparison,
    RowValueNode Left, RowValueNode Right) : SqlNode(NodeKind.RowCompare);
internal sealed record RowNullTestNode(RowValueNode Row, bool Negated)
    : SqlNode(NodeKind.RowNullTest);
internal sealed record RowInNode(RowValueNode Row, QueryNode Query, bool Negated)
    : SqlNode(NodeKind.RowIn);
```

Arithmetic Right is null only for Negate/Abs. Case Operand is null only for Searched;
its tests are conditions. Simple stores one operand and typed match tests. A row
has 1..8 Items and equally many Types. RowCompare accepts only Eq/Ne/Lt/Le/Gt/Ge.
FunctionId's initial closed built-ins are Count, Sum, Min, Max, Avg, Coalesce,
NullIf, Concat, Lower, Upper, Length, RowNumber, Rank, DenseRank; Count's empty
Arguments means `*`, Distinct is allowed only for one-argument Count. Function
metadata maps each fixed ID to arity, scalar/aggregate/window context and intrinsic
volatility; children contribute their volatility. The built-in function catalog is
closed in this version. An unknown parser function is rejected, and caller-written
SQL uses the separate declared-SQL entry; no arbitrary raw-function AST factory or
runtime function registration is left for an implementer to invent.

The common result descriptor reader takes ResultType/ConversionId from the final
expression node or explicit field ascription; it never derives a reader codec by
examining the first value. Alias, scalar-subquery and Over wrappers preserve an
underlying conversion ID. Case/Coalesce do not erase nonidentity reader conversions:
all result branches must share one compatible conversion ID, otherwise require an
explicit cast to a common native representation or fail KORM-TYPE-003. This keeps
SQLite integer-SUM decimal conversion distinct from ordinary decimal TEXT.

## Ordered implementation

1. Field operations capture ordinary T values in fresh typed slots and produce
   nodes; Param<T> operands reference their existing slot without capturing values.
   Field<T> operands preserve their relation and SQL type metadata.
2. And/Or flatten adjacent nodes of the same kind in source order, freeze children
   and merge captures. Preserve order for parameter occurrence collection. Not does
   not apply unsafe two-valued rewrites to nullable comparisons.
3. Implement SQL three-valued truth tables exactly. TRUE AND UNKNOWN=UNKNOWN;
   FALSE AND UNKNOWN=FALSE; TRUE OR UNKNOWN=TRUE; FALSE OR UNKNOWN=UNKNOWN;
   NOT UNKNOWN=UNKNOWN. Fold only when all relevant terms are pure constants.
4. IN snapshots an enumerable once or records ListParam identity/structural arity.
   Empty IN becomes FALSE and empty NOT IN TRUE. Nonempty lists retain NULL entries;
   NOT IN (1,NULL) is not emulated as a series of inequality tests dropping NULL.
5. Rows preserve degree/component types. `(NULL,1) IS NULL` is FALSE and IS NOT NULL
   is FALSE; NOT(IS NULL) is TRUE. Never implement row IS NOT NULL as NOT(row IS NULL).
   Row comparisons obey lexicographic SQL semantics, with profile-checked lowering.
6. BETWEEN is inclusive and preserves expression evaluation semantics. Do not
   duplicate a volatile left operand into two comparisons unless a profile lowering
   explicitly guarantees single evaluation; otherwise reject that lowering.
7. CASE validates each branch condition/result and one explicit common SQL type.
   Missing ELSE gives nullable result. COALESCE requires declared compatible types;
   nullability is nonnull only when a guaranteed nonnull argument exists.
8. LIKE stores pattern as a typed parameter and escape as a validated single
   character. No C# string.Contains is silently translated using a guessed collation.
9. Function metadata includes deterministic/volatile/context flags. Unknown SQL
   functions are outside the initial AST surface and cannot acquire an automatic
   equivalent-lowering claim. A scalar subquery or other expression whose stable
   evaluation is unproved remains unsafe to duplicate even with this closed catalog.
10. Emit descriptors and nodes only; dialect renderers own grammar/operator spelling.

## Mandatory cases

| ID | Exact case | Expected |
| --- | --- | --- |
| EXP-01 | All 9 AND and all 9 OR truth combinations plus 3 NOT values | SQL truth table above |
| EXP-02 | Age = typed NULL; Age IS NULL on canonical users | No rows versus ID3 |
| EXP-03 | IN [] / NOT IN [] | FALSE / TRUE even for nullable input |
| EXP-04 | 2 NOT IN (1,NULL) | UNKNOWN, filtered out in WHERE |
| EXP-05 | row(NULL,1) null predicates | FALSE / FALSE / TRUE as above |
| EXP-06 | Typed row degree2 vs degree3 | Compile failure where known; otherwise KORM-QUERY-002 |
| EXP-07 | Same named distinct slots and repeated one slot | Identity retained; final occurrence policy belongs to renderer |
| EXP-08 | CASE without ELSE | Nullable result descriptor |
| EXP-09 | Volatile BETWEEN lowering on unsupported profile | Explicit capability failure, no duplicated evaluation |
| EXP-10 | Text value containing quote and wildcard | Remains parameter data; declared LIKE escape behavior only |
| EXP-11 | COUNT(empty)/SUM(empty) | 0 / NULL in later database oracle; descriptor already exact here |
| EXP-12 | int field compared to string | Negative compile diagnostic |
| EXP-13 | Int32 x.Add(1), nullable Int32 x.Add(1), Float32 x.Multiply(2f) | Field<long>, Field<long?>, Field<double>; explicit operand widening nodes and null ConversionId |
| EXP-14 | Int32 x.Add(1L), without an explicit operand Cast | Compile failure; no mixed-carrier overload |
| EXP-15 | IntegerDivide(-7,3); Modulo(-7,3) | -2 and -1 on the four profiles, nullable Int64 descriptors |
| EXP-16 | SELECT integer division by zero | PG native division error; SQLite/MySQL/Maria native NULL (and native warnings where applicable); no NULLIF rewrite |
| EXP-17 | SQLite Int64 maximum plus one | Native REAL representation rejected KORM-MAP-002; no truncated Int64 value |
| EXP-18 | Decimal(p,s) multiplication | Output decimal descriptor has no inherited p/s; SQLite KORM-TYPE-004 |
| EXP-19 | Simple CASE NULL WHEN NULL THEN 1 ELSE 2 | 2; no IS NULL rewrite and one base-expression occurrence |
| EXP-20 | Searched CASE End without Else; zero-branch End | Nullable result; KORM-QUERY-002 respectively |
| EXP-21 | Nullable text ConcatNullable("x") / LengthNullable() | Native NULL propagation and string?/long? carriers; no reference-nullability-only overload collision |
| EXP-22 | Text "a\\0b" Length | PG cannot store NUL text; SQLite native 1; MySQL/Maria native 3; parameter/transport validation remains provider-specific |
| EXP-23 | Row arities1/2/8 comparison and matching subquery membership | Closed compile cases; arity1 takes Query<T1>, not Query<Row<T1>> |
| EXP-24 | Explicit Cast Int64 value 32767/32768 to Int16 on SQLite/MySQL/Maria | 32767 / KORM-TYPE-005 through cast.int16.checked; ordinary Int16 reader remains strict |
| EXP-25 | Same explicit narrowing on PG | Native SMALLINT result or preserved server range error; no client promise that the server first returns Int64 |
| EXP-26 | Alias/Over/scalar wrapper over a converted result | ResultColumn retains its conversion ID; incompatible CASE branch converters fail KORM-TYPE-003 |

## Validation and stop

`python3 tests/Orm/Expressions/verify.py` compiles operand/row negative cases and
runs the pure semantic native consumer. Real SQL truth/data cases are shared with
ORM-ORACLE and later Integration; do not mark them database-tested from evaluator
unit tests. Register `orm-expressions` and true model/type consumers. Do not edit
Query/DML/Relational folders or add an executor. Stop at the expression module gate.
