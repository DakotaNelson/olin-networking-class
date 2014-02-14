import UDP_Client as Client

client = Client.UDP_Client() # use default ip 127.0.0.1 and port 5280

# this will probably have to be multi-threaded: one to sit and wait for
# messages, one to enable sending new ones
