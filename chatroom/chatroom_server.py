import UDP_Server as Server

serv = Server.UDP_Server() # using default ip 127.0.0.1 and port 5280
rooms = {}

while True:
    serv.returnData(False) #this will return one packet from the server
    # packet will be in the form [source_IP,source_port,msg]
    # returnData(wait,timeout=None)
    # update users, echo/route messages to correct users, etc.
