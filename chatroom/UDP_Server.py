import CN_Sockets
import queue
from threading import Thread

class UDP_Server(object):
######################################################################
    def returnData(self,wait,timeout=None):
        if wait:
            try:
                return self.packetQueue.get(True,timeout)
            except:
                return None
        else:
            try:
                return self.packetQueue.get_nowait()
            except:
                return None
######################################################################
    def recieveData(self):
        socket, AF_INET, SOCK_DGRAM, timeout = CN_Sockets.socket, CN_Sockets.AF_INET, CN_Sockets.SOCK_DGRAM, CN_Sockets.timeout
        with socket(AF_INET, SOCK_DGRAM) as sock:
            sock.bind((self.ip,self.port))
            sock.settimeout(2.0) # 2 second timeout

            print ("UDP Server started on IP Address {}, port{}".format(self.ip,self.port,))

            while True:
                try:
                    bytearray_msg, address = sock.recvfrom(1024)
                    source_IP, source_port = address

                    print ("\nMessage received from ip address {}, port {}:".format(
                        source_IP,source_port))
                    print (bytearray_msg.decode("UTF-8"))
                    self.packetQueue.put_nowait([source_IP,source_port,bytearray_msg.decode("UTF-8")])

                except timeout:
                    #print (".",end="",flush=True)
                    continue
#######################################################################
    def __init__(self,IP="127.0.0.1",port=5280):
        self.port = port
        self.ip = IP
        self.packetQueue = queue.Queue()
        recieveThread = Thread(target=UDP_Server.recieveData,args=[self])
        recieveThread.start()
