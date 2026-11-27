"""Read published provider versions from the official NuGet flat container."""

import io
import json
import re
import time
import zipfile
from pathlib import Path
import os
import sys
from urllib.error import HTTPError
from urllib.request import urlopen


def read(url):
    for attempt in range(3):
        try:
            with urlopen(url, timeout=40) as response:
                return response.read()
        except OSError as error:
            if isinstance(error, HTTPError) and error.code == 404 or attempt == 2:
                raise
            time.sleep(2**attempt)


def package(identity, version):
    name = identity.lower()
    return read(f"https://api.nuget.org/v3-flatcontainer/{name}/{version}/{name}.{version}.nupkg")


# The second numeric component was used by the pre-migration build workflow.
PREVIEW = re.compile(r"0\.1\.0-preview\.([1-9][0-9]*)(?:\.([0-9]+))?")


def next_preview(previous):
    number = int(PREVIEW.fullmatch(previous)[1]) if previous else 0
    return f"0.1.0-preview.{number + 1}"


def public_heads(identities):
    heads = {}
    for provider, identity in identities.items():
        url = f"https://api.nuget.org/v3-flatcontainer/{identity.lower()}/index.json"
        try:
            versions = json.loads(read(url))["versions"]
        except HTTPError as exc:
            if exc.code != 404:
                raise
            versions = []
        releases = [v for v in versions if PREVIEW.fullmatch(v)]
        if not releases:
            heads[provider] = {"version": None, "inputs": None}
            continue
        version = max(
            releases,
            key=lambda v: tuple(int(n or 0) for n in PREVIEW.fullmatch(v).groups()),
        )
        with zipfile.ZipFile(io.BytesIO(package(identity, version))) as archive:
            info = (
                json.loads(archive.read("korda/public.json"))
                if "korda/public.json" in archive.namelist()
                else {}
            )
        heads[provider] = {"version": version, "inputs": info.get("inputs")}
        if "payload_inputs" in info:
            heads[provider]["payload_inputs"] = info["payload_inputs"]
    return heads


def publication_state(module, latest, plan):
    from facts import inputs
    from catalog import load_catalog

    wanted = plan["inputs"][module]
    if inputs(latest).get(module) != wanted:
        # An older push (or rerun) must never roll back a newer package.
        return False, False
    identity = load_catalog().packages[module]
    head = public_heads({module: identity})[module]
    version = plan["versions"][module]
    if head["inputs"] == wanted:
        return False, head["version"] == version
    if next_preview(head["version"]) != version:
        raise ValueError(f"{identity}: registry advanced since planning {version}")
    return True, True


if __name__ == "__main__":
    if len(sys.argv) != 5 or sys.argv[1] != "--publish-current":
        sys.exit("Expected --publish-current MODULE LATEST_SHA PLAN")
    publish, verify = publication_state(sys.argv[2], sys.argv[3], json.loads(Path(sys.argv[4]).read_text()))
    with open(os.environ["GITHUB_OUTPUT"], "a") as out:
        print("publish=" + str(publish).lower(), file=out)
        print("verify=" + str(verify).lower(), file=out)
    print(f"{sys.argv[2]}: publish={publish}, verify={verify}")
