# ORM-SCHEMA-TOOL — explicit acquisition and offline generation

Status: `planned_candidate`; `implementation_authorized: false`.

## Fixed outcome and dependencies

Implement the `Korda.Orm.Schema` local .NET tool and `korda-orm-schema` command
specified in the graph-pinned Design `generation-integration.md` sections 7–8.
Read ORM-C05/ORM-C06 and the provider metadata contract in
`implementation-spec.md`. Reuse the Schema validator/canonical writer and the
Generator's neutral model/emission code. Do not create a second schema format,
parser, naming strategy or row-code emitter.

Start after `ORM-FOUNDATION`; final acceptance requires `ORM-SCHEMA`,
`ORM-GENERATOR`, `ORM-POSTGRES-DRIVER`, `ORM-SQLITE-DRIVER` and
`ORM-MYSQL-DRIVER`. CLI parsing, offline validation, output safety and fixture
adapters can run in parallel with all of them. The live tool is not a prerequisite
for normal generation or runtime query construction.

## Files and fixed deployment

Own `src/Orm/SchemaTool/**` and matching `tests/Orm/SchemaTool/**`:

| Path | Contents |
| --- | --- |
| `Korda.Orm.SchemaTool.csproj` | net11.0 framework-dependent .NET tool; `PackAsTool=true`, `ToolCommandName=korda-orm-schema`, package ID `Korda.Orm.Schema` |
| `Program.cs`, `CommandLine/Options.cs` | Exact subcommand/argument parser, validation and exit-code dispatch |
| `Commands/AcquireCommand.cs` | Credential resolution, provider selection, connection ownership and read orchestration |
| `Commands/ValidateCommand.cs` | Offline read/validation; no driver initialization |
| `Commands/GenerateCommand.cs` | Offline physical-source emission through the same generator models |
| `Providers/MetadataReaderResolver.cs` | Closed switch for PostgreSQL, SQLite and MySqlConnector adapters; MariaDB selects its distinct profile |
| `IO/AtomicOutput.cs` | Temporary-sibling write, flush, replace and failure cleanup |
| `IO/GeneratedFileManifest.cs` | Safe output ownership for offline generated sources under the selected directory |
| `Diagnostics/ConsoleDiagnosticWriter.cs` | Stable safe diagnostic formatting and redaction |

Project references are SchemaModel, Execution and the three provider projects.
The tool links the generator-owned neutral `Model/` and `Emission/` source subset
and compiles it against its one real net11 SchemaModel reference. It does not
reference the netstandard Generators.dll, which contains an analyzer-private
linked copy of the schema types. Exclude RowGenerator/Analysis/generator Diagnostics
from the linked subset. Roslyn CSharp/Common 4.14.0 may be tool-only dependencies
for validating/escaping supplied C# type/name syntax; no user assembly is loaded.
The CLI calls the same SchemaSourceEmitter.Generate facade as the analyzer.
Compiler-only symbol checks remain the generated application's build gate.

This tool is not Native AOT application runtime code. The selected deployment
requires a .NET 11 runtime/SDK on the developer machine. Do not add Java, GraalVM,
Rust, a private database server, reflection-based provider discovery or a hidden
container requirement. Native AOT is required for generated application consumers;
claiming a native tool distribution would need a separate reviewed packaging gate.

The provider owner implements this exact shared boundary; the neutral records are
fixed in `ORM-SCHEMA`, and the execution owner declares the ADO.NET boundary:

```csharp
namespace Korda.Orm.Execution.Metadata;

public sealed record SchemaReadOptions(SqlProfile Profile,
    ImmutableArray<SchemaNameFilter> Includes,
    ImmutableArray<SchemaNameFilter> Excludes,
    SchemaGenerationOptions Generation,
    ImmutableArray<SchemaOverride> Overrides,
    UnresolvedTypePolicy UnresolvedTypes = UnresolvedTypePolicy.Error);

public interface ISchemaCatalogReader
{
    Task<SchemaSnapshot> ReadAsync(DbConnection connection,
        SchemaReadOptions options, CancellationToken cancellationToken = default);
}
```

Import `Korda.Orm.Schema`, `System.Data.Common`, immutable collections and standard
task/cancellation namespaces. The CLI owns opening/disposal. The reader borrows
the connection and performs catalog reads; it does not close it, execute migration
DDL or modify application data. The reader returns coherent neutral metadata.
`ISchemaCatalogReader.ReadAsync` calls the shared `SchemaSnapshotTransform.Apply`
exactly once after its coherent metadata collection, honoring the options before
returning the snapshot. The CLI must not apply filtering/overrides a second time. A provider can use filters only as a
conservative read optimization, preserving every required type/target reference.
Default immutable arrays, a null profile, or mappings=true with rows=false are
argument errors before opening a connection.

