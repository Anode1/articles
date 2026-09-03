# BRIEF: fix one issue, as a team of three

Seats: seat1-opus seat2-sonnet seat3-haiku . Your name and model are in your prompt.
The issue: /tmp/cross_lab_work/board-sympy__sympy-20916-20260902T220541Z/PROBLEM.md. The shared checkout you all edit: /tmp/cross_lab_work/board-sympy__sympy-20916-20260902T220541Z/repo.
The board room (use the full path in every command): /tmp/cross_lab_work/board-sympy__sympy-20916-20260902T220541Z/room

Protocol, in order:
1. /home/vas/iac/iac join /tmp/cross_lab_work/board-sympy__sympy-20916-20260902T220541Z/room <your name>
2. Read the issue. Investigate the repo. Before reading any board message,
   post your own diagnosis: /home/vas/iac/iac send /tmp/cross_lab_work/board-sympy__sympy-20916-20260902T220541Z/room '*' "[<name>] DIAGNOSIS: ..."
   (this is what makes three seats worth more than one)
3. /home/vas/iac/iac drain /tmp/cross_lab_work/board-sympy__sympy-20916-20260902T220541Z/room <your name>   then discuss: agree who edits which file.
   Claim before editing: /home/vas/iac/iac send /tmp/cross_lab_work/board-sympy__sympy-20916-20260902T220541Z/room '*' "[<name>] CLAIM: <path>"
   Never edit a file another seat has claimed and not released.
4. Edit the shared checkout. Run tests if the repo allows it.
5. When your part is in: /home/vas/iac/iac send /tmp/cross_lab_work/board-sympy__sympy-20916-20260902T220541Z/room '*' "[<name>] DONE: <what you did>"
6. Wait for others: /home/vas/iac/iac recv /tmp/cross_lab_work/board-sympy__sympy-20916-20260902T220541Z/room <your name> 120 -a -e 300
   Exit 0: one or more messages arrived, act on them, return here.
   Exit 1: timeout, run the same recv again, at most 4 times total,
   then post your final state and finish.
   Exit 3: you are alone, the other seats are gone; post your final
   state and finish. When all three have posted DONE, finish.

Every message under 60 words, prefixed [<name>]. Do not create new test
files. Do not commit. Disagreement is data: post it, do not silently
overwrite another seat's edit.
