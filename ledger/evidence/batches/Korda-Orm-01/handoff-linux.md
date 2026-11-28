# Korda-Orm-01 Linux handoff

Status: research in progress; no product implementation authorized or performed.
This is the single maintained progress and continuation entry for this task.

## Scope and source of truth

- [Research plan](plan.md).
- Writable repositories: IzuSharp/Korda-Design and IzuSharp/Plan only.
- Task branch in both: `task/Korda-Orm-01-linux`; ordinary commits, no history rewrite.
- Product baseline, read-only: IzuSharp/Korda `36bd5ba169b628ba4d61dd9fe260eaef5ff15599`.
- Initial Design main: `80746769f11874ae917e17a0f02f5ee47a3e250d`.
- Initial Plan main: `911c9764d0bfe10e78862251b43fcf108a8696e8`.

The commit containing this document identifies its own Plan revision; a document
cannot contain its own future commit hash. Later entries record confirmed earlier
milestones and the final PR head is obtained from GitHub before continuing work.

## Progress and decisions

| Area | State | Confirmed conclusion / next work |
| --- | --- | --- |
| Repository rules | Complete | Read all three root AGENTS and document CI guides; retain distinct PR diff semantics |
| jOOQ core | In progress | Inspect types, query model, execution coupling and OSS license boundaries |
| jOOQ SQL/generation | In progress | Inspect dialect transformations, schema generation and available tests |
| Dapper.AOT/drivers | In progress | Inspect dynamic SQL, generated binding/mapping and driver AOT compatibility |
| Design and implementation plan | In progress | Establish source-informed shared contracts, then author independent modules concurrently |
| Local validation | Environment assessment | No `dotnet` on PATH; no compiled/AOT/benchmark results claimed |
| Review and PR CI | Not started | Review actual documents, check routing, open two linked PRs; do not merge |

jOOQ research uses `version-3.21.10`, commit
`3c58109e7ab69772de75e640852935ee7e284177`. Initial source inspection confirms that
standalone SQL rendering exists while the Java query and type model still contain
JDBC/execution coupling. The C# rewrite must preserve SQL semantics while separating
driver-neutral model/rendering from driver codecs and execution.

## Open questions and immediate next work

Complete fixed-source reviews, finalize the parameter/result boundary, establish
the attainable prototype gates, and write formal Design specifications. In parallel,
design a new implementation DAG without legacy task dependencies. Inspect whether
the current graph checker needs a minimal independent-graph extension.

After each meaningful stage, replace completed work above with concise confirmed
results, formal document links, commit/PR references and remaining limitations.
To resume, fetch both task branches, inspect actual heads and this document, then
continue unfinished entries rather than repeating completed source studies.

No raw logs, experiment projects, agent drafts, runtime state, screenshots, samples
or recovery caches belong here. Reproduction belongs in concise formal methods.
