# BRIEF: fix one issue, as a team of three, by subtraction

Seats: seat1-opus seat2-sonnet seat3-haiku . Your name and model are in your prompt.
The issue: /tmp/cross_lab_work/board-matplotlib__matplotlib-23299-20260903T061947Z/PROBLEM.md. The shared checkout you all edit: /tmp/cross_lab_work/board-matplotlib__matplotlib-23299-20260903T061947Z/repo.
The board room (use the full path in every command): /tmp/cross_lab_work/board-matplotlib__matplotlib-23299-20260903T061947Z/room

The rule this team runs on: a wrong addition costs more than a missing
one. Nothing enters the shared tree without a receipt, and the team's
last act is removal.

Protocol, in order:
1. /home/vas/iac/iac join /tmp/cross_lab_work/board-matplotlib__matplotlib-23299-20260903T061947Z/room <your name>
2. Reproduce the issue before anything else: a command or short script
   that shows the failure on the unmodified tree. Post its output:
   /home/vas/iac/iac send /tmp/cross_lab_work/board-matplotlib__matplotlib-23299-20260903T061947Z/room '*' "[<name>] REPRO: <command> -> <what it printed>"
   Post before reading any board message. No repro, no diagnosis.
3. Post the smallest change you believe fixes the repro, as one file and
   one hunk if possible: /home/vas/iac/iac send /tmp/cross_lab_work/board-matplotlib__matplotlib-23299-20260903T061947Z/room '*' "[<name>] PROPOSAL: <file>: <change>"
   Then /home/vas/iac/iac drain /tmp/cross_lab_work/board-matplotlib__matplotlib-23299-20260903T061947Z/room <your name> and read the others.
4. Claim before editing: /home/vas/iac/iac send /tmp/cross_lab_work/board-matplotlib__matplotlib-23299-20260903T061947Z/room '*' "[<name>] CLAIM: <path>".
   Edit only the file you claimed. Never edit, add or delete a test.
   Never touch a file that is not in your own proposal.
5. Any seat may veto any edit, its own included, with a receipt:
   /home/vas/iac/iac send /tmp/cross_lab_work/board-matplotlib__matplotlib-23299-20260903T061947Z/room '*' "[<name>] VETO: <file>: <the repro output that shows it unnecessary or harmful>"
   The author of a vetoed edit reverts it (git checkout -- <file>) and says so.
6. When your change is in and the repro passes, post the receipt:
   /home/vas/iac/iac send /tmp/cross_lab_work/board-matplotlib__matplotlib-23299-20260903T061947Z/room '*' "[<name>] DONE: <file>: repro now prints <output>"
7. seat1 is the integrator and finishes by subtraction: run the repro on
   the final tree, list every modified file (git status --short), and
   revert anything the repro does not need. Post:
   /home/vas/iac/iac send /tmp/cross_lab_work/board-matplotlib__matplotlib-23299-20260903T061947Z/room '*' "[seat1] FINAL: <files kept> <files reverted> <repro output>"
8. Wait for others: /home/vas/iac/iac recv /tmp/cross_lab_work/board-matplotlib__matplotlib-23299-20260903T061947Z/room <your name> 120 -a -e 300
   Exit 0: messages arrived, act on them, return here.
   Exit 1: timeout, run the same recv again, at most 4 times total.
   Exit 3: you are alone; finish.

Every message under 60 words, prefixed [<name>]. Do not commit.
