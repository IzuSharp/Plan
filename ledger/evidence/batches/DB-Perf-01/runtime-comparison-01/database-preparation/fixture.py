#!/usr/bin/env python3
"""Create and verify the exact DB-Perf-01 8x1024 deterministic fixture.

Only explicit task-owned destinations are changed. No table is dropped.
Generation follows Korda Dataset.cs at 36bd5ba169b628ba4d61dd9fe260eaef5ff15599.
The verifier reads every actual stored row and compares it with the seed formula.
"""
from __future__ import annotations
import argparse
import csv
import ctypes as C
import hashlib
import io
import json
from pathlib import Path
import subprocess
import time

TENANTS, ORDERS, CUSTOMERS = 8, 1024, 256
SOURCE = "https://github.com/IzuSharp/Korda/blob/36bd5ba169b628ba4d61dd9fe260eaef5ff15599/benchmarks/db-perf/managed/Korda/Dataset.cs"
INDEXES = {
    "orders_created": ("orders", ["TenantId", "CreatedAt", "Id"]),
    "orders_customer": ("orders", ["TenantId", "CustomerId", "Id"]),
    "order_lines_parent": ("order_lines", ["TenantId", "OrderId"]),
    "order_lines_product": ("order_lines", ["TenantId", "Product", "OrderId"]),
}
SCHEMA = {
    "db_perf_metadata": [("schema_version", "BIGINT", True, 0), ("tenants", "BIGINT", True, 0), ("orders_per_tenant", "BIGINT", True, 0)],
    "customers": [("Id", "BIGINT", False, 1), ("Name", "TEXT", True, 0), ("Email", "TEXT", False, 0)],
    "orders": [("TenantId", "BIGINT", True, 1), ("Id", "BIGINT", True, 2), ("CreatedAt", "BIGINT", True, 0), ("CustomerId", "BIGINT", False, 0), ("Total", "MONEY", True, 0), ("Note", "TEXT", False, 0), ("Version", "BIGINT", True, 0), ("Settings", "SETTINGS", True, 0), ("InternalMemo", "TEXT", True, 0)],
    "order_lines": [("Id", "BIGINT", False, 1), ("TenantId", "BIGINT", True, 0), ("OrderId", "BIGINT", True, 0), ("Product", "TEXT", True, 0), ("Quantity", "BIGINT", True, 0)],
}

def customer_id(i):
    return None if i % 7 == 0 else 1 + i % 8 if i % 10 < 7 else 9 + i % 248

def cents(t, i):
    return 100 + (t * 1009 + i * 37) % 100000

def order(t, i):
    return (t, i, 1700000000 + i // 4, customer_id(i), cents(t, i),
            None if i % 5 == 0 else "note-" + str(i % 16), 1,
            {"Channel": "web" if i % 2 == 0 else "store", "Gift": i % 11 == 0},
            "m" * (2048 if i % 17 == 0 else 32))

def sql_value(v):
    return "NULL" if v is None else str(v) if isinstance(v, int) else "'" + str(v).replace("'", "''") + "'"

