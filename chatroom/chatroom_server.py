import UDP_Server as Server

serv = Server.UDP_Server() # using default ip 127.0.0.1 and port 5280
rooms = {}

while True:
    serv.get_data() # this is a placeholder for now. Will return one message
    # update users, echo/route messages to correct users, etc.
