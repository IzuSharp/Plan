#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>

#if PROBE_POSTGRES
#include <libpq-fe.h>
#include <poll.h>
#else
#include <sqlite3.h>
#endif

namespace
{
void check(bool value, const char* why)
{
    if (!value)
        throw std::runtime_error(why);
}
constexpr std::string_view name = "Ada O'Reilly 中文";

#if PROBE_POSTGRES
using Result = std::unique_ptr<PGresult, decltype(&PQclear)>;
using Connection = std::unique_ptr<PGconn, decltype(&PQfinish)>;
PGresult* next(PGconn* db)
{
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(15);
    for (;;)
    {
        check(std::chrono::steady_clock::now() < deadline, "libpq result deadline");
        const auto pending = PQflush(db);
        check(pending >= 0, "PQflush");
        if (pending == 0)
            break;
        pollfd descriptor{PQsocket(db), POLLOUT, 0};
        check(poll(&descriptor, 1, 20) >= 0, "poll write");
    }
    for (;;)
    {
        check(std::chrono::steady_clock::now() < deadline, "libpq result deadline");
        check(PQconsumeInput(db) == 1, "PQconsumeInput");
        if (!PQisBusy(db))
            return PQgetResult(db);
        pollfd descriptor{PQsocket(db), POLLIN, 0};
        check(poll(&descriptor, 1, 20) >= 0, "poll read");
    }
}
void drain_command(PGconn* db)
{
    bool reply = false;
    while (auto* raw = next(db))
    {
        Result result(raw, &PQclear);
        if (PQresultStatus(raw) != PGRES_COMMAND_OK)
        {
            std::cerr << PQresultErrorMessage(raw);
            throw std::runtime_error("libpq command status");
        }
        reply = true;
    }
    check(reply, "missing command result");
}
void command(PGconn* db, const char* sql)
{
    check(PQsendQuery(db, sql) == 1, "PQsendQuery");
    drain_command(db);
}
std::string text(PGresult* row, int column)
{
    check(!PQgetisnull(row, 0, column), "unexpected SQL NULL");
    return std::string(PQgetvalue(row, 0, column), static_cast<std::size_t>(PQgetlength(row, 0, column)));
}
std::int64_t int64(PGresult* row, int column)
{
    check(!PQgetisnull(row, 0, column) && PQgetlength(row, 0, column) == 8, "int8 binary shape");
    std::uint64_t value = 0;
    const auto* bytes = reinterpret_cast<const unsigned char*>(PQgetvalue(row, 0, column));
    for (int i = 0; i < 8; ++i)
        value = (value << 8) | bytes[i];
    return static_cast<std::int64_t>(value);
}
int read(PGconn* db, const char* id, bool expected)
{
    const char* values[] = {id};
    check(PQsendQueryPrepared(db, "probe_read", 1, values, nullptr, nullptr, 1) == 1, "PQsendQueryPrepared");
    check(PQsetSingleRowMode(db) == 1, "PQsetSingleRowMode");
    int count = 0;
    bool ended = false;
    while (auto* raw = next(db))
    {
        Result row(raw, &PQclear);
        if (PQresultStatus(raw) == PGRES_SINGLE_TUPLE)
        {
            check(expected && PQnfields(raw) == 5 && PQntuples(raw) == 1, "binary row shape");
            for (int i = 0; i < 5; ++i)
                check(PQfformat(raw, i) == 1, "binary column format");
            check(int64(raw, 0) == 1, "order id");
            check(text(raw, 1) == "12.34", "numeric text exact value");
            check(text(raw, 2) == name, "owned Unicode display name");
            check(PQgetisnull(raw, 0, 3) == 1, "nullable note");
            check(text(raw, 4) == "web", "JSON field value");
            ++count;
        }
        else
        {
            if (PQresultStatus(raw) != PGRES_TUPLES_OK)
                std::cerr << PQresultErrorMessage(raw);
            check(PQresultStatus(raw) == PGRES_TUPLES_OK, "terminal tuples status");
            ended = true;
        }
    }
    check(ended && count == (expected ? 1 : 0), "fully drained row count");
    return count;
}
void probe(const char* connection_string)
{
    check(PQlibVersion() == 180000, "libpq version differs from lock");
    Connection db(PQconnectdb(connection_string), &PQfinish);
    check(db && PQstatus(db.get()) == CONNECTION_OK, "connect PostgreSQL");
    check(PQserverVersion(db.get()) == 180000, "server version differs from lock");
    check(PQsetnonblocking(db.get(), 1) == 0, "set nonblocking");
    std::cout << "libpq_version=" << PQlibVersion() << "\nserver_version=" << PQserverVersion(db.get()) << '\n';
    command(db.get(), "CREATE TABLE dbperf_native_probe(id bigint PRIMARY KEY, amount numeric(18,2) NOT NULL, "
                      "display_name text NOT NULL, note text, settings jsonb NOT NULL)");
    command(db.get(), "BEGIN");
    const char* values[] = {"1", "12.34", name.data(), nullptr, "{\"channel\":\"web\",\"gift\":false}"};
    const Oid types[] = {20, 1700, 25, 25, 3802};
    check(PQsendQueryParams(db.get(), "INSERT INTO dbperf_native_probe VALUES ($1,$2,$3,$4,$5)", 5, types, values,
                            nullptr, nullptr, 0) == 1,
          "bound insert");
    drain_command(db.get());
    command(db.get(), "COMMIT");
    const Oid key_type[] = {20};
    check(PQsendPrepare(
              db.get(), "probe_read",
              "SELECT id,amount::text,display_name,note,settings->>'channel' FROM dbperf_native_probe WHERE id=$1", 1,
              key_type) == 1,
          "prepare");
    drain_command(db.get());
    check(PQsendDescribePrepared(db.get(), "probe_read") == 1, "describe");
    while (auto* raw = next(db.get()))
    {
        Result result(raw, &PQclear);
        check(PQresultStatus(raw) == PGRES_COMMAND_OK && PQnfields(raw) == 5, "description shape");
    }
    const int original = read(db.get(), "1", true);
    read(db.get(), "2", false);
    command(db.get(), "BEGIN");
    command(db.get(), "UPDATE dbperf_native_probe SET amount=99.99, note='rolled back' WHERE id=1");
    command(db.get(), "ROLLBACK");
    const int after_rollback = read(db.get(), "1", true);
    check(PQtransactionStatus(db.get()) == PQTRANS_IDLE, "idle transaction after rollback");
    command(db.get(), "DEALLOCATE probe_read");
    command(db.get(), "DROP TABLE dbperf_native_probe");
    db.reset();
    std::cout << "NATIVE_PROBE_RESULT {\"provider\":\"postgresql\",\"status\":\"passed\",\"rows_materialized\":"
              << original + after_rollback
              << ",\"prepared_reuse\":true,\"parameter_binding\":true,\"unicode\":true,\"null\":true,\"exact_decimal_"
                 "text\":true,\"json_field\":true,\"commit\":true,\"rollback\":true,\"binary_single_row_results\":true,"
                 "\"performance_result\":false}\n";
}
#else
using Statement = std::unique_ptr<sqlite3_stmt, decltype(&sqlite3_finalize)>;
using Connection = std::unique_ptr<sqlite3, decltype(&sqlite3_close)>;
void command(sqlite3* db, const char* sql)
{
    char* message = nullptr;
    const auto status = sqlite3_exec(db, sql, nullptr, nullptr, &message);
    if (status != SQLITE_OK)
    {
        std::string detail = message ? message : "sqlite3_exec";
        sqlite3_free(message);
        throw std::runtime_error(detail);
    }
}
Statement prepare(sqlite3* db, const char* sql)
{
    sqlite3_stmt* raw = nullptr;
    const char* tail = nullptr;
    const auto status = sqlite3_prepare_v3(db, sql, -1, SQLITE_PREPARE_PERSISTENT, &raw, &tail);
    Statement statement(raw, &sqlite3_finalize);
    check(status == SQLITE_OK && raw && tail && *tail == '\0', "sqlite prepare");
    return statement;
}
std::string text(sqlite3_stmt* statement, int column)
{
    check(sqlite3_column_type(statement, column) != SQLITE_NULL, "unexpected NULL");
    const auto* value = sqlite3_column_text(statement, column);
    return std::string(reinterpret_cast<const char*>(value),
                       static_cast<std::size_t>(sqlite3_column_bytes(statement, column)));
}
int read(sqlite3_stmt* statement, std::int64_t id, bool expected)
{
    check(sqlite3_bind_int64(statement, 1, id) == SQLITE_OK, "bind id");
    int count = 0;
    int status;
    while ((status = sqlite3_step(statement)) == SQLITE_ROW)
    {
        check(expected && sqlite3_column_count(statement) == 5, "result shape");
        check(sqlite3_column_int64(statement, 0) == 1, "order id");
        check(sqlite3_column_int64(statement, 1) == 1234, "exact scaled money");
        check(text(statement, 2) == name, "owned Unicode display name");
        check(sqlite3_column_type(statement, 3) == SQLITE_NULL, "nullable note");
        check(text(statement, 4) == "web", "JSON field value");
        ++count;
    }
    check(status == SQLITE_DONE && count == (expected ? 1 : 0), "fully consumed row count");
    check(sqlite3_reset(statement) == SQLITE_OK, "reset prepared query");
    check(sqlite3_clear_bindings(statement) == SQLITE_OK, "clear bindings");
    return count;
}
void probe(const char* filename)
{
    check(sqlite3_libversion_number() == 3051003, "sqlite runtime differs from lock");
    std::cout << "sqlite_version=" << sqlite3_libversion() << "\nsqlite_source_id=" << sqlite3_sourceid() << '\n';
    for (int i = 0; const auto* option = sqlite3_compileoption_get(i); ++i)
        std::cout << "sqlite_compile_option=" << option << '\n';
    sqlite3* raw = nullptr;
    const int opened =
        sqlite3_open_v2(filename, &raw, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX, nullptr);
    Connection db(raw, &sqlite3_close);
    check(opened == SQLITE_OK && raw, "sqlite open");
    check(sqlite3_busy_timeout(raw, 5000) == SQLITE_OK, "busy timeout");
    command(raw, "PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA foreign_keys=ON;");
    command(raw, "CREATE TABLE dbperf_native_probe(id INTEGER PRIMARY KEY, amount_cents INTEGER NOT NULL, display_name "
                 "TEXT NOT NULL, note TEXT, settings TEXT NOT NULL)");
    command(raw, "BEGIN");
    {
        auto insert = prepare(raw, "INSERT INTO dbperf_native_probe VALUES (?1,?2,?3,?4,?5)");
        check(sqlite3_bind_int64(insert.get(), 1, 1) == SQLITE_OK, "insert key");
        check(sqlite3_bind_int64(insert.get(), 2, 1234) == SQLITE_OK, "insert money");
        check(sqlite3_bind_text64(insert.get(), 3, name.data(), name.size(), SQLITE_TRANSIENT, SQLITE_UTF8) ==
                  SQLITE_OK,
              "insert string");
        check(sqlite3_bind_null(insert.get(), 4) == SQLITE_OK, "insert null");
        check(sqlite3_bind_text(insert.get(), 5, "{\"channel\":\"web\",\"gift\":false}", -1, SQLITE_TRANSIENT) ==
                  SQLITE_OK,
              "insert json");
        check(sqlite3_step(insert.get()) == SQLITE_DONE && sqlite3_changes(raw) == 1, "insert result");
    }
    command(raw, "COMMIT");
    auto statement = prepare(raw, "SELECT id,amount_cents,display_name,note,json_extract(settings,'$.channel') FROM "
                                  "dbperf_native_probe WHERE id=?1");
    const int original = read(statement.get(), 1, true);
    read(statement.get(), 2, false);
    command(raw, "BEGIN");
    command(raw, "UPDATE dbperf_native_probe SET amount_cents=9999,note='rolled back' WHERE id=1");
    command(raw, "ROLLBACK");
    const int after_rollback = read(statement.get(), 1, true);
    check(sqlite3_get_autocommit(raw) != 0, "autocommit restored");
    statement.reset();
    check(sqlite3_next_stmt(raw, nullptr) == nullptr, "all statements finalized");
    command(raw, "DROP TABLE dbperf_native_probe");
    check(sqlite3_close(db.release()) == SQLITE_OK, "connection closed");
    std::cout << "sqlite_memory_used_after_close=" << sqlite3_memory_used()
              << "\nsqlite_memory_highwater=" << sqlite3_memory_highwater(0) << '\n';
    std::cout << "NATIVE_PROBE_RESULT {\"provider\":\"sqlite\",\"status\":\"passed\",\"rows_materialized\":"
              << original + after_rollback
              << ",\"prepared_reuse\":true,\"parameter_binding\":true,\"unicode\":true,\"null\":true,\"exact_scaled_"
                 "money\":true,\"json_field\":true,\"commit\":true,\"rollback\":true,\"statements_finalized\":true,"
                 "\"connection_closed\":true,\"performance_result\":false}\n";
}
#endif
} // namespace

int main(int argc, char** argv)
{
    try
    {
        check(argc == 2, "expected database filename or explicit local connection string");
        probe(argv[1]);
        return 0;
    }
    catch (const std::exception& error)
    {
        std::cerr << "NATIVE_PROBE_FAILURE " << error.what() << '\n';
        return 1;
    }
}