def generate(provider):
    money, settings = ("NUMERIC(18,2)", "JSONB") if provider == "postgresql" else ("BIGINT", "TEXT")
    sql = [
        "CREATE TABLE db_perf_metadata (schema_version BIGINT NOT NULL, tenants BIGINT NOT NULL, orders_per_tenant BIGINT NOT NULL);",
        'CREATE TABLE customers ("Id" BIGINT PRIMARY KEY, "Name" TEXT NOT NULL, "Email" TEXT NULL);',
        'CREATE TABLE orders ("TenantId" BIGINT NOT NULL, "Id" BIGINT NOT NULL, "CreatedAt" BIGINT NOT NULL, "CustomerId" BIGINT NULL, "Total" ' + money + ' NOT NULL, "Note" TEXT NULL, "Version" BIGINT NOT NULL, "Settings" ' + settings + ' NOT NULL, "InternalMemo" TEXT NOT NULL, PRIMARY KEY("TenantId","Id"));',
        'CREATE TABLE order_lines ("Id" BIGINT PRIMARY KEY, "TenantId" BIGINT NOT NULL, "OrderId" BIGINT NOT NULL, "Product" TEXT NOT NULL, "Quantity" BIGINT NOT NULL);',
        "BEGIN;",
    ]
    for first in range(1, CUSTOMERS + 1, 128):
        rows = [(i, f"Customer-{i:04d}", None if i % 5 == 0 else f"customer-{i}@example.invalid") for i in range(first, min(first + 128, CUSTOMERS + 1))]
        sql.append("INSERT INTO customers VALUES " + ",".join("(" + ",".join(map(sql_value, row)) + ")" for row in rows) + ";")
    line_id = 0
    for tenant in range(1, TENANTS + 1):
        for first in range(1, ORDERS + 1, 64):
            rows, lines = [], []
            for i in range(first, min(first + 64, ORDERS + 1)):
                row = list(order(tenant, i))
                row[7] = json.dumps(row[7], separators=(",", ":"))
                values = list(map(sql_value, row))
                if provider == "postgresql":
                    values[4] = f"{row[4] // 100}.{row[4] % 100:02d}"
                rows.append("(" + ",".join(values) + ")")
                for line in range(0 if i % 5 == 0 else 1 + i % 3):
                    line_id += 1
                    values = (line_id, tenant, i, f"product-{(i * 7 + line) % 32:02d}", 1 + (i + line) % 7)
                    lines.append("(" + ",".join(map(sql_value, values)) + ")")
            sql.append("INSERT INTO orders VALUES " + ",".join(rows) + ";")
            if lines:
                sql.append("INSERT INTO order_lines VALUES " + ",".join(lines) + ";")
    sql += [f"INSERT INTO db_perf_metadata VALUES (1,{TENANTS},{ORDERS});", "COMMIT;"]
    for name, (table, fields) in INDEXES.items():
        sql.append("CREATE INDEX " + name + " ON " + table + "(" + ",".join('"' + field + '"' for field in fields) + ");")
    sql.append("ANALYZE;")
    return "\n".join(sql) + "\n", line_id

class Sqlite:
    def __init__(self, library, database):
        self.library = Path(library).resolve()
        self.lib = C.CDLL(str(self.library))
        self.lib.sqlite3_open_v2.argtypes = [C.c_char_p, C.POINTER(C.c_void_p), C.c_int, C.c_char_p]
        self.lib.sqlite3_open_v2.restype = C.c_int
        self.lib.sqlite3_close_v2.argtypes = [C.c_void_p]
        self.lib.sqlite3_free.argtypes = [C.c_void_p]
        self.callback_type = C.CFUNCTYPE(C.c_int, C.c_void_p, C.c_int, C.POINTER(C.c_char_p), C.POINTER(C.c_char_p))
        self.lib.sqlite3_exec.argtypes = [C.c_void_p, C.c_char_p, self.callback_type, C.c_void_p, C.POINTER(C.c_void_p)]
        self.lib.sqlite3_exec.restype = C.c_int
        self.db = C.c_void_p()
        code = self.lib.sqlite3_open_v2(str(database).encode(), C.byref(self.db), 2 | 4 | 0x10000, None)
        if code:
            raise RuntimeError("sqlite3_open_v2: " + str(code))
        self.execute("PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA foreign_keys=ON; PRAGMA busy_timeout=5000;")

    def execute(self, sql):
        rows = []
        @self.callback_type
        def callback(unused, count, values, names):
            rows.append(tuple(values[i].decode("utf-8") if values[i] is not None else None for i in range(count)))
            return 0
        error = C.c_void_p()
        code = self.lib.sqlite3_exec(self.db, sql.encode(), callback, None, C.byref(error))
        if code:
            message = C.cast(error, C.c_char_p).value.decode() if error else str(code)
            if error:
                self.lib.sqlite3_free(error)
            raise RuntimeError("SQLite: " + message)
        return rows

    def close(self):
        if self.db:
            code = self.lib.sqlite3_close_v2(self.db)
            if code:
                raise RuntimeError("sqlite3_close_v2: " + str(code))
            self.db = None

class Postgres:
    def __init__(self, psql, connection):
        self.psql, self.connection = str(psql), connection

    def execute(self, sql):
        query = "COPY (" + sql.rstrip(";\n ") + ") TO STDOUT WITH (FORMAT CSV, NULL '\\N');"
        result = subprocess.run([self.psql, "--no-psqlrc", "--set", "ON_ERROR_STOP=1", "--dbname", self.connection, "--command", query], check=True, capture_output=True, text=True, timeout=60)
        return [tuple(None if x == "\\N" else x for x in row) for row in csv.reader(io.StringIO(result.stdout))]

    def initialize(self, path):
        subprocess.run([self.psql, "--no-psqlrc", "--set", "ON_ERROR_STOP=1", "--dbname", self.connection, "--file", str(path)], check=True, capture_output=True, text=True, timeout=120)

    def close(self):
        pass

