# pathread: the index returns a path, the agent reads it

The harness is `../run.py`; the ais binary comes from its checkout (`AIS_REPO`,
default `~/ais`).

The second regime of the paper, run 2026-11-02 on `claude-sonnet-4-6`: the index
maps keys to document paths in the private project, the agent recalls a path and
reads the document; the search arm greps and reads the same tree. Both arms pay
for the reading, so the index saves only the finding. 8 questions, 5 repeats, 80
agent loops, 6.96 USD at list.

| | index arm | search arm |
| --- | --- | --- |
| total tokens, median | 6,215 | 21,020 |
| total tokens, mean | 6,878 | 45,175 |
| retrieval payload, mean | 2,047 | 7,133 |
| tool calls | 3 (6 for the four-document question) | 3 to 24 |
| correct, literal grader | 40/40 | 35/40 |

Ratio of medians 3.4x, of means 6.6x, of payloads 3.5x; per-question ratio of
medians 0.6x to 31x. Where a file name carries the question's words
(`release_runbook`, `db_backup`) grep finds it in one call and the ratio is 1.1x to
1.3x; for the four-document question the index arm reads four files and costs
more than search's one listing. The five search misses by hand: two answers name
the Ant target and the zip without the literal `ant release`, two lists of the
deployment documents each omit one, one run spent its 14 turns without answering.

Files: `questions.json` (ids mirror the main run's), `build_index.sh` (the nine
path records), `run.sh` (the invocation; `run.py --exclude PRIVATE` keeps the
project's private notes out of both arms), `results_sanitized.csv` (no answer
column), `table.tex` (from `analyze.py`). `results.csv` with the answers is not
committed: the answers carry the project's paths. The tree searched was
3,344 files, 0.21 GB (the main run's June tree was 1,300 files, 0.35 GB; same
repository, four months on).
