"""Independent B21 PostgreSQL conflict/commit-acknowledgment oracles.

The proxy changes transport scheduling, never SQL or product results. It records
only protocol/statement categories, backend PIDs and timings, not credentials,
bound values, complete SQL, or PostgreSQL cancellation secrets.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import socket
import struct
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


class OracleFailure(AssertionError):
    """An observed product result or protocol witness violated this oracle."""


def require(condition: bool, description: str) -> None:
    if not condition:
        raise OracleFailure(description)


def _quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _framed_hash(fields: list[str]) -> str:
    # Independent D20 v1 framing; no product assembly or helper is imported.
    data = bytearray(struct.pack("<I", 1))
    for value in fields:
        encoded = value.encode("utf-8", errors="strict")
        data.extend(struct.pack("<I", len(encoded)))
        data.extend(encoded)
    return hashlib.sha256(data).hexdigest()


def _kind(statement: str) -> str:
    text = statement.strip().rstrip(";").strip()
    if re.fullmatch(r"COMMIT(?:\s+WORK)?", text, re.IGNORECASE):
        return "commit"
    if re.match(r"^BEGIN\b", text, re.IGNORECASE):
        return "begin"
    if re.match(r"^ROLLBACK\b", text, re.IGNORECASE):
        return "rollback"
    # SQLx 0.9.0 ColumnResolver resolves prepared-result column origins. This
    # exact catalog-only shape is the sole permitted intervening SQL below.
    # Only the eleven operation columns' numeric OID/attribute pairs vary.
    catalog = " ".join(text.split())
    prefix = ("SELECT attrelid table_oid, attrelid::regclass::text table_name, "
              "array_agg(ROW(attnum, attname)) AS columns FROM (VALUES ")
    suffix = (") lookup(table_oid, attribute_num) INNER JOIN pg_catalog.pg_attribute "
              "ON lookup.table_oid = attrelid AND lookup.attribute_num = attnum GROUP BY attrelid")
    pair = r"\([0-9]{1,10}, [0-9]{1,5}\)"
    if re.fullmatch(re.escape(prefix) + pair + r"(?:, " + pair + r"){0,10}" + re.escape(suffix), catalog):
        return "sqlx_column_metadata"
    if re.match(r'^INSERT\s+INTO\s+(?:"?\w+"?\.)?"?operations"?\b', text, re.IGNORECASE):
        return "operation_insert"
    if re.match(r"^SELECT\b", text, re.IGNORECASE) and re.search(
        r'\bFROM\s+(?:"?\w+"?\.)?"?operations"?\b', text, re.IGNORECASE
    ):
        return "operation_select"
    return "other"


def _cstring(data: bytes, start: int = 0) -> tuple[bytes, int]:
    end = data.find(b"\0", start)
    if end < 0:
        raise OracleFailure("PostgreSQL frontend frame has an unterminated field")
    return data[start:end], end + 1


class _Connection:
    def __init__(self, number: int, client: socket.socket, upstream: socket.socket):
        self.number = number
        self.client = client
        self.upstream = upstream
        self.backend_pid: int | None = None
        self.statements: dict[bytes, tuple[str, str | None]] = {}
        self.portals: dict[bytes, tuple[str, str | None]] = {}
        self.pending: list[tuple[int, str]] = []
        self.operation_transaction = False
        self.suppress = False
        self.commit_confirmed = False
        self.suppressed_frames = 0
        self.closed = threading.Event()

    def close(self) -> None:
        self.closed.set()
        for stream in (self.client, self.upstream):
            try:
                stream.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            stream.close()


class PostgreSqlProxy:
    """Loopback plaintext PG proxy with one explicitly armed commit fault.

    Authentication frames pass transparently. TLS/GSS negotiation is declined on
    this test-only listener; the caller selects the product's explicit local
    database TLS-disable option. Its validated URI must not add sslmode. HTTP
    protocol/TLS profile belongs to the ordinary reference-service launcher.
    """

    MAX_FRAME = 16 * 1024 * 1024

    def __init__(self, database_uri: str, output: Path, timeout: float = 30.0):
        parsed = urlsplit(database_uri)
        require(parsed.scheme in ("postgres", "postgresql"), "A PostgreSQL URI is required")
        require(parsed.hostname is not None, "The PostgreSQL URI needs a TCP host")
        self.upstream_address = (parsed.hostname, parsed.port or 5432)
        self.timeout = timeout
        self.output = Path(output)
        self.output.mkdir(parents=True, exist_ok=True)
        self._log = (self.output / "protocol.jsonl").open("w", encoding="utf-8")
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._connections: list[_Connection] = []
        self._threads: list[threading.Thread] = []
        self.events: list[dict[str, Any]] = []
        self.failures: list[str] = []
        self.mode: str | None = None
        self.selected_connection: int | None = None
        self.selected_command: int | None = None
        self.held = threading.Event()
        self.release = threading.Event()
        self.discarded = threading.Event()
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind(("127.0.0.1", 0))
        self.listener.listen(32)
        self.listener.settimeout(0.2)
        port = self.listener.getsockname()[1]
        credentials = parsed.netloc.rsplit("@", 1)[0] + "@" if "@" in parsed.netloc else ""
        query = [(key, value) for key, value in parse_qsl(parsed.query, keep_blank_values=True)
                 if key.lower() not in ("sslmode", "host", "hostaddr", "port")]
        self.database_uri = urlunsplit((parsed.scheme, f"{credentials}127.0.0.1:{port}",
                                       parsed.path, urlencode(query), ""))

    def __enter__(self) -> PostgreSqlProxy:
        self._spawn(self._accept)
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.release.set()
        self._stop.set()
        self.listener.close()
        with self._lock:
            connections = list(self._connections)
        for connection in connections:
            connection.close()
        deadline = time.monotonic() + 3.0
        for worker in list(self._threads):
            worker.join(max(0.0, deadline - time.monotonic()))
        with self._lock:
            self._log.close()

    def _spawn(self, target: Callable[..., None], *args: Any) -> None:
        worker = threading.Thread(target=target, args=args, daemon=True)
        with self._lock:
            self._threads.append(worker)
        worker.start()

    def _record(self, event: str, connection: _Connection | None = None, **fields: Any) -> int:
        with self._lock:
            sequence = len(self.events) + 1
            value = {"sequence": sequence, "monotonic_ns": time.monotonic_ns(), "event": event,
                     "connection": connection.number if connection else None,
                     "backend_pid": connection.backend_pid if connection else None, **fields}
            self.events.append(value)
            if not self._log.closed:
                self._log.write(json.dumps(value, sort_keys=True) + "\n")
                self._log.flush()
            return sequence

    def arm(self, mode: str) -> None:
        require(mode in ("hold", "discard"), "Unknown PostgreSQL proxy mode")
        with self._lock:
            require(self.mode is None and self.selected_connection is None, "Proxy may be armed only once")
            self.mode = mode
        self._record("armed", mode=mode)

    def _read(self, stream: socket.socket, count: int, connection: _Connection) -> bytes:
        result = bytearray()
        while len(result) < count:
            if self._stop.is_set() or connection.closed.is_set():
                raise EOFError()
            try:
                part = stream.recv(count - len(result))
            except socket.timeout:
                continue
            if not part:
                raise EOFError()
            result.extend(part)
        return bytes(result)

    def _frame(self, stream: socket.socket, connection: _Connection) -> tuple[bytes, bytes, bytes]:
        tag = self._read(stream, 1, connection)
        size_bytes = self._read(stream, 4, connection)
        size = struct.unpack("!I", size_bytes)[0]
        require(4 <= size <= self.MAX_FRAME, "PostgreSQL framed message exceeds the oracle bound")
        payload = self._read(stream, size - 4, connection)
        return tag, payload, tag + size_bytes + payload

    def _accept(self) -> None:
        while not self._stop.is_set():
            try:
                client, _ = self.listener.accept()
            except socket.timeout:
                continue
            except OSError:
                return
            try:
                upstream = socket.create_connection(self.upstream_address, timeout=self.timeout)
                client.settimeout(0.5)
                upstream.settimeout(0.5)
                with self._lock:
                    connection = _Connection(len(self._connections) + 1, client, upstream)
                    self._connections.append(connection)
                self._record("connected", connection)
                self._spawn(self._frontend, connection)
            except OSError:
                client.close()
                with self._lock:
                    self.failures.append("Could not connect the proxy to PostgreSQL")

    def _frontend(self, connection: _Connection) -> None:
        try:
            while True:
                size_bytes = self._read(connection.client, 4, connection)
                size = struct.unpack("!I", size_bytes)[0]
                require(8 <= size <= self.MAX_FRAME, "PostgreSQL startup message exceeds the oracle bound")
                data = self._read(connection.client, size - 4, connection)
                code = struct.unpack("!I", data[:4])[0]
                if code in (80877103, 80877104):  # SSLRequest / GSSENCRequest.
                    connection.client.sendall(b"N")
                    self._record("test_transport_encryption_declined", connection)
                    continue
                connection.upstream.sendall(size_bytes + data)
                if code == 80877102:  # CancelRequest is an unframed one-shot connection.
                    self._record("cancel_forwarded", connection)
                    return
                require(code == 196608, "Only PostgreSQL protocol version 3 is supported by the oracle")
                break
            self._spawn(self._backend, connection)
            while True:
                tag, payload, frame = self._frame(connection.client, connection)
                command_kind: str | None = None
                statement_sha256: str | None = None
                if tag == b"P":
                    name, offset = _cstring(payload)
                    statement, _ = _cstring(payload, offset)
                    kind = _kind(statement.decode("utf-8", errors="strict"))
                    fingerprint = hashlib.sha256(statement).hexdigest() if kind == "sqlx_column_metadata" else None
                    connection.statements[name] = (kind, fingerprint)
                elif tag == b"B":
                    portal, offset = _cstring(payload)
                    statement, _ = _cstring(payload, offset)
                    connection.portals[portal] = connection.statements.get(statement, ("other", None))
                elif tag == b"E":
                    portal, _ = _cstring(payload)
                    command_kind, statement_sha256 = connection.portals.get(portal, ("other", None))
                elif tag == b"Q":
                    statement, _ = _cstring(payload)
                    command_kind = _kind(statement.decode("utf-8", errors="strict"))
                    if command_kind == "sqlx_column_metadata":
                        statement_sha256 = hashlib.sha256(statement).hexdigest()
                if command_kind is not None:
                    self._before_command(connection, command_kind, statement_sha256)
                connection.upstream.sendall(frame)
                if tag == b"X":
                    return
        except (EOFError, ConnectionError, OSError):
            pass  # An actual disconnected endpoint is recorded by the outcome oracle.
        except Exception as error:
            self._failure(connection, error)
        finally:
            connection.close()

    def _before_command(self, connection: _Connection, kind: str, statement_sha256: str | None) -> None:
        with self._lock:
            fields = {"statement_sha256": statement_sha256} if statement_sha256 is not None else {}
            sequence = self._record("command", connection, kind=kind, **fields)
            connection.pending.append((sequence, kind))
            if kind == "operation_insert":
                connection.operation_transaction = True
            selected = (kind == "commit" and connection.operation_transaction and self.mode is not None
                        and self.selected_connection is None)
            if selected:
                self.selected_connection = connection.number
                self.selected_command = sequence
                mode = self.mode
                if mode == "discard":
                    connection.suppress = True
                    self._record("commit_forwarded_ack_suppressed", connection, command_sequence=sequence)
            else:
                mode = None
        if mode == "hold":
            self._record("commit_held_before_upstream", connection, command_sequence=sequence)
            self.held.set()
            require(self.release.wait(self.timeout), "The held COMMIT was not released before the oracle deadline")
            self._record("commit_released_to_upstream", connection, command_sequence=sequence)

    def _backend(self, connection: _Connection) -> None:
        try:
            while True:
                tag, payload, frame = self._frame(connection.upstream, connection)
                if tag == b"K":
                    require(len(payload) == 8, "Unexpected PostgreSQL backend-key frame")
                    connection.backend_pid = struct.unpack("!I", payload[:4])[0]
                    self._record("backend_identity", connection)
                if tag == b"C":
                    completion = payload.rstrip(b"\0").decode("ascii", errors="strict")
                    with self._lock:
                        sequence, kind = connection.pending.pop(0) if connection.pending else (None, "other")
                    self._record("command_complete", connection, kind=kind, command_sequence=sequence,
                                 completion=completion, discarded=connection.suppress)
                    if connection.suppress and completion == "COMMIT":
                        connection.commit_confirmed = True
                elif tag == b"E":
                    with self._lock:
                        sequence, kind = connection.pending.pop(0) if connection.pending else (None, "other")
                    # Provider error fields can contain user values; preserve only its occurrence.
                    self._record("provider_error", connection, kind=kind, command_sequence=sequence,
                                 discarded=connection.suppress)
                if connection.suppress:
                    connection.suppressed_frames += 1
                    if tag == b"Z":
                        require(connection.commit_confirmed and payload == b"I",
                                "Discard mode did not observe COMMIT followed by idle ReadyForQuery")
                        self._record("commit_ack_discarded", connection, transaction_status="I",
                                     suppressed_frames=connection.suppressed_frames,
                                     command_sequence=self.selected_command)
                        self.discarded.set()
                        return
                    continue
                connection.client.sendall(frame)
                if tag == b"Z":
                    require(payload in (b"I", b"T", b"E"), "Unknown PostgreSQL transaction status")
                    self._record("ready", connection, transaction_status=payload.decode("ascii"))
                    if payload == b"I":
                        connection.operation_transaction = False
        except (EOFError, ConnectionError, OSError):
            pass
        except Exception as error:
            self._failure(connection, error)
        finally:
            connection.close()

    def _failure(self, connection: _Connection, error: Exception) -> None:
        message = str(error) if isinstance(error, OracleFailure) else type(error).__name__
        with self._lock:
            self.failures.append(message)
        self._record("proxy_failure", connection, reason=message)

    def snapshot(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self.events)

    def selected_pid(self) -> int:
        with self._lock:
            values = [c.backend_pid for c in self._connections if c.number == self.selected_connection]
        require(len(values) == 1 and values[0] is not None, "The selected COMMIT lacks a backend PID witness")
        return int(values[0])


class _Request:
    def __init__(self, action: Callable[[], tuple[int, bytes, dict[str, Any]]]):
        self.done = threading.Event()
        self.value: tuple[int, bytes, dict[str, Any]] | None = None
        self.error: BaseException | None = None

        def run() -> None:
            try:
                self.value = action()
            except BaseException as error:
                self.error = error
            finally:
                self.done.set()

        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

    def result(self, timeout: float) -> tuple[int, bytes, dict[str, Any]]:
        require(self.done.wait(timeout), "The HTTP request exceeded the PG oracle deadline")
        if self.error is not None:
            raise self.error
        require(self.value is not None, "The HTTP request produced no result")
        return self.value  # type: ignore[return-value]


def _write_result(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _durable(sql: Callable[[str], list[tuple[str | None, ...]]], principal: dict[str, Any],
             key: str, title: str, response: bytes | None = None,
             operation_id: str | None = None) -> dict[str, Any]:
    semantic = "POST /v1/items"
    tenant, actor = principal["tenant"], principal["principal"]
    scope = _framed_hash(["scope.v1", tenant, actor, semantic])
    request_hash = _framed_hash([semantic, tenant, actor, title])
    rows = sql(
        "SELECT o.operation_id,o.tenant_id,o.principal_id,o.request_key,o.request_hash,"
        "o.response_status::text,encode(o.response_bytes,'hex'),o.response_version::text,"
        "(SELECT count(*) FROM items i WHERE i.operation_id=o.operation_id)::text,"
        "(SELECT count(*) FROM outbox x WHERE x.operation_id=o.operation_id)::text,"
        "(SELECT i.item_id FROM items i WHERE i.operation_id=o.operation_id),"
        "(SELECT i.title FROM items i WHERE i.operation_id=o.operation_id) "
        f"FROM operations o WHERE o.scope={_quote(scope)} AND o.request_key={_quote(key)}"
    )
    require(len(rows) == 1, "Independent SQL did not observe exactly one scoped operation")
    row = rows[0]
    require(len(row) == 12, "Independent SQL returned an unexpected operation shape")
    require(tuple(row[1:6]) == (tenant, actor, key, request_hash, "201"),
            "Durable scope, request hash, key or replay status differs from the request")
    require(tuple(row[7:10]) == ("1", "1", "1"), "Operation, item and outbox effects are not atomic singletons")
    require(row[11] == title, "The independently observed item payload differs")
    stored = bytes.fromhex(str(row[6]))
    document = json.loads(stored)
    require(document.get("operationId") == row[0] and document.get("itemId") == row[10],
            "Stored replay identities disagree with independent durable rows")
    if response is not None:
        require(response == stored, "The HTTP response differs from the durable versioned replay bytes")
    if operation_id is not None:
        require(operation_id == row[0], "The Unknown recovery identity differs from the committed operation")
    return {"operation_id": row[0], "item_id": row[10], "operation_count": 1,
            "item_count": 1, "outbox_count": 1, "request_hash": request_hash,
            "response_sha256": hashlib.sha256(stored).hexdigest(), "response_hex": stored.hex()}


def _conflict(command: list[str], config: dict[str, Any], output: Path,
              service_factory: Callable[[dict[str, Any], Path], Any],
              sql: Callable[[str], list[tuple[str | None, ...]]], principal: dict[str, Any]) -> dict[str, Any]:
    del command  # The caller owns exact program/artifact provenance in its normal runner receipt.
    key = "b21-conflict-" + uuid.uuid4().hex
    title = "B21 concurrent PostgreSQL snapshot " + key
    body = json.dumps({"title": title}, separators=(",", ":")).encode()
    with PostgreSqlProxy(config["database"], output) as proxy:
        overrides = copy.deepcopy(config)
        overrides.update(database=proxy.database_uri, allowLocalDatabaseTlsDisable=True)
        with service_factory(overrides, output / "service") as service:
            proxy.arm("hold")
            send = lambda: service.request("POST", "/v1/items", body=body,
                                           headers={"Content-Type": "application/json", "Idempotency-Key": key},
                                           token=principal["token"])
            winner = _Request(send)
            try:
                require(proxy.held.wait(proxy.timeout), "The winning product request never reached a held COMMIT")
                winner_pid = proxy.selected_pid()
                loser = _Request(send)
                deadline = time.monotonic() + proxy.timeout
                witness: tuple[str | None, ...] | None = None
                while time.monotonic() < deadline:
                    candidates = sorted({event["backend_pid"] for event in proxy.snapshot()
                                         if event["event"] == "command" and event.get("kind") == "operation_insert"
                                         and event["connection"] != proxy.selected_connection
                                         and event["backend_pid"] is not None})
                    if candidates:
                        pids = ",".join(str(pid) for pid in candidates)
                        rows = sql("SELECT a.pid::text,a.wait_event_type,a.wait_event "
                                   f"FROM pg_stat_activity a WHERE a.pid IN ({pids}) "
                                   f"AND {winner_pid}=ANY(pg_blocking_pids(a.pid)) "
                                   "AND a.wait_event_type='Lock' AND EXISTS "
                                   "(SELECT 1 FROM pg_locks l WHERE l.pid=a.pid AND NOT l.granted)")
                        if rows:
                            require(len(rows) == 1, "More than one contender is blocked by the held winner")
                            witness = rows[0]
                            break
                    time.sleep(0.01)
                require(witness is not None, "No actual PostgreSQL lock wait established the conflict snapshot")
                require(not winner.done.is_set() and not loser.done.is_set(),
                        "A product response completed while the conflicting transaction was still held")
                proxy._record("independent_lock_wait", loser_backend_pid=int(witness[0]),
                              winner_backend_pid=winner_pid, wait_type=witness[1], wait_event=witness[2])
                proxy.release.set()
                first, second = winner.result(proxy.timeout), loser.result(proxy.timeout)
                require(first[0] == second[0] == 201, "Concurrent same-key product requests did not both return replay status 201")
                require(first[1] == second[1], "Concurrent same-key requests returned different stable bytes")
                durable = _durable(sql, principal, key, title, first[1])
                events = proxy.snapshot()
                loser_pid = int(witness[0])
                insert = [event for event in events if event["event"] == "command_complete"
                          and event["backend_pid"] == loser_pid and event.get("kind") == "operation_insert"]
                require(len(insert) == 1 and insert[0]["completion"] == "INSERT 0 0",
                        "The contender did not observe the actual DO NOTHING zero-row result")
                following = [event for event in events if event["event"] == "command"
                             and event["backend_pid"] == loser_pid and event["sequence"] > insert[0]["command_sequence"]]
                # Start at INSERT dispatch, not its completion: a pipelined
                # command sent while that INSERT waits must remain observable.
                # Preparing FindAsync can cause the pinned SQLx driver to load
                # column origins from pg_catalog. It carries no business-table
                # read/write and cannot reuse the INSERT's statement snapshot.
                controls = []
                while following and following[0].get("kind") == "sqlx_column_metadata":
                    controls.append(following.pop(0))
                require(len(controls) <= 1, "Unexpected repeated SQLx metadata queries before the recovery SELECT")
                require(bool(following) and following[0].get("kind") == "operation_select",
                        "The zero-row INSERT was not followed by a separate operations SELECT")
                selected = [event for event in events if event["event"] == "command_complete"
                            and event.get("command_sequence") == following[0]["sequence"]]
                require(len(selected) == 1 and selected[0]["completion"] == "SELECT 1",
                        "The next statement did not recover exactly one winning operation")
                require(not proxy.failures, "The PostgreSQL proxy recorded a framing failure")
                return {"passed": True, "key": key, "winner_pid": winner_pid,
                        "loser_pid": loser_pid, "lock_wait": list(witness),
                        "separate_select": True,
                        "sqlx_metadata_query_count_before_select": len(controls),
                        "sqlx_metadata_before_select": [{"sequence": item["sequence"],
                                                         "statement_sha256": item["statement_sha256"]}
                                                        for item in controls],
                        "durable": durable}
            finally:
                proxy.release.set()


def _unknown(command: list[str], config: dict[str, Any], output: Path,
             service_factory: Callable[[dict[str, Any], Path], Any],
             sql: Callable[[str], list[tuple[str | None, ...]]], principal: dict[str, Any]) -> dict[str, Any]:
    del command
    key = "b21-unknown-" + uuid.uuid4().hex
    title = "B21 discarded PostgreSQL COMMIT acknowledgement " + key
    body = json.dumps({"title": title}, separators=(",", ":")).encode()
    with PostgreSqlProxy(config["database"], output) as proxy:
        overrides = copy.deepcopy(config)
        overrides.update(database=proxy.database_uri, allowLocalDatabaseTlsDisable=True)
        with service_factory(overrides, output / "service") as service:
            proxy.arm("discard")
            response = service.request("POST", "/v1/items", body=body,
                                       headers={"Content-Type": "application/json", "Idempotency-Key": key},
                                       token=principal["token"])
            require(proxy.discarded.wait(proxy.timeout), "No real COMMIT/idle reply was discarded")
            require(response[0] == 503, "Lost COMMIT acknowledgment did not produce HTTP 503")
            problem = json.loads(response[1])
            require(problem.get("code") == "outcome_unknown", "Lost COMMIT acknowledgment was relabeled as a known outcome")
            operation_id = problem.get("operationId")
            require(isinstance(operation_id, str) and str(uuid.UUID(operation_id)) == operation_id,
                    "Unknown did not retain a canonical recovery identity")
            recovery_uri = "/v1/operations/" + operation_id
            require(problem.get("recoveryUri") == recovery_uri, "Unknown recovery URI is not identity-bound")
            durable = _durable(sql, principal, key, title, operation_id=operation_id)
            recovered = service.request("GET", recovery_uri, token=principal["token"])
            require(recovered[0] == 200 and recovered[1].hex() == durable["response_hex"],
                    "Authorized recovery did not return the durable original result")
            replay = service.request("POST", "/v1/items", body=body,
                                     headers={"Content-Type": "application/json", "Idempotency-Key": key},
                                     token=principal["token"])
            require(replay[0] == 201 and replay[1] == recovered[1],
                    "Protected same-key recovery did not replay the confirmed original response")
            after = _durable(sql, principal, key, title, replay[1], operation_id)
            require(after == durable, "Protected replay changed the winning operation/item/outbox effect")
            require(not proxy.failures, "The PostgreSQL proxy recorded a framing failure")
            return {"passed": True, "key": key, "unknown_http_status": response[0],
                    "unknown_code": problem["code"], "operation_id": operation_id,
                    "backend_pid": proxy.selected_pid(), "commit_then_idle_discarded": True,
                    "authorized_recovery": True, "protected_same_key_replay": True, "durable": durable}


def run_postgres_oracles(command: list[str], config: dict[str, Any], output: Path,
                         service_factory: Callable[[dict[str, Any], Path], Any],
                         sql: Callable[[str], list[tuple[str | None, ...]]]) -> dict[str, Any]:
    """Run two new-product B21 oracles; failures persist and propagate.

    service_factory(config, output) is a context manager yielding an object with
    request(method, path, body=None, headers=None, token=None) -> (status, bytes,
    headers). Each call must use an independent HTTP client, so the two conflict
    requests can run concurrently. sql(statement) uses independent direct psql
    and returns text/NULL tuples, never through this proxy or the product API.
    """
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    require(config.get("provider") == "postgresql", "These B21 oracles require the PostgreSQL provider")
    principals = [entry for entry in config.get("principals", []) if entry.get("canWrite") is True]
    require(bool(principals), "The oracle needs one configured writable principal")
    principal = principals[0]
    result: dict[str, Any] = {"schema_version": 1, "task": "B21", "platform": "linux-x64",
                              "scope": "real PostgreSQL conflict snapshot and discarded COMMIT acknowledgment",
                              "passed": False, "cases": {}}
    try:
        for name, action in (("conflict_snapshot", _conflict), ("commit_ack_loss", _unknown)):
            result["active_case"] = name
            _write_result(output / "result.json", result)
            result["cases"][name] = action(command, config, output / name, service_factory, sql, principal)
            _write_result(output / "result.json", result)
        result["active_case"] = None
        result["passed"] = True
        return result
    except Exception as error:
        result["failure_type"] = type(error).__name__
        result["failure"] = str(error) if isinstance(error, OracleFailure) else "External launcher, HTTP or SQL call failed; see caller-owned logs"
        raise
    finally:
        _write_result(output / "result.json", result)
