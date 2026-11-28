# ORM-PARSER — bounded SQL parsing and translation module

Status: `planned_candidate`; product implementation is **not authorized**.
This optional module does not block the initial DSL/provider release.

## Fixed outcome, inputs and dependencies

Parse the exact grammar below into the same typed immutable nodes used by the
Fluent DSL. Translation is a subsequent target-profile render; normal DSL queries
never round-trip through SQL text. Use Design `implementation-spec.md`,
`contracts.md`, `language-model.md` and `upstream-policy.md` at the immutable batch
revision; consume ORM-C01, ORM-C02, ORM-C03 and ORM-C06.

Start: `ORM-FOUNDATION`; acceptance: `ORM-QUERY`, `ORM-RELATIONAL`,
`ORM-EXPRESSIONS`, `ORM-DML`, `ORM-SCHEMA` and `ORM-RENDER`. Own `src/Orm/Parser/` and
`tests/Orm/Parser/`; the dependency points from Parser toward language/schema
contracts, plus the pure SchemaModel assembly, never back from the core DSL. Do not acquire schema from a live database,
execute supplied SQL or implement a second AST/renderer/executor.

## Mature source mapping and exact files

Pin jOOQ 3.21.10 commit `3c58109e7ab69772de75e640852935ee7e284177`, public
`jOOQ/src/main/java/org/jooq/impl/ParserImpl.java`. Use its public parsing branches
as the source of precedence/context/unsupported-syntax behavior. The C# module
uses a separate token pass and immutable model; it does not port Java reflection
or expand into every grammar accepted by the large upstream parser.

| Source entry | Local implementation |
| --- | --- |
| `parseQuery`, `parseSelect`, `parseField0`, `parseCondition` | Full-input entry checks and syntax-class dispatch; trailing unexpected content is never discarded |
| `parseWith`, `parseJoinedTable`, `parseIdentifier`, `parseTableName` | Scoped relation/CTE and quoted-name binding |
| `parseInsert`, `parseUpdate`, `parseDelete`, `parseSetClauseList` | Structural DML, target/assignment ownership and ordered values |
| `parseStringLiteral`, numeric/token helpers | Bounded lexical handling; quoted content never interpreted as a placeholder |
| `requireProEdition`, `requireUnsupportedSyntax` | Unsupported diagnostics; do not invent missing commercial grammar/transform bodies |

| Owned file / type | Exact responsibility |
| --- | --- |
| `SqlParser.cs` | Public entry methods below, pass orchestration, no database I/O |
| `SqlParseOptions.cs` | Source profile, explicit search path, fixed budget defaults, AllowUnfilteredMutation=false |
| `SqlToken.cs`, `SqlLexer.cs` | Token kind, raw UTF-16 span, decoded identifier/literal metadata; `Lex` |
| `Syntax/` | Internal immutable syntax records carrying spans; these are parser syntax, not a competing executable query model |
| `StatementParser.cs` | `ParseSelect`, `ParseWith`, `ParseInsert`, `ParseUpdate`, `ParseDelete` |
| `ExpressionParser.cs` | Pratt parser `ParseExpression(minBindingPower)` plus predicates/CASE/function/window suffixes |
| `NameBinder.cs` | `BindTable`, `BindColumn`, `BindCte`, scope stack and schema lookup |
| `TypeBinder.cs` | Closed literals/operators/functions/parameters, explicit registered casts, expected projection compatibility |
| `ParseParameters.cs` | `Named<T>(string,Param<T>)`, `Position<T>(int,Param<T>)`; immutable typed parameter declarations, no request values |
| `ParseResult.cs`, `ParserDiagnostic.cs` | Success/value/one primary diagnostic with stage, span and code |
| Tests | `LexerTests`, `PrecedenceTests`, `ScopeTests`, `ParameterTests`, `DmlTests`, `BudgetTests`, `TranslationTests`, `NativeConsumer` |

## Public entry contract — no unspecified result-type inference

The fixed entry methods are:

```csharp
ParseResult<ParsedSyntax> ParseSyntax(string sql, SqlParseOptions options);
ParseResult<Query<T>> ParseSelect<T>(string sql, SqlParseOptions options,
    SchemaSnapshot schema, ParseParameters parameters, Projection<T> expected);
ParseResult<InsertBuilder> ParseInsert(string sql, SqlParseOptions options,
    SchemaSnapshot schema, ParseParameters parameters);
ParseResult<UpdateBuilder> ParseUpdate(string sql, SqlParseOptions options,
    SchemaSnapshot schema, ParseParameters parameters);
ParseResult<DeleteBuilder> ParseDelete(string sql, SqlParseOptions options,
    SchemaSnapshot schema, ParseParameters parameters);
ParseResult<ReturningMutation<T>> ParseReturning<T>(string sql,
    SqlParseOptions options, SchemaSnapshot schema, ParseParameters parameters,
    Projection<T> expected);
```

ParsedSyntax is non-executable syntax evidence. It has no Render/Execute method.
For ParseSelect, `expected` supplies the declared output type/alias contract; the
parser checks degree, each SQL identity/nullability and exact output alias, then
constructs a Projection<T> using the **resolved parsed fields**. It does not reuse
unrelated Field relation IDs from the expected projection. Arbitrary CLR result
types are never manufactured at runtime. Existing generated mapping validation
still runs before execution of the resulting Query<T>.

DML parsers construct the same immutable InsertBuilder/UpdateBuilder/DeleteBuilder
through their internal checked-node factories. They do not create new parser-only
mutation handles. Non-generic ParseInsert/Update/Delete reject a RETURNING clause
with KORM-PARSER-008 because no typed result projection was supplied. ParseReturning<T>
requires an INSERT/UPDATE/DELETE with RETURNING, resolves the clause, checks its
degree/identities/exact aliases against expected, then calls the ordinary builder's
Returning<T> with the resolved parsed projection to create ReturningMutation<T>.
It never exposes an intermediate mutation with an unvalidated result shape. An
entry for the wrong statement kind returns KORM-PARSER-007. The DML owner supplies
the shared internal factory; this task does not change its execution facade.

ParseResult<T> contains Success, Value (present only on success), and an immutable
array with zero or one primary ParserDiagnostic. Diagnostic has Code, Stage
(Lexical/Syntax/Resolution), Start, Length, Line and Column. Offsets/lengths use
UTF-16 code units; lines/columns are 1-based. Compute line starts once. EOF errors
have Start=input.Length and Length=0. Stop at the first primary error in pass order;
no speculative error-recovery query is returned.

## Supported input grammar

Keywords are ASCII case-insensitive. Brackets below mean optional grammar, braces
mean repetition; quoted terminals are literal syntax, not SQL text to emit.

```ebnf
input       = statement, [";"], EOF ;
statement   = [with], (selectSet | insert | update | delete) ;
with        = "WITH", ["RECURSIVE"], cte, {",", cte} ;
cte         = identifier, ["(", identifiers, ")"], "AS",
              ["MATERIALIZED" | "NOT MATERIALIZED"], "(", selectSet, ")" ;
selectSet   = selectTerm, {setOperator, selectTerm}, [order], [pagination] ;
selectTerm  = selectCore | "(", selectSet, ")" ;
setOperator = "UNION" | "UNION ALL" | "INTERSECT" | "INTERSECT ALL"
              | "EXCEPT" | "EXCEPT ALL" ;
selectCore  = "SELECT", ["DISTINCT"], selectItem, {",", selectItem},
              ["FROM", relation, {join}], ["WHERE", condition],
              ["GROUP BY", expressions], ["HAVING", condition] ;
selectItem  = expression, ["AS", identifier] ;
relation    = qualifiedName, [["AS"], identifier]
              | "(", selectSet, ")", ["AS"], identifier ;
join        = ["INNER"], "JOIN", relation, "ON", condition
              | ("LEFT" | "RIGHT" | "FULL"), ["OUTER"], "JOIN", relation,
                "ON", condition
              | "CROSS JOIN", relation ;
order       = "ORDER BY", sort, {",", sort} ;
sort        = expression, ["ASC" | "DESC"], ["NULLS FIRST" | "NULLS LAST"] ;
pagination  = "LIMIT", unsignedIntegerOrParameter,
              ["OFFSET", unsignedIntegerOrParameter]
              | "OFFSET", unsignedIntegerOrParameter ;
insert      = "INSERT INTO", qualifiedName,
              ("(", identifiers, ")", ("VALUES", valueRow, {",", valueRow}
                | selectSet) | "DEFAULT VALUES"), [conflict], [returning] ;
update      = "UPDATE", qualifiedName, [["AS"], identifier], "SET", assignments,
              ["WHERE", condition], [returning] ;
delete      = "DELETE FROM", qualifiedName, [["AS"], identifier],
              ["WHERE", condition], [returning] ;
returning   = "RETURNING", selectItem, {",", selectItem} ;
```

