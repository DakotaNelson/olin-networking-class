import UDP_Server as Server

serv = Server.UDP_Server() # using default ip 127.0.0.1 and port 5280
rooms = {}

while True:
    serv.returnData(False) #this will return one packet from the server
    # packet will be in the form [source_IP,source_port,msg]
    # returnData(wait,timeout=None)
    # see UDP_Server.py

    # here: update users, echo/route messages to correct users, etc.

def echoMessages(userList,incMsg):
    for room in userList:
        for userNum in userList[room]:
            serv.sendMessage(userList[room[userNum[1]]],userList[room[userNum[2]]],incMsg)
