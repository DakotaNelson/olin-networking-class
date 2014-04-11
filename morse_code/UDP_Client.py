import morse_socket as CN_Sockets # CN_Sockets adds ability to interrupt "while True" loop with ctl-C
import queue
from threading import Thread
from time import sleep

class UDP_Client(object):
######################################################################
    def returnData(self):
        try:
            return messageQueue.get_nowait()
        except:
            return None
######################################################################
    def recieveData(self):
        socket, AF_INET, SOCK_DGRAM = CN_Sockets.morse_socket,2,2
        #with socket(AF_INET, SOCK_DGRAM) as sock:
        sock = socket(AF_INET,SOCK_DGRAM)
        #sock.bind((self.ip,self.port))
        sock.settimeout(2.0) # 2 second timeout

        print ("UDP Client listening on IP Address {}, port {}".format(self.ip,self.port,))

        while True:
            try:
                bytearray_msg, address = sock.recvfrom(1024)
                source_IP, source_port = address

                print (bytearray_msg.decode("UTF-8"))
                self.messageQueue.put_nowait([source_IP,source_port,bytearray_msg.decode("UTF-8")])

            except:
                    #print (".",end="",flush=True)
                continue
######################################################################
    def __init__(self,Server_Address=("127.0.0.1",5280)):
        self.messageQueue = queue.Queue()
        self.port = Server_Address[1]
        self.ip = Server_Address[0]
        recieveThread = Thread(target=self.recieveData)
        recieveThread.start()
        socket, AF_INET, SOCK_DGRAM = CN_Sockets.morse_socket, 2,2
        sock = socket(AF_INET,SOCK_DGRAM)
        #with socket(AF_INET,SOCK_DGRAM) as sock:

        print ("UDP_Client started for UDP_Server at IP address {} on port {}".format(Server_Address[0],Server_Address[1]))
        sleep(2)
        while True:
            str_message = input("Enter message to send to server:\n")
            if not str_message:
                break
            str_message = str_message.upper()
            bytearray_message = bytearray(str_message,encoding="UTF-8")
            sock.sendto(bytearray_message, Server_Address)
            #print ("{} bytes sent".format(bytes_sent))