Provider tasks own the exact catalog SQL. PostgreSQL uses one tagged-union
statement so all catalog rows share one statement snapshot. SQLite checks
`schema_version` before/after and compares two complete normalized acquisitions.
MySQL/MariaDB compare two complete normalized acquisitions. A mismatch or failed
coherent read raises ORMSCHEMA008, returns exit 3 and leaves the old output intact.
No automatic retry hides concurrent DDL. SchemaTool must not duplicate those
queries or broaden connection permissions.

## Exact CLI behavior

| Command | Accepted inputs | Observable result |
| --- | --- | --- |
| `acquire` | Required `--provider`, `--profile`, `--connection-env`, `--output`; optional repeatable `--include`/`--exclude`, `--overrides`, `--unresolved error|record`, `--namespace`, `--rows true|false`, `--mappings true|false` | Validate options, open the provider, read the already-transformed coherent snapshot, canonicalize and atomically replace one output |
| `validate` | Required `--input` | Read and validate offline; no connection, environment-secret lookup or provider creation |
| `generate` | Required `--input`, `--output`; optional `--mappings true|false` override | Validate offline, produce deterministic physical C# and an owned-file manifest under the output directory |
| `--help`, `--version` | No secret or database arguments required | Print fixed help/version and return success without constructing providers |

`--provider` is exactly `postgresql`, `sqlite`, `mysql` or `mariadb`. It selects a
family, not an assumed server-version capability. The explicit profile must match
the selected family and actual provider/server requirements. The only initial profile IDs are `postgres-18`, `sqlite-3.45`, `mysql-8.4` and
`mariadb-11.8`, respectively. Reject an unknown or incompatible profile; do not
silently choose a nearby one. A profile baseline and the exact tested server
version remain separate metadata.

Read a connection string only from the explicitly named environment variable.
A missing/empty variable is an argument error. Do not support plaintext connection
strings in command-line arguments. Do not include the value in diagnostics,
exceptions printed to console, snapshots or generated source. Query/provider
errors preserve a safe code/category and object identity without echoing secrets.

Each `--include`/`--exclude` value is one JSON array of exactly three string-or-null
segments, for example `'[null,"public","invoice*"]'`. Catalog/schema may be null;
name must be a nonempty string. Null/empty and wildcard/escape behavior is fixed in
`ORM-SCHEMA`; the JSON representation preserves dots and quotes inside names.
Comparison is ordinal and exclusion wins. Filters are not SQL fragments or regex.
The overrides file is exactly `{ "formatVersion": 1, "overrides": [...] }`, using
`SchemaOverride`'s wire shape, duplicate/unknown-field rules and safe diagnostics.
Acquisition defaults are namespace `Korda.Generated`, rows=true and mappings=true.
The explicit switches replace those values. Mappings=true with rows=false is an
argument error; the tool never silently changes the other option.
Keep required type definitions. When a selected relation's FK target is excluded,
preserve the ordered target columns and qualified target identity with
`externalTarget=true`; do not silently drop the FK or reinclude the excluded
relation. Internal target references must resolve normally. Generated relation
navigation to an external target is unavailable until that target is supplied.

`--unresolved` defaults to `error`: an unresolved SQL type/binding declaration prevents replacing
the previous snapshot. Explicit `record` writes a structurally valid snapshot
with unresolved requirements and prints ORMSCHEMA007 warnings; generation still
fails until overrides resolve them. A complete override is a binding declaration;
acquisition does not load an application assembly to prove its static symbol or
selected provider codec exists. The generator checks the referenced symbol, and
execution preflight checks the actual closed codec. This opt-in is never inferred
automatically.

## Implement in this order

1. Build a small deterministic argument parser for the table above. Reject unknown
   switches, missing values, conflicting repetitions and output paths that refer
   to an input file. Parse all options before looking up any secret or connecting.
2. Implement `validate` first with maintained schema fixtures. Return structured
   diagnostics sorted by JSON pointer/code; successful validation does not claim
   a live database still matches the snapshot.
3. Implement the closed adapter resolver. Passing `mariadb` must supply MariaDB
   profile/type rules to the shared MySqlConnector adapter. A resolver test uses
   fakes and asserts which adapter is requested without loading unrelated native
   drivers.
4. Implement acquisition ownership: create the selected data source/connection,
   `OpenAsync(token)`, call the catalog reader, then dispose on success, exception
   or cancellation. Respect a provider's read-snapshot/concurrent-DDL checks;
   surface a consistency failure instead of writing mixed metadata. Do not add
   automatic retries that hide schema changes.
