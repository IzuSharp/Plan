"""Original selected-native command subsets; no producer or cost-mode execution."""
from pathlib import Path


def plan(product, output, native, tools, design):
    dotnet, python = tools['dotnet']['path'], tools['python']['path']
    sdk = str(Path(tools['dotnet']['executable_path']).parent)
    flags = ['-m:1', '-nr:false', '-p:UseSharedCompilation=false']
    asset = '-p:NativeWeaveServerAssetPath=' + native['path']
    rows, binaries = [], {}

    def add(label, argv, timeout=600, environment=None, executable=None, server=True):
        rows.append(dict(label=label, argv=list(map(str, argv)), cwd=str(product),
                         timeout_seconds=timeout, environment_overrides=environment or {}))
        if executable is not None:
            binaries[label] = dict(executable=str(executable), server=server)

    project = product / 'tests/Server.Native/Server.Native.Tests.csproj'
    dll = project.parent / 'bin/Release/net11.0/NativeWeave.Server.Native.Tests.dll'
    aot = output / 'B17/aot'
    add('b17-jit-restore', [dotnet, 'restore', project, '--locked-mode', '--ignore-failed-sources', *flags], 900)
    add('b17-jit-build', [dotnet, 'build', project, '-c', 'Release', '--no-restore', asset, *flags], 900)
    add('b17-jit-execute', [dotnet, dll], 90, {'NW_SERVER_EVIDENCE': str(output / 'B17/jit-fixture')}, dll)
    add('b17-aot-restore', [dotnet, 'restore', project, '-r', 'linux-x64', '-p:PublishAot=true', '--locked-mode', '--ignore-failed-sources', *flags], 900)
    add('b17-aot-publish', [dotnet, 'publish', project, '-c', 'Release', '-r', 'linux-x64', '-p:PublishAot=true', '--no-restore', asset, '-o', aot, *flags], 900)
    add('b17-aot-execute', [aot / 'NativeWeave.Server.Native.Tests'], 90, {'NW_SERVER_EVIDENCE': str(output / 'B17/aot-fixture')}, aot / 'NativeWeave.Server.Native.Tests')

    add('b15-selected-native', [python, product / 'tests/Server.Application/verify.py', '--output', output / 'B15',
                               '--native', native['path'], '--design', design, '--sdk', sdk], 5400)

    project = product / 'tests/Protocols.Mcp/Protocols.Mcp.Tests.csproj'
    dll = project.parent / 'bin/Release/net11.0/NativeWeave.Server.Mcp.Tests.dll'
    api = project.parent / 'ApiCheck/ApiCheck.csproj'
    api_dll = api.parent / 'bin/Release/net11.0/NativeWeave.Server.Mcp.ApiCheck.dll'
    aot = output / 'B19-managed/aot'
    add('b19-restore-jit', [dotnet, 'restore', project, '--locked-mode', '--ignore-failed-sources', *flags])
    add('b19-build-jit', [dotnet, 'build', project, '-c', 'Release', '--no-restore', asset, *flags])
    add('b19-actual-jit', [dotnet, dll], executable=dll)
    add('b19-api-restore', [dotnet, 'restore', api, '--locked-mode', '--ignore-failed-sources', *flags])
    add('b19-api-build', [dotnet, 'build', api, '-c', 'Release', '--no-restore', *flags])
    add('b19-api-exact', [dotnet, api_dll, product, design, sdk], executable=api_dll, server=False)
    add('b19-restore-aot', [dotnet, 'restore', project, '-r', 'linux-x64', '-p:PublishAot=true', '--locked-mode', '--ignore-failed-sources', *flags])
    add('b19-publish-aot', [dotnet, 'publish', project, '-c', 'Release', '-r', 'linux-x64', '-p:PublishAot=true', '--no-restore', asset, '-o', aot, *flags])
    add('b19-actual-aot', [aot / 'NativeWeave.Server.Mcp.Tests'], executable=aot / 'NativeWeave.Server.Mcp.Tests')
    add('b19-package-consumer', [python, product / 'tests/Protocols.Mcp/package_probe.py', '--output', output / 'B19-managed/package', '--native', native['path']])

    flags = ['-p:UseSharedCompilation=false', '-nr:false', '-m:1', '-p:RestoreLockedMode=true', asset]
    project = 'tests/Server.Diagnostics/Server.Diagnostics.Tests.csproj'
    folder = product / 'tests/Server.Diagnostics/bin'
    debug = folder / 'Debug/net11.0/NativeWeave.Server.Diagnostics.Tests.dll'
    release = folder / 'Release/net11.0/NativeWeave.Server.Diagnostics.Tests.dll'
    api = 'tests/Server.Diagnostics/ApiCheck/bin/Release/net11.0/NativeWeave.Server.Diagnostics.ApiCheck.dll'
    sample = 'samples/api/server-diagnostics/bin/Debug/net11.0/server-diagnostics.dll'
    aot = output / 'B20-managed/aot'
    add('b20-managed-debug-build', [dotnet, 'build', project, '-c', 'Debug', *flags], 900)
    add('b20-actual-debug', [dotnet, debug, '--defaults'], 120, executable=debug)
    add('b20-managed-release-build', [dotnet, 'build', project, '-c', 'Release', *flags], 900)
    add('b20-actual-jit', [dotnet, release], 180, executable=release)
    add('b20-api-build', [dotnet, 'build', 'tests/Server.Diagnostics/ApiCheck/ApiCheck.csproj', '-c', 'Release', *flags], 900)
    add('b20-api-public-xml', [dotnet, api, product, sdk, design], 900, executable=product / api, server=False)
    add('b20-sample-debug-build', [dotnet, 'build', 'samples/api/server-diagnostics/server-diagnostics.csproj', '-c', 'Debug', *flags], 900)
    add('b20-sample-debug-disabled', [dotnet, sample], 900, executable=product / sample)
    add('b20-sample-debug-explicit-local', [dotnet, sample, '--local'], 900, executable=product / sample)
    add('b20-publish-aot', [dotnet, 'publish', project, '-c', 'Release', '-r', 'linux-x64', '-p:PublishAot=true', *flags, '-o', aot], 900)
    add('b20-actual-aot', [aot / 'NativeWeave.Server.Diagnostics.Tests'], 180, executable=aot / 'NativeWeave.Server.Diagnostics.Tests')
    add('b20-package-consumer', [python, product / 'tests/Server.Diagnostics/package_probe.py', '--output', output / 'B20-managed/package', '--native', native['path']], 1800)
    return rows, binaries
