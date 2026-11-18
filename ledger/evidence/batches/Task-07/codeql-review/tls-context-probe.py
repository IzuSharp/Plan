#!/usr/bin/env python3
"""Read SSL policy without opening sockets or loading a private key."""
import hashlib
import inspect
import json
from pathlib import Path
import ssl
import _ssl
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


events = []


def forbid_socket(event, arguments):
    if event.startswith("socket."):
        events.append(event)
        raise RuntimeError("The policy probe permits no socket operations")


sys.addaudithook(forbid_socket)
certificate = Path(sys.argv[1]).resolve()
extension_path = getattr(_ssl, "__file__", None)
observations = []
for alpn in (None, ["h2"]):
    context = ssl.create_default_context(cafile=str(certificate))
    if alpn:
        context.set_alpn_protocols(alpn)
    observations.append({
        "constructor": "ssl.create_default_context(cafile=certificate)",
        "alpn": alpn,
        "protocol": context.protocol.name,
        "minimumVersion": context.minimum_version.name,
        "minimumVersionValue": int(context.minimum_version),
        "maximumVersion": context.maximum_version.name,
        "verifyMode": context.verify_mode.name,
        "checkHostname": context.check_hostname,
        "options": hex(context.options),
        "securityLevel": context.security_level,
        "certificateStore": context.cert_store_stats(),
        "cipherProtocolLabels": sorted({item["protocol"] for item in context.get_ciphers()}),
        "allowsTLSv1ByVersionRange": context.minimum_version <= ssl.TLSVersion.TLSv1,
        "allowsTLSv1_1ByVersionRange": context.minimum_version <= ssl.TLSVersion.TLSv1_1,
    })
    assert context.minimum_version >= ssl.TLSVersion.TLSv1_2
    assert context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname

print(json.dumps({
    "schemaVersion": 1,
    "kind": "source-and-in-memory-policy-observation",
    "networkHandshakePerformed": False,
    "privateKeyRead": False,
    "socketAuditEvents": events,
    "python": {
        "version": sys.version,
        "executable": str(Path(sys.executable).resolve()),
        "executableSha256": sha(Path(sys.executable).resolve()),
    },
    "opensslVersion": ssl.OPENSSL_VERSION,
    "sslModule": {"path": ssl.__file__, "sha256": sha(ssl.__file__)},
    "sslExtension": {
        "origin": _ssl.__spec__.origin,
        "path": extension_path,
        "sha256": sha(extension_path) if extension_path else None,
        "note": "A built-in module has no independent file to hash." if not extension_path else None,
    },
    "createDefaultContextSource": inspect.getsource(ssl.create_default_context),
    "certificate": {"path": str(certificate), "sha256": sha(certificate)},
    "observations": observations,
}, indent=2))
