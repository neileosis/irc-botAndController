This is a IRC based botnet. The controller issues commands to many bots and the bots accept commands from the controller and execute them. They communicate to each other through an IRC server.

This was created as an assignment for CPSC 526 at the University of Calgary in 2017.
The authors are Neil Hagstrom and Christopher Neave.

To run the programs you can follow this protocol:
bot.py:

$python3 bot.py <hostname> <port> <channel> <secret>
$python3 bot.ph 199.116.235.44 12399 1337 password

conbot.py:

$python3 conbot.py <hostname> <port> <channel> <secret>
$python3 conbot.ph 199.116.235.44 12399 1337 password

The controller will then ask for you to input your commands.

Commands supported:
status
- This command will make the controller issue a command that will result in the bots identifying themselves to the controller. The controller will then print out the list of bots (their nicks), and their total number.

attack <hostname> <port>
- This command will make every bot connect to the given hostname and port and send it a message with its bot name and attack counter. After it is complete the bots will send diagnostic messages back to the controller.

move <hostname> <port> <channel>
- This command will instruct all bots to disconnect from the current IRC server and connect to the new specified IRC server.

quit
- The controller will disconnect from the IRC and then terminate. The bots are unaffected.

shutdown
- This command will terminate all of the bots. The controller will report the nicks of the bots that shut down and itself will remain running.