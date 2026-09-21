# Standing rules (repo hygiene)

## Git
- **One branch only: `main`.** Do not create `cursor/*` agent branches, extra worktrees, or parallel feature forks unless the human explicitly asks.
- Land all thesis work as commits on `main`. Prefer small focused commits over branch sprawl.
- Do **not** push to `origin` unless the human asks.
- Remote `origin/cursor/*` leftovers may be deleted later with `git push origin --delete <branch>` when the human wants remote cleanup.

## Scope
- Drive theses (excluding Kasi unless re-included) to 100% CA2 research-scope alignment first.
- Rubric JPEG + `master_rubric.md` = 70%+ quality check only (not a substitute for CA2 floor).
- `GENAI_HANDOFF.md` **not now** — only after thesis requirements are met **and** that thesis completes 3 full-scale final evals. When written, use the self-contained e2e structure in `GENAI_HANDOFF_TEMPLATE.md`.

## Evaluation cycle (binding)
Once a thesis is at **100% CA2**:
1. Run **one** initial evaluation (destroy-after-round).
2. **Re-check** the thesis against the CA2 proposal.
3. If CA2 no longer fully satisfied → **fix** issues → run **one** evaluation again → re-check.
4. Repeat until CA2 remains **100%** after evaluation.
5. **Only then** run **3 full-scale final evaluations** for consistent/reproducible results.
6. Baseline compare (pos+neg), stats, RQ/objectives/limitations/conclusions; then handoff.

Do **not** start the final-3 until the post-eval CA2 re-check stays at 100%.

## AWS
- Free Tier–safe. Destroy stacks after each round. ConcurrentExecutions=10. No endless lite campaigns.
- One live stack at a time when possible; never leave resources running.
