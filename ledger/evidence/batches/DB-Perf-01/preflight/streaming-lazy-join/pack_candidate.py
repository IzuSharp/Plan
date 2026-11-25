#!/usr/bin/env python3
"""Compose an experimental managed-only candidate with verified original native bytes.

This calls the repository's public bundle composer and closure validator. It does
not publish. The native producer receipt and every original unsigned package entry
are checked before reuse; all native/profile source inputs must still match.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'eng/ci'))
import bundles
from facts import files, fingerprints
from catalog import load_catalog


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--dotnet', type=Path, required=True)
    parser.add_argument('--packages', type=Path, required=True)
    parser.add_argument('--version', required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    tree = subprocess.check_output(['git', 'rev-parse', 'HEAD^{tree}'], cwd=ROOT, text=True).strip()
    scopes = ['src', 'native', 'eng/ci', 'Directory.Build.props', 'global.json', 'CMakeLists.txt', 'CMakePresets.json']
    if subprocess.check_output(['git', 'diff', 'HEAD', '--', *scopes], cwd=ROOT):
        raise ValueError('Tracked package inputs differ from the committed producer')
    catalog = load_catalog('HEAD')
    entries_at_head = files('HEAD')
    inputs = fingerprints(catalog, entries_at_head)
    payloads = fingerprints(catalog, entries_at_head, include_metadata=False)
    source_paths = subprocess.check_output(['git', 'ls-files', '-z', '--', *scopes], cwd=ROOT).decode().split('\0')
    source_hashes = {path: digest((ROOT/path).read_bytes()) for path in source_paths if path}
    env = os.environ.copy()
    env.update(DOTNET_CLI_TELEMETRY_OPTOUT='1', DOTNET_CLI_USE_MSBUILD_SERVER='0', MSBUILDDISABLENODEREUSE='1',
               NUGET_PACKAGES=str(args.packages.resolve()))
    records = []

    def run(label, argv):
        path = args.output / (label + '.log')
        with path.open('wb') as log:
            result = subprocess.run([str(x) for x in argv], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        records.append(dict(label=label, argv=[str(x) for x in argv], exit_code=result.returncode, log=path.name, sha256=digest(path.read_bytes())))
        (args.output/'commands.json').write_text(json.dumps(records,indent=2)+'\n')
        print(label, result.returncode, flush=True)
        if result.returncode:
            raise RuntimeError(path.read_text()[-8000:])

    def compile_project(project, version, extra=()):
        label = Path(project).stem
        flags = ['-m:1', '-nr:false', '-p:UseSharedCompilation=false', *extra]
        run(label+'-restore', [args.dotnet,'restore',project,'--locked-mode',*flags])
        run(label+'-build', [args.dotnet,'build',project,'-c','Release','--no-restore',f'-p:Version={version}',*flags])

    compile_project(bundles.TASK_PROJECT,args.version)
    receipts = []
    for provider in ('postgresql','sqlite'):
        base = args.baseline/provider
        release = json.loads((base/'release.json').read_text())
        if release['source_commit'] != '771bc77cbd68d3f932b99ed2497c0697bbba5f02' or release['source_dirty']:
            raise ValueError('Wrong fixed original candidate producer')
        old = release['packages'][0]
        package = base/'feed'/f"{old['id']}.{old['version']}.nupkg"
        if digest(package.read_bytes()) != old['upload_archive_sha256']:
            raise ValueError('Original candidate archive hash differs')
        with zipfile.ZipFile(package) as archive:
            original = {name: archive.read(name) for name in archive.namelist() if not name.endswith('/')}
        actual = {name:digest(data) for name,data in original.items() if name not in ('.signature.p7s',)}
        expected = old['unsigned_entries']
        if isinstance(expected,list):
            expected = {item['path']:item['sha256'] for item in expected}
        if actual != expected:
            raise ValueError('Original candidate member inventory differs')
        native_inventory = json.loads(original['korda/dependencies.json'])
        for name, expected_hash in native_inventory['inputSha256'].items():
            if digest((ROOT/name).read_bytes()) != expected_hash:
                raise ValueError('Native input changed; rebuilding required: '+name)
        native_name = old['native']['path']
        native_bytes = original[native_name]
        if digest(native_bytes) != old['native']['sha256']:
            raise ValueError('Original native hash differs')
        native_path = args.output/provider/Path(native_name).name
        native_path.parent.mkdir(parents=True)
        native_path.write_bytes(native_bytes)
        prop = 'KordaSqliteAssetPath' if provider=='sqlite' else 'KordaPostgresAssetPath'
        identity = bundles.IDS[provider]
        compile_project(bundles.managed_project(identity),args.version,[f'-p:{prop}={native_path.resolve()}'])
        selected = {name:data for name,data in original.items() if name.startswith('korda/licenses/') or name in ('NOTICE','korda/dependencies.json','korda/manifest.json',native_name)}
        for component in sorted((set(bundles.MANAGED)-set(bundles.IDS.values()))|{identity}):
            for name,path in bundles.managed_entries(component).items():
                if name.startswith(('lib/','tools/')):
                    selected[name]=path.read_bytes()
        for suffix in ('.dll','.xml'):
            name='Korda.Packaging.Tasks'+suffix
            selected['tools/net11.0/'+name]=(bundles.TASK_PROJECT.parent/'bin/Release/net11.0'/name).read_bytes()
        bundles.OUT=args.output/provider
        native=dict(path=native_name,sha256=old['native']['sha256'],rid='linux-x64',abi_major=1)
        record=bundles.compose(provider,args.version,selected,native,commit,inputs[provider],payloads[provider])
        receipt=dict(schema_version=1,source_commit=commit,source_tree=tree,rid='linux-x64',source_dirty=False,
            packages=[record],publish=[],inputs=inputs,scope='local experimental managed-only candidate; original verified native bytes retained',
            original_release_sha256=digest((base/'release.json').read_bytes()),original_package_sha256=old['upload_archive_sha256'])
        bundles.save(args.output/provider/'release.json',receipt)
        bundles.compat.validate_closure(receipt,{identity:args.output/provider/'feed'/f'{identity}.{args.version}.nupkg'})
        receipts.append(receipt)
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()!=commit:
        raise ValueError('Producer commit changed during compilation')
    if {p:digest((ROOT/p).read_bytes()) for p in source_hashes}!=source_hashes:
        raise ValueError('Source changed during compilation')
    bundles.save(args.output/'build-receipt.json',dict(schema_version=1,source_commit=commit,source_tree=tree,
        tracked_product_inputs=source_hashes,commands=records,packages=[r['packages'][0] for r in receipts],
        native_recompiled=False,public_publication=False))
    print('CANDIDATES_COMPLETE',flush=True)


if __name__=='__main__':
    main()