Conflict grammar is exactly PostgreSQL/SQLite `ON CONFLICT [(columns) [WHERE
condition] | ON CONSTRAINT name] DO NOTHING | DO UPDATE SET assignments [WHERE
condition]`, or source MySQL/Maria `ON DUPLICATE KEY UPDATE assignments`. MySQL
VALUES sources may have `AS rowAlias` before the conflict clause. Resolve that
alias's fields to the shared Excluded node. Maria VALUES(column) is admitted only
inside that conflict-update context and becomes Excluded. Source profile
capabilities validate these distinctions before target translation.

Expressions include qualified/unqualified column references, scalar literals,
known parameters, parentheses, unary +/-, arithmetic + - * / %, comparisons
= <> != < <= > >=, AND/OR/NOT, IS [NOT] NULL, IS [NOT] DISTINCT FROM, LIKE [ESCAPE
one-character literal], [NOT] IN(nonempty expression list or SELECT), EXISTS
(SELECT), searched CASE WHEN/THEN/ELSE/END, CAST(expr AS registeredType), and the
closed function set COUNT/SUM/MIN/MAX/AVG/COALESCE/LOWER/UPPER/LENGTH/ABS. COUNT(*)
is the only admitted star. Function names and overload result types come from the
existing expression catalog; an unknown function is not guessed to return Text.

ROW_NUMBER, RANK and DENSE_RANK are admitted only with an inline OVER specification:
optional PARTITION BY, optional ORDER BY, optional ROWS/RANGE BETWEEN bounds.
Bounds are UNBOUNDED PRECEDING/FOLLOWING, CURRENT ROW or nonnegative integer
PRECEDING/FOLLOWING. The common window validator rejects illegal start/end order
and function/frame combinations. Named WINDOW clauses, GROUPS/EXCLUDE in parser
input, LATERAL syntax, DISTINCT ON, QUALIFY, SELECT *, USING/NATURAL joins,
UPDATE FROM/DELETE USING, MERGE, DDL, routines, transaction/session commands,
procedural blocks, optimizer hints and commercial-only grammar are outside this
initial parser subset. Their DSL counterparts may have wider independent support.

Recursive CTE grammar accepts one anchor plus UNION ALL recursive member. Require
an explicit CTE column list, bind anchor types first, then make that declared row
shape visible to the recursive member, and require compatible degree/types.
Mutual recursion, multiple recursive references and recursive aggregates are
rejected by the same declared relational subset; do not leave types Unknown.

## Lexer, precedence and resource algorithms

Budgets: at most 1,048,576 UTF-16 code units, 100,000 tokens, parse nesting depth
128, 128 CTEs and 65,535 declared/encountered parameter positions. Check input size
before token allocation; count nesting before recursive descent; check token and
list limits before appending. Scan with one monotonically increasing index; do not
use an unbounded backtracking regular expression or repeated whole-input substring
search. Token spans retain the original string; decode escapes once when needed.

Recognize whitespace, -- line comments and /* block comments */. Nested block
comments are allowed only for PostgreSQL source and count toward depth. Reject
MySQL/Maria executable comments `/*!...*/` and optimizer comments `/*+...*/` instead
of discarding their meaning. Unterminated strings/comments/quoted identifiers have
an opening-token span and KORM-PARSER-001. Semicolons inside them are ordinary
content, never statement delimiters.

Single quotes escape by doubling. The accepted MySQL/Maria source profile requires
NO_BACKSLASH_ESCAPES and HIGH_NOT_PRECEDENCE=off; MariaDB also requires
EMPTY_STRING_IS_NULL=off. Do not guess mode from text. PostgreSQL source additionally
admits dollar-quoted strings with an exact empty/ASCII-identifier tag. Escape-string
E'...' syntax is outside this baseline. Double-quoted identifiers are accepted for
PG/SQLite, backticks for MySQL/Maria and SQLite; SQLite square-bracket identifiers
are not in the initial input grammar. Bare identifiers use ASCII letters/digits/_
with a letter/_ start; non-ASCII identifiers must be quoted.

