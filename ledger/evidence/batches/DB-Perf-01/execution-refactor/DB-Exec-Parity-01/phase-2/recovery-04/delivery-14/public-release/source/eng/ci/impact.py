"""Plan module checks and package candidates from two Git trees."""

import argparse
import json
import posixpath
import xml.etree.ElementTree as ET
from pathlib import Path

from catalog import DIRECTORY, git, load_catalog
from registry import next_preview, public_heads

from facts import IDS as IDS, PROVIDERS, files, fingerprints, inputs as inputs
from language import language, purpose
from database_plan import plan_actions


def changed_paths(base, tree):
    diff = git("diff", "--no-renames", "--name-only", "-z", base, tree)
    return [p.decode() for p in diff.split(b"\0") if p]


def solution_projects(path, entry):
    """Separate project membership from solution-wide build settings."""
    if entry is None:
        return {}, ""
    blob = entry.split(b"\t", 1)[0].split()[-1].decode()
    root = ET.fromstring(git("cat-file", "blob", blob))
    projects = {}
    for parent in root.iter():
        for project in list(parent.findall("Project")):
            name = posixpath.normpath(posixpath.join(posixpath.dirname(path), project.attrib["Path"]))
            projects[name] = ET.tostring(project, encoding="unicode").strip()
            parent.remove(project)
    for folder in list(root.findall("Folder")):
        if not len(folder):
            root.remove(folder)
    return projects, ET.canonicalize(ET.tostring(root, encoding="unicode"), strip_text=True)


def classify(paths, catalog, entries, previous):
    direct, affected_packages, affected_modules, reasons = set(), set(), set(), {}
    owners, payload_changes, product_changes = set(), set(), set()
    for path in paths:
        graph = catalog if path in entries else previous
        module, kind = graph.owner(path)
        role = purpose(path, kind)
        reasons.setdefault(module, []).append(path)
        if role == "documentation":
            continue
        if role == "metadata":
            affected_packages.update(graph.consumers({module}) & catalog.packages.keys())
            continue
        if module in catalog.modules:
            direct.add(module)
        if role == "sources":
            if module in catalog.modules:
                owners.add(module)
            consumers = graph.consumers({module})
            affected_modules.update(consumers & catalog.modules.keys())
            packages = consumers & catalog.packages.keys()
            affected_packages.update(packages)
            payload_changes.update(packages)
            if "bundle.check" not in graph.modules[module].get("checks", ()):
                product_changes.update(packages)
    # A manifest is also an input to routing. Test a changed command, and account for
    # added/removed dependencies even if no source file moved in the same commit.
    if previous is not catalog:
        for name, spec in catalog.modules.items():
            old = previous.modules.get(name, {})
            if any(spec.get(k) != old.get(k) for k in ("run", "integration", "pack", "consume", "includes")):
                direct.add(name)
    # An aggregate source edit exercises its own included components. A test-only
    # edit, or an edit in one of its children, does not pull in its siblings.
    for owner in owners:
        for child in catalog.modules[owner].get("includes", []):
            affected_modules.update(catalog.dependencies(child))
    return direct, affected_modules, affected_packages, payload_changes, product_changes, reasons


