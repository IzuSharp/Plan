# Milestones and parallel work

[CURRENT-PHASE.md](CURRENT-PHASE.md) records delivered database batches and the
current scope. The three graphs retain 34 research, 32 documentation and 48
original delivery task definitions. Task edges describe local prerequisites;
A/B labels are not whole-project serial barriers.

Historical parallel work groups remain useful for interpreting task intent:

| Work group | Dependent work | Acceptance scope |
| --- | --- | --- |
| ABI, models, shared data boundary | Interop, providers and query bindings | Component contracts and actual implementation |
| Interop/generation and database foundations | Host, mapping, queries and relations | Native and C# behavior with resource ownership |
| Platforms and independent packages | Consumer composition and releases | Applicable Native AOT, package and runtime checks |
| Diagnostics and comparison design | Fault/resource/performance investigations | Actual scoped measurements and explicit limitations |

Retired Server and future hardware/mobile tasks are historical plans, not current
execution authority or prerequisites for ordinary database development.