5. Accept only the reader's successfully transformed/validated snapshot. Verify
   its returned profile and generation options match the request, then canonicalize
   it with SchemaSnapshotCodec. A schema validation exception is exit 2, except
   ORMSCHEMA008 coherence failures are exit 3. Do not run the shared transform a
   second time. The previous output is untouched until this entire phase succeeds.
6. Write to a unique temporary sibling in the destination directory, flush and
   close, then atomically replace the requested file. Clean only the task's own
   temporary sibling on error. Never replace a directory or recursively clean a
   user-selected parent directory.
7. Implement `generate` using the generator's shared neutral models/emitter. Its
   output `korda-generated.manifest.json` has formatVersion=1, inputFingerprint
   (64 lowercase SHA-256 digits of canonical effective snapshot bytes), and files
   (ordinal-sorted objects with path and sha256). A file path is the emitter's
   deterministic ASCII .g.cs hint name; its digest covers exact UTF-8/LF bytes. Validate every filename stays within the output directory. Remove
   only stale files previously listed in that manifest; preserve unrelated files.
   Normal generator operation remains available and requires no prebuild tool.
8. Keep physical-source generation and incremental generation mutually explicit:
   a project using the former excludes the corresponding AdditionalFile from
   incremental generation. Never emit duplicate types and silently suppress
   compiler errors.
9. Add console cancellation handling. Return 130 on cancellation; dispose owned
   resources and leave the previous snapshot intact. Do not claim synchronous
   interruption for SQLite or retry a command whose completion is uncertain.
10. Package/help text uses the exact local acquire → review → compile/publish →
    run sequence. Installation and database acquisition are not build events.

Exit codes: 0 success; 2 argument/schema/mapping error; 3 provider connection,
permission/catalog or consistency error; 130 cancellation. Output replacement
failure also returns a nonzero safe diagnostic. Stderr contains diagnostics;
stdout contains concise success/path/version output only.

## Required fixtures and acceptance

| Fixture | Expected outcome |
| --- | --- |
| `ValidateOfflineNoEnvironment` | Valid schema succeeds when no connection variable exists and every provider factory is a throwing fake |
| `AcquireMissingSecret`, `UnknownOption`, `ProfileMismatch` | Exit 2, no connection created, previous output unchanged |
| `FilterNullEmptyAndQuotedName` | Exact JSON triples preserve null/empty and names containing dots; invalid wildcards/escapes fail before connection |
| `FilterExternalForeignKey` | Excluded target absent from relations; explicit external FK identity/order preserved |
| `UnknownTypeStrict`, `UnknownTypeRecord` | Default mode keeps old file and fails; explicit record writes unresolved metadata; subsequent generation fails ORMGEN004/007 |
| `CanonicalSecondAcquire` | Same live metadata/options produce byte-identical output, including key/enum order |
| `PermissionDenied`, `Unreachable`, `ConcurrentDdl` | Exit 3; safe diagnostic, disposed connection and no partial replacement |
| `CancelBeforeOpen`, `CancelDuringRead` | Exit 130; cancellation propagated and owned resources disposed |
| `AtomicWriteFailure` | Injected write/rename failure preserves the previous complete snapshot |
| `GenerateStaleFiles` | Removes only old manifest-owned generated files; keeps a neighboring handwritten file |
| `GenerateNoNetwork` | Emits compilable code from an offline fixture without consulting secrets or adapters |
| `Redaction` | A canary password/connection string appears nowhere in stdout/stderr/snapshot/generated files |

Run actual acquisition on each accepted PostgreSQL, SQLite, MySQL and MariaDB
profile, validate the output, then compile/publish and run a Native AOT consumer
without any additional database access during generation. Compare captured
column/key/enum/default/generated metadata to explicit fixture expectations.
Do not equate a successful connection with metadata correctness.

## Local entry points, CI and stop

```sh
bash tests/Orm/SchemaTool/check.sh --offline
bash tests/Orm/SchemaTool/check.sh --provider postgresql
bash tests/Orm/SchemaTool/check.sh --provider sqlite
bash tests/Orm/SchemaTool/check.sh --provider mysql
bash tests/Orm/SchemaTool/check.sh --provider mariadb
```

The script owns no database server globally; provider lanes consume disposable
fixture endpoints supplied through their documented environment. Offline checks
run without services. Propose `orm-schema-tool` source/test/dependency registration
to the CI owner, including linked Schema/Generator inputs and only the selected
provider lane's service requirements. Ordinary prose changes select no tool build.
`ORM-PACKAGE` separately validates the exact tool archive and installation.

Stop at the reviewed implementation PR and declared checks. Do not add migrations,
a live-build connection, arbitrary plugins, publication, product cutover or legacy
removal.