def make_plan(
    catalog,
    paths,
    entries,
    previous,
    full=False,
    old_entries=None,
    *,
    images=False,
    reconcile=False,
):
    direct, consumers, touched, payload_changes, product_changes, reasons = classify(
        paths, catalog, entries, previous
    )
    if old_entries is not None:
        # The solution is an index shared by otherwise independent products.
        for path in (p for p in paths if p.endswith(".slnx")):
            old, old_settings = solution_projects(path, old_entries.get(path))
            new, settings = solution_projects(path, entries.get(path))
            for project in old.keys() | new.keys():
                if settings != old_settings or old.get(project) != new.get(project):
                    graph = catalog if project in entries else previous
                    owner, _ = graph.owner(project)
                    if owner in catalog.modules:
                        direct.add(owner)
    hashes = fingerprints(catalog, entries)
    payloads = fingerprints(catalog, entries, include_metadata=False)
    if old_entries is not None and previous is not catalog:
        # Recompute impact when registered dependency edges or packaging recipes changed.
        old_hashes = fingerprints(previous, old_entries)
        touched.update(name for name in catalog.packages if old_hashes.get(name) != hashes[name])
        old_payloads = fingerprints(previous, old_entries, include_metadata=False)
        payload_changes.update(p for p in touched if old_payloads.get(p) != payloads[p])
    db = set(PROVIDERS) & catalog.packages.keys()
    # Ordinary diffs select checks. Main also checks each ID for a missing or stale preview.
    published = public_heads(catalog.packages) if reconcile else {}
    pending = {p for p in catalog.packages if published[p]["inputs"] != hashes[p]} if reconcile else set()
    # A metadata-only merge can also deliver an earlier, unshipped binary change.
    payload_changes.update(p for p in pending if published[p].get("payload_inputs") != payloads[p])
    package_checks = set(touched) | pending
    selected = set(catalog.modules) if full else direct | consumers
    result = plan_actions(
        catalog,
        reasons,
        direct,
        product_changes & db,
        package_checks & db,
        payload_changes & db,
        previous=previous,
        entries=entries,
        full=full,
        images=images,
    )
    # A first or missed release may have no changed files in this push. Build any
    # registered internal artifacts needed to package it in this run.
    for name in pending - db:
        selected.update(m for m in catalog.dependencies(name) if catalog.modules[m].get("artifacts"))
    run_steps = {}
    for name in selected:
        spec = catalog.modules[name]
        step = "run" if name in direct or full or "package" not in spec else "integration"
        if spec.get(step):
            run_steps[name] = step
    modules = sorted(run_steps)
    changed_languages = sorted({language(p) for p in paths})
    languages = set(changed_languages) & {"python", "csharp"}
    if full or ".github/workflows/security.yml" in paths:
        languages.update(("python", "csharp"))
    releases = [{"module": p, "database": p in db} for p in sorted(pending)]
    validate_packages = set(catalog.packages) if full else package_checks | (direct & catalog.packages.keys())
    module_packages = sorted(validate_packages - db)
    return dict(
        result,
        changed_languages=changed_languages,
        inputs=hashes,
        payload_inputs={p: payloads[p] for p in sorted(db)},
        packages=sorted(package_checks & db),
        candidates=sorted(pending),
        versions={
            p: next_preview(published[p]["version"]) if p in pending else "0.1.0-ci.1"
            for p in sorted(catalog.packages)
        },
        releases=releases,
        modules=modules,
        run_steps=run_steps,
        languages=sorted(languages),
        artifacts={n: catalog.modules[n]["artifacts"] for n in modules if "artifacts" in catalog.modules[n]},
        module_packages=module_packages,
        reasons=reasons,
        module_resources={n: catalog.resources(n) for n in set(modules) | set(module_packages)},
        compose_from={
            p: sorted(
                n for n in catalog.dependencies(p) & set(modules) if catalog.modules[n].get("artifacts")
            )
            for p in module_packages
        },
    )


def plan_tree(base, tree="HEAD", *, replay=None, full=False, images=False, reconcile=False):
    paths = changed_paths(base, tree) if replay is None else replay
    catalog = load_catalog(tree)
    previous = catalog
    old_files = files(base)
    has_registry = any(p.startswith(DIRECTORY + "/") for p in old_files)
    if has_registry and any(p.startswith(DIRECTORY + "/") or p.endswith(".csproj") for p in paths):
        previous = load_catalog(base, historical=True)
    entries = files(tree)
    if replay is not None:
        for p in replay:
            if p not in entries or catalog.owner(p)[1] != "tests":
                raise ValueError("Replay accepts tracked test or documentation paths only: " + p)
    return make_plan(
        catalog,
        paths,
        entries,
        previous,
        full,
        old_files,
        images=images,
        reconcile=reconcile,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base")
    parser.add_argument("--tree", default="HEAD")
    parser.add_argument("--full", action="store_true")
    parser.add_argument(
        "--images",
        action="store_true",
        help="Include clean images and CPU emulation in a full run",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = json.dumps(
        plan_tree(args.base, args.tree, full=args.full, images=args.images),
        indent=2,
        sort_keys=True,
    )
    print(data)
    if args.output:
        args.output.parent.mkdir(exist_ok=True, parents=True)
        args.output.write_text(data + "\n")


if __name__ == "__main__":
    main()