Pratt binding powers, from low to high: OR=10, AND=20, prefix NOT=30,
comparison/IS/LIKE/IN=40, +-=50, */%=60, unary +/-=70, primary/function/cast=80.
Binary arithmetic is left-associative. Reject chained non-parenthesized comparison
`a=b=c`; it is not Boolean-to-number coercion. NOT consumes a complete comparison,
so `NOT a=1 AND b=2` is `(NOT (a=1)) AND (b=2)`. IN list commas do not terminate the
surrounding SELECT list. Searched CASE has its own terminator-aware parser.
Set precedence is source-profile specific: PG/MySQL/Maria INTERSECT binds more
tightly than UNION/EXCEPT; SQLite compounds associate left-to-right. Explicit
parentheses always override it. The produced tree preserves that meaning when
rendered to another profile.

Integers use Int32 when representable, otherwise Int64; signed minimum literals
are recognized before range selection. Decimal-point literals use checked CLR
decimal with explicit precision/scale. Exponent/floating-special/hex numeric
syntax is outside the baseline. Overflow is KORM-PARSER-006, never silent Double.
Strings/booleans and explicitly CAST NULL have known SQL types. An untyped NULL
must be resolved by a compatible expression/expected projection context; otherwise
fail instead of fabricating an arbitrary object-typed Field.

## Name/type/parameter binding and DML intent

Run syntax to completion before name binding. Build a lexical scope frame per
SELECT, CTE and derived relation. Allocate new relation IDs for every alias occurrence;
self joins cannot reuse an entity's ID. Bind qualified names first, unqualified
columns only when exactly one visible relation supplies the name. Projection
aliases resolve in allowed ORDER BY positions, not WHERE. Correlated subqueries
may see declared outer scopes; a non-lateral derived relation cannot capture a
sibling. Forward CTE/self references require the explicit recursive rule.

Use the supplied SchemaSnapshot and explicit search path; no current session,
default schema guessing or network query. PG bare names fold ASCII uppercase to
lowercase, quoted names are exact. SQLite identifiers compare ASCII-insensitively,
including quoted names. MySQL/Maria table lookup uses the profile's observed
lower_case_table_names setting, while columns/aliases use their declared source
rules. For non-ASCII names the initial resolver requires an exact catalog spelling
rather than inventing culture-dependent server case folding. Preserve the resolved
catalog name and the source alias separately. Missing/ambiguous metadata fails
resolution; ParseSyntax alone can still report syntax success without strong typing.

PostgreSQL input placeholders are $1..$N. SQLite admits ? (next encounter position),
?N, :name and @name; MySQL/Maria admit ? and declared @name. Every reference must
exist in ParseParameters with its typed Param<T>; position is 1-based and name
matching is ordinal. Duplicate token references retain one SlotId. Undeclared
@name is not interpreted as a session variable. Placeholder-like text inside
strings/comments/identifiers is ignored by the parameter binder. Mixing declared
named and positional inputs is allowed, but aliasing them to different types for
one SlotId fails before query construction. All declared entries must be used.

Example: PG `$2 + $1 + $2` resolves slots B,A,B and rendering to SQLite emits
`@p0 + @p1 + @p2` with those three logical identities. Physical ordinals follow
final target emission, not the input placeholder number. ParseParameters contains
no values; the caller later supplies typed ParameterValues to bind the rendered
template. Source SQL literals remain explicit Literal nodes and participate in
its template fingerprint. Literal pagination uses the same LiteralNode as
QueryOperations.LimitLiteral; a typed parameter pagination token remains a parameter
and cannot acquire SQLite's at-most-one scalar proof from its current value.

ParseUpdate/Delete without WHERE fails unless AllowUnfilteredMutation=true. That
explicit option maps to the shared AllRows marker; there is no runtime confirmation
flow. Shared old-row assignment semantics still apply: cross-assignment dependencies
on MySQL/Maria fail the dialect rule, even if the input text used native left-to-right
SQL. DML target/column/type and source-profile checks run before returning a builder.

## Exact diagnostics and fixtures

