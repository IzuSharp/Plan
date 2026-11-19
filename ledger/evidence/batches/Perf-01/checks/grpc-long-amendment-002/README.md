# Pre-execution supervisor acceptance correction

Amendment001 was published and read back at c90f982c but never executed. Independent review identified a possible false acceptance if a completed outer driver exits nonzero yet its finalized result permits the standalone verifier to pass. Amendment002 preserves the001 bytes/history and binds the corrected supervisor. It requires both the standalone verifier and all actual command exit codes to pass; any nonzero exit receives zero overall credit.

No rate,case,producer,profile,driver,TLS,resource,command argv or acceptance threshold changed. This correction grants no extra measurement attempt: there is still exactly one new115/s attempt at grpc-r115-002. The same parentfreeze85061 and frozen three-command document3f582663 apply. Actual publication/readback is required before launch.
