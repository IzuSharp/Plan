#!/usr/bin/env python3
"""Apply the same local event ledger to exact before/tail ordinary source bases.

No build or workload is run. Outputs are diagnostic-only worktrees and must never
be relabeled as the ordinary candidate or pushed into product CI.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASES = {'before': '2ea67ce1902f330679c3ebff4d6d5733be20f69c',
         'tail': '4a9e4435ea5c836be44fb00dc4219301567072c6'}


def replace(text, old, new):
    assert text.count(old) == 1, 'Expected one exact original boundary: ' + old[:100]
    return text.replace(old, new)


def method(text, signature):
    start = text.index(signature)
    opening = text.index('{', start)
    depth = 1
    index = opening + 1
    while depth:
        depth += (text[index] == '{') - (text[index] == '}')
        index += 1
    return text[start:index]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('variant', choices=BASES)
    args = parser.parse_args()
    tree = ROOT / ('worktrees/Korda-tail06-diag-' + args.variant)
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=tree, text=True).strip() == BASES[args.variant]
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=tree)
    before = {}
    after = {}

    def write(relative, old, new):
        path = tree / relative
        if old is not None:
            before[relative] = hashlib.sha256(old.encode()).hexdigest()
        else:
            assert not path.exists()
        path.write_text(new)
        after[relative] = hashlib.sha256(path.read_bytes()).hexdigest()

    relative = 'src/Interop.Callbacks/CallbackCoordinator.cs'
    original = (tree / relative).read_text()
    text = replace(original, '    private long _rejections;', '''    private long _rejections;
    // LOCAL DIAGNOSTIC: identity is a coherent immutable reference, not two
    // separately observed mutable generation/version fields.
    private readonly long _diagnosticController = CallbackDispatchDiagnostics.NewController();
    private CallbackDiagnosticRequest? _diagnosticRequest, _diagnosticQueuedRequest;
    private long _diagnosticOffer;
    protected CallbackDiagnosticRequest? DiagnosticRequest => Volatile.Read(ref _diagnosticRequest);
    protected void ResetDiagnosticRequest(ulong generation, short version)
    {
        var request = CallbackDispatchDiagnostics.NewRequest(_diagnosticController, generation, version);
        Volatile.Write(ref _diagnosticRequest, request);
        CallbackDispatchDiagnostics.Record("request", request);
    }''')
    old_signal = method(text, '    internal void Signal()')
    new_signal = '''    internal void Signal()
    {
        var diagnosticRequest = DiagnosticRequest;
        long diagnosticOffer = 0;
        lock (_scheduleGate)
        {
            if (_completed) return;
            _dirty = true;
            if (_scheduled) return;
            _scheduled = true;
            if (diagnosticRequest is not null)
            {
                _diagnosticOffer = diagnosticOffer = CallbackDispatchDiagnostics.NewOffer();
                _diagnosticQueuedRequest = diagnosticRequest;
            }
        }
        CallbackDispatchDiagnostics.BeginOffer(diagnosticRequest, diagnosticOffer);
        bool accepted, diagnosticThrew = false;
        try { accepted = _scheduler.TryQueue(this); }
        catch (Exception) { accepted = false; diagnosticThrew = true; }
        CallbackDispatchDiagnostics.EndOffer(diagnosticRequest, diagnosticOffer, accepted, diagnosticThrew);
        if (!accepted)
        {
            Interlocked.Increment(ref _rejections);
            lock (_scheduleGate)
            {
                _scheduled = false;
                _diagnosticOffer = 0; _diagnosticQueuedRequest = null;
            }
        }
    }'''
    text = replace(text, old_signal, new_signal)
    old_execute = method(text, '    void IThreadPoolWorkItem.Execute()')
    beginning = ('        CallbackPublication publication = default;' if args.variant == 'tail'
                 else '        try { Process(); }')
    original_tail = old_execute[old_execute.index(beginning):old_execute.rfind('\n    }')]
    instrumented_tail = '\n'.join('    ' + line for line in original_tail.splitlines())
    new_execute = '''    void IThreadPoolWorkItem.Execute()
    {
        CallbackDiagnosticRequest? diagnosticRequest, diagnosticQueuedRequest;
        long diagnosticOffer;
        bool diagnosticSkipped;
        lock (_scheduleGate)
        {
            diagnosticRequest = DiagnosticRequest;
            diagnosticQueuedRequest = _diagnosticQueuedRequest;
            diagnosticOffer = _diagnosticOffer;
            _diagnosticOffer = 0; _diagnosticQueuedRequest = null;
            diagnosticSkipped = _completed;
            if (_completed) _scheduled = false;
            else { _dirty = false; _retry = false; }
        }
        diagnosticRequest ??= diagnosticQueuedRequest;
        CallbackDispatchDiagnostics.ClaimOffer(diagnosticOffer);
        long queuedGeneration = diagnosticQueuedRequest is null ? 0 : unchecked((long)diagnosticQueuedRequest.Generation);
        long queuedVersion = diagnosticQueuedRequest?.Version ?? 0;
        CallbackDispatchDiagnostics.Activity("execute", diagnosticRequest, true, diagnosticOffer, queuedGeneration, queuedVersion);
        try
        {
            if (diagnosticSkipped)
            {
                CallbackDispatchDiagnostics.Record("execute-skipped", diagnosticRequest, diagnosticOffer);
                return;
            }
''' + instrumented_tail + '''
        }
        finally
        {
            // Only captured diagnostic locals are used after tail publication.
            CallbackDispatchDiagnostics.Activity("execute", diagnosticRequest, false, diagnosticOffer, queuedGeneration, queuedVersion);
        }
    }'''
    text = replace(text, old_execute, new_execute)
    write(relative, original, text)

    relative = 'src/Data.NativeHost/HostPullController.cs'
    original = (tree / relative).read_text()
    text = replace(original, '            _completion.Reset(); version = _completion.Version;',
                   '            _completion.Reset(); version = _completion.Version;\n            ResetDiagnosticRequest(_generation, version);')
    text = replace(text, '        bool control = false;', '        var diagnosticRequest = DiagnosticRequest;\n        bool control = false;')
    text = replace(text, '                var status = NativeHost.PullExecution(_source.Binding).Prepare(',
                   '                CallbackDispatchDiagnostics.Record("prepare-enter", diagnosticRequest);\n                var status = NativeHost.PullExecution(_source.Binding).Prepare(')
    text = replace(text, '                    checked((uint)_rows), checked((ulong)_source.Limits.MaxBatchBytes), &callbacks, &error);',
                   '                    checked((uint)_rows), checked((ulong)_source.Limits.MaxBatchBytes), &callbacks, &error);\n                CallbackDispatchDiagnostics.Record("prepare-exit", diagnosticRequest, status);')
    text = replace(text, '        ExecutePrepared();', '        CallbackDiagnosticRequest? diagnosticPublicationRequest = null;\n        ExecutePrepared();')
    text = replace(text, '            _published = true;', '''            _published = true;
            diagnosticPublicationRequest = DiagnosticRequest;
            int diagnosticObligations = (_rooted ? 1 : 0) | (_slot >= 0 ? 2 : 0)
                | (_controls != 0 ? 4 : 0) | (_callbackEntries != 0 ? 8 : 0)
                | (!_registrationDrained ? 16 : 0) | (_executing ? 32 : 0);
            CallbackDispatchDiagnostics.Record("retired", diagnosticPublicationRequest, diagnosticObligations);''')
    text = replace(text, '        if (take)\n        {\n            try',
                   '        if (take)\n        {\n            var diagnosticTakeRequest = DiagnosticRequest;\n            try')
    text = replace(text, '                Boundary(HostPullBoundary.BeforeTake);',
                   '                Boundary(HostPullBoundary.BeforeTake);\n                CallbackDispatchDiagnostics.Record("take-enter", diagnosticTakeRequest);')
    text = replace(text, '                    checked((int)_source.Limits.MaxBatchBytes), _token, _source.TestAfterErrorTake);',
                   '                    checked((int)_source.Limits.MaxBatchBytes), _token, _source.TestAfterErrorTake);\n                CallbackDispatchDiagnostics.Record("take-exit", diagnosticTakeRequest);')

    setter = '''        if (failure is null) _completion.SetResult(_batch);
        else _completion.SetException(failure);'''
    if args.variant == 'tail':
        setter = '''        if (failure is null) _completion.SetResult((ScopedStreamBatch)result!);
        else _completion.SetException(failure);'''
        request_line = '        var diagnosticPublicationRequest = DiagnosticRequest;\n'
    else:
        request_line = ''
    wrapped_setter = request_line + '''        var diagnosticSetter = CallbackDispatchDiagnostics.EnterSetter(diagnosticPublicationRequest);
        bool diagnosticSetterReturned = false;
        try
        {
''' + '\n'.join('    ' + line for line in setter.splitlines()) + '''
            diagnosticSetterReturned = true;
        }
        finally
        {
            // Never read controller/generation fields after the actual setter.
            CallbackDispatchDiagnostics.ExitSetter(diagnosticSetter, !diagnosticSetterReturned);
        }'''
    text = replace(text, setter, wrapped_setter)

    run_method = method(text, '    private unsafe void ExecutePrepared()')
    changed_run = replace(run_method, '        bool abandon;', '        CallbackDiagnosticRequest? diagnosticRequest;\n        bool abandon;')
    changed_run = replace(changed_run, '            generation = _generation;', '            generation = _generation;\n            diagnosticRequest = DiagnosticRequest;')
    changed_run = replace(changed_run, '            Boundary(abandon ? HostPullBoundary.BeforeAbandon : HostPullBoundary.BeforeRun);',
                          '            Boundary(abandon ? HostPullBoundary.BeforeAbandon : HostPullBoundary.BeforeRun);\n            CallbackDispatchDiagnostics.Record("native-run-enter", diagnosticRequest, abandon ? 1 : 0);')
    changed_run = replace(changed_run, '                : calls.Run(lease.Pointer, generation, &error);',
                          '                : calls.Run(lease.Pointer, generation, &error);\n            CallbackDispatchDiagnostics.Record("native-run-return", diagnosticRequest, status, abandon ? 1 : 0);')
    changed_run = changed_run[:-5] + '        CallbackDispatchDiagnostics.Record("native-frame-exit", diagnosticRequest);\n    }'
    text = replace(text, run_method, changed_run)

    get_result = method(text, '    ScopedStreamBatch IValueTaskSource<ScopedStreamBatch>.GetResult(short token)')
    inner = get_result[get_result.index('{') + 1:get_result.rfind('}')].strip('\n').rstrip()
    get_result_wrapped = '''    ScopedStreamBatch IValueTaskSource<ScopedStreamBatch>.GetResult(short token)
    {
        var diagnosticRequest = DiagnosticRequest;
        CallbackDispatchDiagnostics.Activity("getresult", diagnosticRequest, true, token);
        try
        {
''' + '\n'.join('    ' + line for line in inner.splitlines()) + '''
        }
        finally { CallbackDispatchDiagnostics.Activity("getresult", diagnosticRequest, false, token); }
    }'''
    text = replace(text, get_result, get_result_wrapped)
    text = replace(text, '''    void IValueTaskSource<ScopedStreamBatch>.OnCompleted(Action<object?> continuation, object? state, short token,
        ValueTaskSourceOnCompletedFlags flags) => _completion.OnCompleted(continuation, state, token, flags);''', '''    void IValueTaskSource<ScopedStreamBatch>.OnCompleted(Action<object?> continuation, object? state, short token,
        ValueTaskSourceOnCompletedFlags flags)
    {
        var diagnosticRequest = DiagnosticRequest;
        if (diagnosticRequest is null) { _completion.OnCompleted(continuation, state, token, flags); return; }
        ArgumentNullException.ThrowIfNull(continuation);
        long diagnosticRegistration = CallbackDispatchDiagnostics.NewRegistration();
        int diagnosticScheduler = CallbackDispatchDiagnostics.SchedulerKind(flags);
        var diagnosticContinuation = new CallbackDiagnosticContinuation(diagnosticRequest, diagnosticRegistration, continuation, state);
        CallbackDispatchDiagnostics.Activity("oncompleted", diagnosticRequest, true, diagnosticRegistration, (long)flags, diagnosticScheduler);
        bool diagnosticReturned = false;
        try
        {
            _completion.OnCompleted(static item => ((CallbackDiagnosticContinuation)item!).Invoke(), diagnosticContinuation, token, flags);
            diagnosticReturned = true;
        }
        finally
        {
            CallbackDispatchDiagnostics.Activity("oncompleted", diagnosticRequest, false, diagnosticRegistration,
                diagnosticReturned ? 0 : 1, diagnosticScheduler);
        }
    }''')
    write(relative, original, text)
    logger = (HERE / 'CallbackDispatchDiagnostics.cs').read_text()
    write('src/Interop.Callbacks/CallbackDispatchDiagnostics.cs', None, logger)
    subprocess.run(['git', 'diff', '--check'], cwd=tree, check=True)
    receipt = {'task': 'DB-Exec-Parity-01', 'variant': args.variant, 'base': BASES[args.variant],
               'worktree': str(tree), 'before': before, 'after': after,
               'generatorSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'ordinaryTimingCredit': False, 'runtimeModified': False,
               'scope': 'Independent local diagnostic source overlay; package/ELF identities remain pending'}
    output = HERE / ('applied-' + args.variant + '-01.json')
    assert not output.exists()
    output.write_text(json.dumps(receipt, indent=2) + '\n')
    print(output)


if __name__ == '__main__':
    main()
