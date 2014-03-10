class morse_socket:
    # constants for people to use because numbers are hard
    self.AF_INET = 2
    self.SOCK_DGRAM = 2
    self.timeout = 2.0 # default

    def __init__(self,family,dtype):
        if family == 2 && dtype == 2:
            import morse_code
            self.network = morse_code.morseNet

    def bind(self,address):
        self.myipaddr=address[0]
        self.myport = address[1]
        return

    def sendto(bytearray_msg,destination):
        if not self.network:
            print("Socket has not been initialized.")
            return False
        # destination is a tuple (ip,port)
        toipaddr = destination[0]
        toport = destination[1]
        # ipaddr is in the form groupcode.mac
        macto = self.toipaddr.split('.')[1]
        groupto = self.toipaddr.split('.')[0] # this group's code is E
        # self.toport is the GPIO port of the receiving device/process
        # the protocol is "1" for now
        msg = bytearray_msg.decode("UTF-8") # don't actually want a bytearray
        packet = groupto+macto+toport+self.myport+"1"+msg
        self.network.sendMassage(macto,packet)
        # packet structure:
        # |GROUP CODE|MAC TO|GPIO TO|GPIO FROM|PROTOCOL|MSG|
        # which is then encapsulated by morse_code into
        # |TTL|TO|FROM|LEN|THIS PACKET|CKSUM|
        return packet

    def recvfrom(self,buflen):
        if not self.network:
            print("Socket has not been initialized.")
            return False
        # call the morse code recieve function
        msg = self.network.returnMessage(True,self.timeout)

        if msg is Null:
            raise Exception('timeout')

        address = msg[0]
        message = msg[1]
        return address,message

    def settimeout(timeout):
        self.timeout = timeout
        return
