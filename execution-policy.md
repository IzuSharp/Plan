# Planning and execution policy

Plan work before changing the design; resolve the design before changing the
product. Use task-marked branches and isolated worktrees, with scoped ownership
for parallel work. The current user instruction determines authorization and
where to stop; old task text is historical context.

Keep dependencies explicit in the three graphs. Start dependencies constrain
when work begins; acceptance dependencies constrain when its result is accepted.
Research and documentation references provide context without creating a global
execution lock. Select optional work explicitly, and preserve uncertainty.

Record the actual source/platform/result boundary in final conclusions. Product
execution, Native AOT consumers, package publication and performance comparisons
must have their own observed results. A document gate is not execution evidence.
Separate development findings, short comparisons and long campaigns; do not
reassign measurements to different source or package bytes.

Keep temporary logs, samples, archives, receipts and recovery state on the
execution machine. Commit concise final findings and rationale. Review the final
diff and applicable current checks before a PR; do not bypass required reviews,
change repository settings to obtain a green result or impersonate reviewers.

See [AGENTS.md](AGENTS.md) and [document CI](eng/ci/README.md) for registration and
local validation. Historical acceptance workflows are no longer replayed.
