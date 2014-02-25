import UDP_Server as Server
import sys, signal
serv = Server.UDP_Server() # using default ip 127.0.0.1 and port 5280
rooms = {}
########################################################################################
def parseMessage(current_message):
    source_ip = current_message[0]
    source_port = current_message[1]
    msg = current_message[2]
    room = detRoom(current_message)
    if room is not False:
        room_name = room[0]
        user_name = room[1]
    else:
        room_name = user_name = False

    if (msg[0] =='\\'): # This is a command message.
        # message contains special command, do not retransmit.
        messageSplit = msg.split(' ')

        command = messageSplit[0] # we can assume there's at least one character, therefore this is safe

        try:
            arg1 = messageSplit[1]
        except:
            serv.sendMessage(source_ip,source_port,"Error: malformed command.")
            return # Break out to the top of our while loop.

        try:
            arg2 = messageSplit[2]
        except:
            serv.sendMessage(source_ip,source_port,"Error: malformed command.")
            arg2 = source_ip

        if command =='\\join':
            joinRoom(arg1,arg2,source_ip,source_port) # join the new room
            if room != False:
                leaveRoom(room_name,user_name) # leave the old room, if any
        if command=='\\leave':
            if room != False:
                leaveRoom(room_name,user_name)
            else:
                serv.sendMessage(source_ip,source_port,'Error: Not in a room.')

        if command == '\\room':
            if room != False:
                serv.sendMessage(source_ip,source_port,'You are currently in '+room_name+'.')

        if command =='\\message':
            if room != False:
                #WIP,code to find IP & port
                serv.sendMessage(pm_ip, pm_port, user_name+'(Private): '+msg)
            else:
                serv.sendMessage(source_ip,source_port,"Error: Not in a room.")

    else: # A regular, non-command message.
        if room != False:
            for user in rooms[room_name]:
                serv.sendMessage(user[1],user[2],user_name+': '+msg)
        else:
            serv.sendMessage(source_ip,source_port,"Error: you are not in any rooms.")
    #adc://electra:2780
########################################################################################
def detRoom(msg):
    for key in rooms.keys():
        for user in rooms[key]:
            if user[2] == msg[1] and user[3] == msg[2]:
                return [room, user[0]]
    return False
########################################################################################
def joinRoom(room,user,ip,port):
    if room in rooms.keys():
        rooms[room].append([user,ip,port])
    else:
        rooms[room] = [user,ip,port]
    print("User joined a room!")
########################################################################################
def leaveRoom(room,user):
    if room in rooms.keys():
        rooms[room_name] = [user for user in rooms[room] if user[0]!=user]
    else:
        serv.sendMessage(source_ip,source_port,'Error: Not in a room.')
########################################################################################

while not serv.killReciever:
    current_message = serv.returnData(False) #this will return one packet from server
    # packet will be in the form [source_IP,source_port,msg]
    # returnData(wait,timeout=None)
    # update users, echo/route messages to correct users, etc.
    if current_message is not None:
        parseMessage(current_message)

