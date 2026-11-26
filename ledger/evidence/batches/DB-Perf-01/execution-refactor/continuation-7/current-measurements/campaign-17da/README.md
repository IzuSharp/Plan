# Exact final campaign inputs — public 17da

The actual pre-run freeze completed with `status=frozen`, before either final
output directory existed. Freeze SHA-256:
`fc1dae9be0a76b0de38c4f94c3836e47b398e10b5ff23f3c8f82313a3cb4bc1a`.
This directory preserves exact copies and original paths; no output or consumer
metadata was rewritten. Product, candidate harness and runner are public
`17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`; reused Dapper harness source
equivalence is pinned to `05fdd6b507bbfa9e971caa739784cf42dfb7199c`.

SQLite uses C4/R3000 and PostgreSQL C8/R3600, queue 64, all 35 cases, batch and
requested rows 32, 8 tenants with 1024 orders each. The 30-second offered
selection retains zero business failures but explicitly records refusals.
See `offered-selection-01.json` and the prospective campaign selection document.

The two baseline plans contain before/current at 120 seconds each. The final
derived plans contain only current/Dapper at 1800 seconds each and 15 seconds
of post-disposal idle. Source final plans are never executed. Timing is serial;
no build, profiler or second workload overlaps. Host affinity is client 0-3,
PostgreSQL 4-7 and observer 8; cgroup quota and exclusive hardware remain
unproven, as recorded by the actual host observation.

At this checkpoint final execution remains 0/4. The frozen input proof is a
prerequisite, not a successful final audit. After four actual intervals the
unchanged arithmetic analyzer and final identity/owner supplement must both
pass; failures retain their original paths.