| Code | Fixed message template |
| --- | --- |
| `KORM-PARSER-001` | `Unterminated or invalid token at offset {offset}.` |
| `KORM-PARSER-002` | `Expected {expected} at offset {offset}; found {actual}.` Syntax/EOF mismatch |
| `KORM-PARSER-003` | `Syntax '{syntax}' is outside parser profile '{profile}'.` Unsupported grammar/comment/multiple statement |
| `KORM-PARSER-004` | `Name '{name}' is unresolved or ambiguous in this scope.` |
| `KORM-PARSER-005` | `Parameter '{parameter}' has no unique compatible declaration.` Also unused declaration |
| `KORM-PARSER-006` | `Expression at offset {offset} has no compatible declared SQL type.` |
| `KORM-PARSER-007` | `Expected statement kind '{expected}', found '{actual}'.` |
| `KORM-PARSER-008` | `Parsed result column {ordinal} does not match the declared projection.` |
| `KORM-PARSER-009` | `Mutation without WHERE requires AllowUnfilteredMutation.` |
| `KORM-PARSER-010` | `Parser budget '{budget}' exceeded its limit {limit}.` |

Required fixtures use a schema with users(id Int64 non-null, name Text non-null,
score nullable Int64) and departments(id Int64, name Text). Include:

- `SELECT u.id AS "Id" FROM users AS u WHERE u.score >= $1 OR u.id = $1` with one
  Int64 declaration; PG render has $1/$2 tied to that slot, SQLite @p0/@p1; expected
  projection is one non-null Int64 column alias Id.
- `SELECT 'x;@p0' AS "Text" /* @missing */` contains no parameter occurrence and
  one Text output; no statement splitting inside the literal/comment.
- The A EXCEPT (B EXCEPT C) tree translates to SQLite's checked derived operand
  wrapper and retains {1,3} for A={1,2,3}, B={2,3}, C={3}.
- `NOT score = $1 AND id = $2` has the exact precedence tree specified above;
  typed NULL binding retains SQL UNKNOWN instead of becoming IS NULL.
- `SELECT id FROM users u JOIN departments d ON u.id=d.id` fails ambiguous id at
  its source span; a self join with distinct aliases resolves separate identities.
- `SELECT 1; SELECT 2` fails at the second statement; `/*! SELECT 1 */` and
  unknown functions fail explicitly; no executable template is returned.
- SQL length 1,048,577, token 100,001, nesting 129 and parameter position 65,536
  fail the named budget before unbounded allocations/recursion.
- Valid INSERT VALUES/SELECT, DEFAULT VALUES, each accepted conflict form and
  RETURNING; unfiltered UPDATE/Delete default fails and explicit option succeeds;
  assignments with unsafe target semantics fail before target translation.

For every negative fixture assert Code/Stage/Start/Length and absence of a query
value. For positive fixtures assert typed node identity/scopes/result metadata,
then target SQL/ordered parameters and independent result semantics. Eligible
pinned jOOQ cases are a differential input, not the sole correctness oracle.

Publish/run a driver-free Native AOT parser consumer, including typed declarations,
quoted Unicode names and deliberately invalid inputs. Probe bounded adversarial
input to verify monotonic scanning and budget enforcement; do not claim linear
wall time for arbitrary schema lookup or unbounded source expressions. Integration
separately executes target SQL on actual providers. Stop at the scoped reviewed
parser PR; no universal translation claim, implicit execution, migrations, product
publication, merge or blocking of unrelated DSL/provider acceptance.

Primary source: [pinned ParserImpl](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ/src/main/java/org/jooq/impl/ParserImpl.java),
[PostgreSQL lexical rules](https://www.postgresql.org/docs/18/sql-syntax-lexical.html),
[SQLite SELECT grouping](https://www.sqlite.org/lang_select.html),
[MySQL SQL modes](https://dev.mysql.com/doc/refman/8.4/en/sql-mode.html).

## Exact local runner contract

This task owns `tests/Orm/Parser/verify.py`,
`tests/Orm/Parser/Korda.Orm.Parser.Tests.csproj` and its Program/fixture files.
The CI command, from repository root with no additional flags, is:

```sh
python3 tests/Orm/Parser/verify.py
```

The runner compiles the packet's positive/negative declaration cases, publishes
its actual consumer with `dotnet publish tests/Orm/Parser/Korda.Orm.Parser.Tests.csproj -c Release -r linux-x64 -p:PublishAot=true`,
then executes that native consumer and asserts RuntimeFeature.IsDynamicCodeSupported
is false. Use the repository's pinned SDK/restore settings; place outputs under
artifacts, never beside source. Run this packet's enumerated pure fixtures and
report individual case failures with nonzero exit. The runner does not start a
database, accept an absent peer as a passing stub, or claim live SQL correctness.
Real four-server rows, faults and SQL execution remain ORM-INTEGRATION's gate.
