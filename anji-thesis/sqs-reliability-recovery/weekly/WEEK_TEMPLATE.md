# Weekly activity report - template

Copy this file to `WEEK_NN.md` each week and fill it in yourself before the
supervision meeting (it is 12 % of the module mark, so keep it honest and
specific: commits, run ids, numbers, problems).

```text
Week: NN | Dates: YYYY-MM-DD to YYYY-MM-DD | Student: Anjaneya Reddy Gurram 24288853
Goals this week:
-
Work completed:
-
Artefact commits / experiment IDs:
- commits: (git log --oneline --since="1 week ago")
- runs:    (campaign + RUN_IDs from results/**/manifests)
Results / blockers:
-
Next week plan:
-
Supervisor questions:
-
Hours:
```

## Planned 12 weeks (from the proposal)

| Week | Phase | Planned milestone |
|------|-------|-------------------|
| 1-2  | Rig | SAM stack, harness, fault switch, unit tests, validated environment |
| 3    | Baseline | no-fault Kyrychenko replication, duplicate floor recorded |
| 4    | Arms | sync vs queue arm under matched load |
| 5    | Campaign A | visibility timeout x consumer_kill |
| 6    | Campaigns B/C | maxReceiveCount x unhandled_error / datastore_reject |
| 7    | Campaigns D/E | datastore_timeout, guidance transfer (H3) |
| 8    | Burst | burst replication of key cells |
| 9-10 | Analysis | H1-H3, Holm, effect sizes, figures |
| 11   | Write-up | report + configuration manual |
| 12   | Buffer | overruns, video recordings, teardown check |

Useful commands for filling this in:

```bash
git log --oneline --since="1 week ago"
ls results/*/manifests | head
python analysis/stats_tests.py --in results/pilot --power
```

Anjaneya Reddy Gurram
