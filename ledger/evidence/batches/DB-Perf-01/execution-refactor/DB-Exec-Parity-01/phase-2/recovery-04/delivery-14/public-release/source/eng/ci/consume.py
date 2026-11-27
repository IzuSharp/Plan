"""Restore only the requested public IDs and execute independent and combined Native AOT applications."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests/Packaging.Domain"))
from consumer_cases import GRAPHS, project
from orm_experience import exercise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--public", action="store_true")
    args = parser.parse_args()
    record = json.loads(args.record.read_text())
    selected = {p["id"]: p["version"] for p in record["packages"]}
    with tempfile.TemporaryDirectory(prefix="korda-public-") as tmp:
        work = Path(tmp)
        conf = ET.parse(ROOT / "NuGet.Config")
        # Keep application packages isolated. NuGet may read SDK tooling from the runner's warm cache.
        sdk_cache = Path(os.environ.get("NUGET_PACKAGES", Path.home() / ".nuget/packages")).resolve()
        if sdk_cache.is_dir():
            fallback = work / "sdk-cache"
            fallback.mkdir()
            for folder in sdk_cache.iterdir():
                if folder.is_dir() and folder.name.lower().startswith(
                    (
                        "microsoft.netcore.app.",
                        "microsoft.aspnetcore.app.",
                        "microsoft.dotnet.",
                        "runtime.linux-x64.microsoft.dotnet.",
                    )
                ):
                    (fallback / folder.name).symlink_to(folder, target_is_directory=True)
            folders = ET.SubElement(conf.getroot(), "fallbackPackageFolders")
            ET.SubElement(folders, "clear")
            ET.SubElement(folders, "add", key="sdk", value=str(fallback))
        if not args.public:
            ET.SubElement(
                conf.find("packageSources"),
                "add",
                key="candidate",
                value=str(args.record.resolve().parent / "feed"),
            )
            local = ET.SubElement(conf.find("packageSourceMapping"), "packageSource", key="candidate")
            for identity in selected:
                ET.SubElement(local, "package", pattern=identity)
        conf.write(work / "NuGet.Config")
        shutil.copy(ROOT / "global.json", work)
        env = os.environ | {"NUGET_PACKAGES": str(work / "cache")}
        for graph, (refs, symbols, providers) in GRAPHS.items():
            if not set(refs).issubset(selected):
                continue
            app = work / graph
            app.mkdir()
            shutil.copy(ROOT / "samples/api/packaging-domain/Program.cs", app)
            project(
                app / "Consumer.csproj",
                refs,
                selected,
                [*symbols, "PUBLIC_PROVIDER_BUNDLE"],
            )

            def run(*argv, extra=None):
                subprocess.run(argv, cwd=app, env=env | (extra or {}), check=True)

            def execute(*command):
                for provider in providers:
                    database = (
                        str(app / "smoke.db") if provider == "sqlite" else os.environ["NW_TEST_POSTGRES"]
                    )
                    run(
                        *command,
                        extra={"B24_PROVIDER": provider, "B24_DATABASE": database},
                    )

            run(
                "dotnet",
                "publish",
                "-c",
                "Release",
                "-r",
                "linux-x64",
                "-p:PublishAot=true",
                "-o",
                "out",
            )
            assets = json.loads((app / "obj/project.assets.json").read_text())
            actual = {key for key in assets["libraries"] if key.lower().startswith("korda.")}
            if actual != {name + "/" + selected[name] for name in refs}:
                raise ValueError("Unexpected Korda dependencies: " + str(actual))
            execute("./out/B24Consumer", "--require-aot")
        exercise(work, selected, env, args.record.resolve().parent / "consumer-evidence" /
                 ("public" if args.public else "candidate"))


if __name__ == "__main__":
    main()
