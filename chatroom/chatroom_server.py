import UDP_Server as Server

serv = Server.UDP_Server() # using default ip 127.0.0.1 and port 5280
rooms = {}

while True:
    current_message = serv.returnData(False) #this will return one packet from server
    # packet will be in the form [source_IP,source_port,msg]
    # returnData(wait,timeout=None)
    # update users, echo/route messages to correct users, etc.

    if (current_message[2][0] =='\\'):
    # message contains special command, do not retransmit.
        messageSplit = current_message[2].split(' ')
        if '\\join' in current_message[2]:
            if messageSplit[0]=='\\join' and messageSplit[1] != None:
                if messageSplit[2] == None:
                    messageSplit.append(current_message[0])
                if messageSplit[1] in rooms.keys:
                    rooms[messageSplit[1]].append([messageSplit[2],current_message[0],current_message[1])
                else:
                    rooms[messageSplit[1]]=[messageSplit[2],current_message[0],current_message[1]]
            else: serv.sendMessage(current_message[0],current_message[1],'malformed join attempt')
        if '\\leave' in message[2]:
            if messageSplit[0]=='\\leave' and messageSplit[1] != None:
                if room=detRoom(current_message)!=False:
                    rooms[room] = [x for x in rooms[room] if x[1]!=current_message[0] and x[2]!=current_message[1]]
                else: serv.sendMessage(current_message[0],current_message[1],'invalid room')
            else: serv.sendMessage(current_message[0],current_message[1],'no room')
      # need to parse special command here
    else:
        if room=detRoom(current_message)!=False:
            for user in rooms[room[0]]:
                serv.sendMessage(user[1],user[2],room[1]+':'+current_message[2])
def detRoom(msg):
    for room in rooms.keys:
        for user in rooms[room]:
            if user[2] == msg[1] and user[3] == msg[2]:
                return [room, user[0]]
    return False
