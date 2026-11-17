# Independent review of the integration counter test isolation

Reviewer: database_host. Reviewed source: `874001186635d1f58ecc2d1ad2aae736b9a9421d`. Result: no blocker.

The complete change adds10 test-only lines: one async mutex and guards covering the five migration cases that affect process-global connection counters. Guards include cleanup. The other three cases do not open migration connections. No production code, counter implementation, reset, assertion, exclusion or ignored-test change is present.

Within-case concurrency is retained: SQLite `tokio::join!`, spawned cancellation work, and PostgreSQL lock/cleanup operations are unchanged. Exact zero live-counter assertions, closed-counter comparisons, rollback and original/cleanup errors remain checked. The connection deadline begins after guard acquisition.

The original CI log records the SQLite cleanup check observing another case's live connection. Both reviewed log hashes match `review.json`; the corrected actual PostgreSQL18 run with `--test-threads=8` passed all8 tests, with zero failures, ignored or filtered cases. No new test or code change was made during this independent review.