def verify(db, provider, expected_lines):
    from decimal import Decimal
    schema_observed = {}
    for table, fields in SCHEMA.items():
        expected_fields = [(name, ("NUMERIC(18,2)" if provider == "postgresql" else "BIGINT") if typ == "MONEY" else ("JSONB" if provider == "postgresql" else "TEXT") if typ == "SETTINGS" else typ, null, pk) for name, typ, null, pk in fields]
        if provider == "sqlite":
            rows = db.execute("PRAGMA table_info('" + table + "')")
            actual_fields = [(r[1], r[2].upper(), bool(int(r[3])), int(r[5])) for r in rows]
            assert actual_fields == expected_fields, (table, actual_fields, expected_fields)
            assert all(r[4] is None for r in rows), "Unexpected SQLite column default"
            assert not db.execute("PRAGMA foreign_key_list('" + table + "')"), "Unexpected SQLite foreign key"
            schema_observed[table] = actual_fields
        else:
            rows = db.execute("SELECT column_name, CASE WHEN data_type='numeric' THEN 'NUMERIC('||numeric_precision||','||numeric_scale||')' ELSE upper(data_type) END, is_nullable, column_default FROM information_schema.columns WHERE table_schema='public' AND table_name='" + table + "' ORDER BY ordinal_position")
            expected_pg = [(name, typ, "NO" if null or pk else "YES", None) for name, typ, null, pk in expected_fields]
            assert rows == expected_pg, (table, rows, expected_pg)
            pks = db.execute("SELECT a.attname FROM pg_index i JOIN pg_class c ON c.oid=i.indrelid JOIN pg_namespace n ON n.oid=c.relnamespace CROSS JOIN LATERAL unnest(i.indkey) WITH ORDINALITY k(attnum,pos) JOIN pg_attribute a ON a.attrelid=c.oid AND a.attnum=k.attnum WHERE n.nspname='public' AND c.relname='" + table + "' AND i.indisprimary ORDER BY k.pos")
            assert [r[0] for r in pks] == [name for name, typ, null, pk in sorted(expected_fields, key=lambda f: f[3]) if pk], (table, pks)
            schema_observed[table] = rows
    expected_count = {"db_perf_metadata": 1, "customers": CUSTOMERS, "orders": TENANTS * ORDERS, "order_lines": expected_lines}
    counts = {table: int(db.execute("SELECT count(*) FROM " + table)[0][0]) for table in expected_count}
    assert counts == expected_count, (counts, expected_count)
    assert db.execute("SELECT schema_version,tenants,orders_per_tenant FROM db_perf_metadata") == [("1", str(TENANTS), str(ORDERS))]
    customers = db.execute('SELECT "Id","Name","Email" FROM customers ORDER BY "Id"')
    assert customers == [(str(i), f"Customer-{i:04d}", None if i % 5 == 0 else f"customer-{i}@example.invalid") for i in range(1, CUSTOMERS + 1)]
    rows = db.execute('SELECT "TenantId","Id","CreatedAt","CustomerId","Total","Note","Version","Settings","InternalMemo" FROM orders ORDER BY "TenantId","Id"')
    digest = hashlib.sha256()
    for raw in rows:
        t, i = int(raw[0]), int(raw[1])
        actual = (t, i, int(raw[2]), None if raw[3] is None else int(raw[3]), int(Decimal(raw[4]) * 100) if provider == "postgresql" else int(raw[4]), raw[5], int(raw[6]), json.loads(raw[7]), raw[8])
        assert actual == order(t, i), (t, i, "order row mismatch")
        digest.update((json.dumps(actual, separators=(",", ":"), sort_keys=True) + "\n").encode())
    lines = db.execute('SELECT "Id","TenantId","OrderId","Product","Quantity" FROM order_lines ORDER BY "Id"')
    expected = []
    line_id = 0
    for t in range(1, TENANTS + 1):
        for i in range(1, ORDERS + 1):
            for line in range(0 if i % 5 == 0 else 1 + i % 3):
                line_id += 1
                expected.append((str(line_id), str(t), str(i), f"product-{(i * 7 + line) % 32:02d}", str(1 + (i + line) % 7)))
    assert lines == expected, "order_lines row mismatch"
    if provider == "sqlite":
        indexes = {}
        for name, (table, fields) in INDEXES.items():
            names = {r[1] for r in db.execute("PRAGMA index_list('" + table + "')")}
            assert name in names, name
            actual = [r[2] for r in db.execute("PRAGMA index_info('" + name + "')")]
            assert actual == fields, (name, actual, fields)
            indexes[name] = actual
        integrity = db.execute("PRAGMA integrity_check")
        assert integrity == [("ok",)], integrity
        version = db.execute("SELECT sqlite_version(),sqlite_source_id()")[0]
        assert version[0] == "3.51.3", version
        settings = {name: db.execute("PRAGMA " + name)[0][0] for name in ["journal_mode", "synchronous", "foreign_keys", "busy_timeout"]}
        detail = {"version": version, "compileOptions": [r[0] for r in db.execute("PRAGMA compile_options")], "settings": settings, "indexes": indexes, "integrityCheck": integrity}
    else:
        indexes = db.execute("SELECT indexname,indexdef FROM pg_indexes WHERE schemaname='public' ORDER BY indexname")
        names = {r[0] for r in indexes}
        assert set(INDEXES).issubset(names)
        for name, (table, fields) in INDEXES.items():
            actual = db.execute("SELECT a.attname FROM pg_index i JOIN pg_class c ON c.oid=i.indexrelid CROSS JOIN LATERAL unnest(i.indkey) WITH ORDINALITY k(attnum,pos) JOIN pg_attribute a ON a.attrelid=i.indrelid AND a.attnum=k.attnum WHERE c.relname='" + name + "' ORDER BY k.pos")
            assert [r[0] for r in actual] == fields, (name, actual, fields)
        version = db.execute("SELECT version(), current_setting('server_version_num')")[0]
        assert version[1] == "180000", version
        detail = {"version": version, "indexes": indexes}
    return {"counts": counts, "schema": schema_observed, "allStoredRowsMatchSeedFormula": True, "normalizedOrdersSha256": digest.hexdigest(), **detail}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--provider", choices=["sqlite", "postgresql"], required=True)
    p.add_argument("--sql-output", type=Path, required=True)
    p.add_argument("--receipt", type=Path, required=True)
    p.add_argument("--sqlite-library", type=Path)
    p.add_argument("--sqlite-database", type=Path)
    p.add_argument("--psql", type=Path)
    p.add_argument("--connection")
    args = p.parse_args()
    assert not args.sql_output.exists(), "Preserve prior SQL; choose a fresh SQL destination"
    assert not args.receipt.exists(), "Preserve prior receipt; choose a fresh destination"
    sql, line_count = generate(args.provider)
    args.sql_output.parent.mkdir(parents=True, exist_ok=True)
    args.sql_output.write_text(sql)
    receipt = {"schemaVersion": 1, "source": SOURCE, "provider": args.provider, "tenants": TENANTS, "ordersPerTenant": ORDERS, "customers": CUSTOMERS, "lines": line_count, "sqlPath": str(args.sql_output.resolve()), "sqlSha256": hashlib.sha256(args.sql_output.read_bytes()).hexdigest(), "scriptSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "startedUnixSeconds": time.time(), "isPressureTest": False}
    db = None
    try:
        if args.provider == "sqlite" and args.sqlite_database:
            assert args.sqlite_library
            assert not args.sqlite_database.exists(), "Refuse to initialize an existing SQLite file"
            args.sqlite_database.parent.mkdir(parents=True, exist_ok=True)
            db = Sqlite(args.sqlite_library, args.sqlite_database)
            db.execute(sql)
            receipt["verification"] = verify(db, args.provider, line_count)
            receipt["librarySha256"] = hashlib.sha256(args.sqlite_library.read_bytes()).hexdigest()
            db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        elif args.provider == "postgresql" and args.connection:
            assert args.psql
            db = Postgres(args.psql, args.connection)
            assert db.execute("SELECT count(*) FROM pg_tables WHERE schemaname='public'") == [("0",)], "Refuse to initialize nonempty PG schema"
            db.initialize(args.sql_output)
            receipt["verification"] = verify(db, args.provider, line_count)
        receipt["status"] = "verified" if "verification" in receipt else "sql_generated_only"
    except Exception as error:
        receipt["status"] = "failed"
        receipt["error"] = {"type": type(error).__name__, "message": str(error)}
        raise
    finally:
        if db:
            db.close()
        receipt["finishedUnixSeconds"] = time.time()
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps(receipt, indent=2))

if __name__ == "__main__":
    main()
