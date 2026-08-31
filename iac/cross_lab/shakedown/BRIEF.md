# BRIEF: passphrase assembly over the board

You are one of three seats: haiku, opus, sonnet. Your name is in your prompt.
Room: /tmp/claude-1000/-home-vas-hsearch/87a841e8-8b64-4f8a-98e4-a955f6217cb3/scratchpad/board1 (call it ROOM below; use the full path in every command).

1. /home/vas/iac/iac join ROOM <your name>
2. Read ROOM/frag/<your name>.txt - your fragment.
3. Broadcast it: /home/vas/iac/iac send ROOM '*' "[<your name>] FRAG: <fragment>"
4. Collect the other two FRAG messages:
   /home/vas/iac/iac drain ROOM <your name>
   while you have fewer than two: /home/vas/iac/iac recv ROOM <your name> 60
   (exit 0 = a message arrived; exit 1 = timeout, retry; give up after 5 timeouts)
5. Order the three fragments by seat name alphabetically (haiku, opus, sonnet), join with "-", and send:
   /home/vas/iac/iac send ROOM operator "[<your name>] ANSWER: <joined>"
6. One final /home/vas/iac/iac recv ROOM <your name> 60, then finish. Do not send anything after your ANSWER.

Every message under 20 words. Prefix every message with [<your name>].
