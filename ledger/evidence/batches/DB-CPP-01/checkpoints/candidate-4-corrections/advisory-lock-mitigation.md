# Preserved advisory-lock mitigation

## Report paragraph

The fixed Rust baseline already isolated an upstream SQLx Migrator behavior:
a direct checksum-mismatch return could leave a session advisory lock held.
NativeWeave used a dedicated administrative connection and physically closed
it after every successful or failed operation, so the connection was never
returned to the request pool. The C++ implementation preserves this policy:
checksum validation retains the same public error classification, and the
Host closes its dedicated libpq connection on both success and exception
before publishing completion. This is a preserved mitigation, with no new
public behavior difference attributed to it. The original Rust test first
demonstrates the upstream lock retention, then verifies lock release after
physical close and zero live product administration connections. The C++ B02
bridge keeps a separately identified contaminated-lease negative control
(one advisory lock before close, zero after retirement); it does not claim to
rerun the removed SQLx code. The unchanged B08 consumer checks the actual
checksum rejection, nonzero correlation ID, subsequent successful validation,
and deterministic source/resource retirement.

## Fixed source and assertion references

| Evidence | Meaning |
| --- | --- |
| [Rust `migrations/src/postgres.rs`](https://github.com/IzuSharp/NativeWeave/blob/465cd0f90e6af05ec50eb581156240377cf0825b/native/database/migrations/src/postgres.rs), `run` | Captures the administrative result and always awaits dedicated `connection.close()`. Its comment identifies upstream early-return lock retention. |
| [Rust `migrations/src/tests.rs`](https://github.com/IzuSharp/NativeWeave/blob/465cd0f90e6af05ec50eb581156240377cf0825b/native/database/migrations/src/tests.rs), direct Migrator mismatch oracle | Observes advisory locks greater than zero on the intentionally retained direct SQLx connection, then zero after physical close; the product path rejects as `Checksum` with `LIVE_CONNECTIONS == 0`. |
| [C++ `administration.cpp`](https://github.com/IzuSharp/NativeWeave/blob/3e49cee95d206468a32c94f0a3b98e923f02acbf/native/cpp/src/administration.cpp), `administer` / `validate_ledger` | Acquires the migration advisory lock and preserves checksum validation. The dedicated connection owns lock lifetime. |
| [C++ `host_abi.cpp`](https://github.com/IzuSharp/NativeWeave/blob/3e49cee95d206468a32c94f0a3b98e923f02acbf/native/cpp/src/host_abi.cpp), `nw_db_admin_create_v1` | Both normal and exception paths call `connection->close()`; no request-pool reuse occurs. |
| [C++ `provider.cpp`](https://github.com/IzuSharp/NativeWeave/blob/3e49cee95d206468a32c94f0a3b98e923f02acbf/native/cpp/src/provider.cpp), `ProviderConnection::close` | Physically closes libpq with `PQfinish`. |
| [B02 `fixtures/postgres.cpp`](https://github.com/IzuSharp/NativeWeave/blob/3e49cee95d206468a32c94f0a3b98e923f02acbf/native/cpp/tests/fixtures/postgres.cpp), `migration_lock` | Explicitly creates one advisory lock as a contaminated-lease control and observes zero after actual dedicated retirement. |
| [Unchanged B08 `Program.cs`](https://github.com/IzuSharp/NativeWeave/blob/465cd0f90e6af05ec50eb581156240377cf0825b/tests/Data.Migrations/Program.cs), `Suite.Run` | Verifies checksum rejection as `DatabaseErrorKind.InvalidState`, nonzero correlation, subsequent validation, source cleanup and final native counts. |

The cited C++ administrative and disposal paths predate the input-admission
correction and are unchanged by it. These references describe the preserved
policy; formal acceptance remains bound to the final tested candidate.
