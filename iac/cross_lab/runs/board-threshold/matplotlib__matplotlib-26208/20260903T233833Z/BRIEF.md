# BRIEF: fix one issue, as a team of three, posting only what you are sure of

Seats: seat1-opus seat2-sonnet seat3-haiku . Your name and model are in your prompt.
The issue: /tmp/cross_lab_work/board-matplotlib__matplotlib-26208-20260903T233833Z/PROBLEM.md. The shared checkout you all edit: /tmp/cross_lab_work/board-matplotlib__matplotlib-26208-20260903T233833Z/repo.
The board room (use the full path in every command): /tmp/cross_lab_work/board-matplotlib__matplotlib-26208-20260903T233833Z/room

Every board message is posted with one command and carries your confidence:
    /tmp/cross_lab_work/board-matplotlib__matplotlib-26208-20260903T233833Z/room/post <your name> <KIND> <conf> "<text under 60 words>"
conf is an integer 0 to 100: the probability that the claim survives a
peer running a command against it. 100 means you ran it and saw the output.
A claim you have not executed is at most 60. The board holds any message
rated under 90 and posts a PASS line in its place; a PASS costs nothing,
a wrong claim costs the team the run. After a held post: run the thing and
post again with the receipt, or wait and let another seat continue. A held
DONE means your edit is not trusted: revert it (git checkout -- <file>).

Protocol, in order:
1. /home/vas/iac/iac join /tmp/cross_lab_work/board-matplotlib__matplotlib-26208-20260903T233833Z/room <your name>
2. Read the issue. Investigate the repo. Before reading any board message,
   post your own diagnosis: post <name> DIAGNOSIS <conf> "<cause, file>"
3. /home/vas/iac/iac drain /tmp/cross_lab_work/board-matplotlib__matplotlib-26208-20260903T233833Z/room <your name>   then agree who edits which file.
   Claim before editing: post <name> CLAIM 100 "<path>"  (CLAIM is never held)
   Never edit a file another seat has claimed and not released.
4. Edit the shared checkout. Run tests if the repo allows it.
5. When your part is in: post <name> DONE <conf> "<file>: <what you ran and what it printed>"
6. Wait for others: /home/vas/iac/iac recv /tmp/cross_lab_work/board-matplotlib__matplotlib-26208-20260903T233833Z/room <your name> 120 -a -e 300
   Exit 0: one or more messages arrived, act on them, return here.
   Exit 1: timeout, run the same recv again, at most 4 times total,
   then post your final state and finish.
   Exit 3: you are alone, the other seats are gone; post your final
   state and finish. When all three have posted DONE or PASS, finish.

Other kinds: REPRO, VETO (with the output that shows an edit wrong), NOTE.
Do not use /home/vas/iac/iac send directly. Do not create new test files. Do not commit.
Disagreement is data: post it, do not silently overwrite another seat's edit.
