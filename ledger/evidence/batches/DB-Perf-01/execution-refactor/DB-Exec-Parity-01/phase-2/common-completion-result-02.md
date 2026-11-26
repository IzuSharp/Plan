# Common-A completion mechanism: measured, not adopted

The original-delegate diagnostic completed for both databases. It receives count/ordering credit only. Each variant/provider has six warm windows of32 queries; every query produces32 native batches. No ordinary timing/CPU/allocation benefit is inferred from these instrumented runs.

| Provider / variant | Pull generations | Registered before setter | GetResult inside setter on setter thread | Different setter/consumer TID |
| --- | ---: | ---: | ---: | ---: |
| sqlite / baseline | 6144 | 5993 | 0 | 1489 |
| sqlite / candidate | 6144 | 5667 | 5670 | 449 |
| postgresql / baseline | 6144 | 5889 | 0 | 1588 |
| postgresql / candidate | 6144 | 5627 | 5630 | 492 |

Every pre-registered, uncaptured candidate continuation was positively witnessed consuming its result inside the setter. Baseline showed no such containment. Thus the intended second-hop removal is implemented and observed. Same TID outside the setter does not count as inline; registration races and synchronous-before-await completion remain separate in the JSON. No observed setter or consumer shared that generation's native-ready callback thread. Markers and reported perf loss channels are zero-loss in these records; this does not prove statistical precision or global thread coverage.

The separate ordinary two-round A/B still shows no repeatable thousand-row CPU/latency benefit. This mechanism result therefore does not justify adopting Common-A by itself. It is retained as an evaluated, unselected experiment, along with its correctness counterexample/regressions and actual source/binaries.

A separate source/marker check also finds that the baseline already defers successful request processing until native readiness. Unconditional post-submit scheduling is not a new missing optimization: request finalization uses deferToReady under the same gate as OnReady. Ordinary batch-granularity native/managed handoffs remain. A custom fixed managed callback pool has not been implemented: running arbitrary continuations on a finite non-growing pool risks starvation/deadlock when those continuations synchronously wait for other work. No global ThreadPool runtime setting is selected.

Evidence: analysis/completion-mechanism-02.json, analysis/summarize_completion_mechanism_02.py, measurements/completion-mechanism-02, and analysis/causal-a-phase-ab-02.json.
