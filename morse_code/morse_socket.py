class morse_socket:
    # constants for people to use because numbers are hard
    AF_INET = 2
    SOCK_DGRAM = 2
    timeout = 2.0 # default

    def __init__(self,family,dtype):
        if family == 2 and dtype == 2:
            import morse_code
            outpin = 11
            inpin = 7
            self.network = morse_code.morseNet(inpin,outpin)
            self.myipaddr = "EE"
            self.myport = int(outpin)

    def bind(self,address):
        self.myipaddr = address[0]
        self.myport = int(address[1])
        self.network.ourMac = address[0]
        return

    def sendto(self,bytearray_msg,destination):
        if not self.network:
            print("Socket has not been initialized.")
            return False
        # destination is a tuple (ip,port)
        toipaddr = destination[0]
        toport = destination[1]
        # ipaddr is in the form "EA" where E is the groupcode and A is the mac
        macto = toipaddr.split('')[1]
        groupto = toipaddr.split('')[0] # this group's code is E
        # self.toport is the GPIO port of the receiving device/process
        # the protocol is "E" for now
        # TODO: "myipaddr" is currently never used. This is probably an issue
        msg = bytearray_msg.decode("UTF-8") # don't actually want a bytearray
        packet = str(groupto)+str(macto)+str(toport)+str(self.myport)+"E"+msg
        self.network.sendMassage(macto,packet)
        # packet structure:
        # |GROUP CODE|MAC TO|GPIO TO|GPIO FROM|PROTOCOL|MSG|
        # which is then encapsulated by morse_code into
        # |TTL|MAC TO|MAC FROM|LEN|THIS PACKET|CKSUM|
        return packet

    def recvfrom(self,buflen=0):
        if not self.network:
            print("Socket has not been initialized.")
            return False
        # call the morse code recieve function
        msg = self.network.returnMessage(True,self.timeout)

        if msg is None:
            raise Exception('timeout')

        address = msg[0]
        message = msg[1]
        return address,message

    def settimeout(timeout):
        self.timeout = timeout
        return
