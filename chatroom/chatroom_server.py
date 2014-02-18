import UDP_Server as Server

serv = Server.UDP_Server() # using default ip 127.0.0.1 and port 5280
rooms = {}

while True:
    current_message = serv.returnData(False) #this will return one packet from the server
    # packet will be in the form [source_IP,source_port,msg]
    # returnData(wait,timeout=None)
    # update users, echo/route messages to correct users, etc.

    if (current_message[2][0] == "\\"):
    # message contains special command, do not retransmit.
      pass
      # need to parse special command here
    else:
      for room in rooms.values:
        for users in room:
          if current_message[0] in users:
            # sender is in chatroom room
            echoMessages(room, users)
          else:
            # sender not in chatroom, no need to retransmit
            pass



def echoMessages(userList,incMsg):
    for room in userList:
        for userNum in userList[room]:
            serv.sendMessage(userList[room[userNum[1]]],userList[room[userNum[2]]],incMsg)
