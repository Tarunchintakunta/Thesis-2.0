# Standing rules (repo hygiene)

## Git
- **One branch only: `main`.** Do not create `cursor/*` agent branches, extra worktrees, or parallel feature forks unless the human explicitly asks.
- Land all thesis work as commits on `main`. Prefer small focused commits over branch sprawl.
- Do **not** push to `origin` unless the human asks.
- Remote `origin/cursor/*` leftovers may be deleted later with `git push origin --delete <branch>` when the human wants remote cleanup.

## Scope
- Drive theses (excluding Kasi unless re-included) to 100% CA2 research-scope alignment first.
- Rubric JPEG + `master_rubric.md` = 70%+ quality check only (not a substitute for CA2 floor).
- Full-scale final AWS evals (3–5) only after 100% CA2; destroy-after-round; ConcurrentExecutions=10.
- `GENAI_HANDOFF.md` **not now** — only after thesis requirements are met **and** that thesis completes 3–5 full-scale final evals. When written, use the self-contained e2e structure in `GENAI_HANDOFF_TEMPLATE.md`.

## AWS
- Free Tier–safe. Destroy stacks after each round. No endless lite campaigns.
