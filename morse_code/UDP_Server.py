from morse_socket import morse_socket
import queue
from threading import Thread
import signal, sys

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
        socket, AF_INET, SOCK_DGRAM = morse_socket,2,2
        #with socket(AF_INET, SOCK_DGRAM) as sock:
        sock = socket(AF_INET,SOCK_DGRAM)
        sock.bind((self.ip,self.port))
        sock.settimeout(2.0) # 2 second timeout
        self.socket = sock

        print ("UDP Server started on IP Address {}, port {}".format(self.ip,self.port,))

        while not self.killReciever:
            try:
                bytearray_msg, address = sock.recvfrom(1024)
                source_IP, source_port = address

                print ("\nMessage received from ip address {}, port {}:".format(source_IP,source_port))
                print (bytearray_msg.decode("UTF-8"))
                self.packetQueue.put_nowait([source_IP,source_port,bytearray_msg.decode("UTF-8")])

            except:
                continue
        sys.exit()
        return
######################################################################
    def sendMessage(self,ip,port,message):
            destination=(ip,port)
            bytearray_message = bytearray(message,encoding="UTF-8")
            bytes_sent = self.socket.sendto(bytearray_message, destination)
            print ("{} bytes sent".format(bytes_sent))

#######################################################################
    def signal_handler(self,signal,frame):
        print ('exiting')
        self.killReciever = True
        raise SystemExit

    def __init__(self,IP="127.0.0.1",port=5280):
        self.port = port
        self.ip = IP
        self.packetQueue = queue.Queue()
        self.recieveThread = Thread(target=self.recieveData)
        self.recieveThread.start()
        self.killReciever = False
        signal.signal(signal.SIGINT, self.signal_handler)

    def __exit__(self,argException,argString,argTraceback):
        print("exiting")
