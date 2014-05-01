class morse_socket:
    # constants for people to use because numbers are hard
    AF_INET = 2
    SOCK_DGRAM = 2
    timeout = 2.0 # default

    def __init__(self,family,dtype):
        if family == 2 and dtype == 2:
            import morse_code
            outpin = 7
            inpin = 11
            self.network = morse_code.morseNet(inpin,outpin)
            self.myipaddr = "EE"
            self.myport = int(outpin) # our 'port' is the GPIO pin being used.

    def bind(self,address):
        self.myipaddr = address[0]
        #self.myport = int(address[1])
        # Not allowing a change in port, since it's hardcoded to the GPIO pin used.
        self.network.setAddress(address)
        return

    def sendto(self,bytearray_msg,destination):
        if not self.network:
            print("Socket has not been initialized.")
            return False
        # destination is a tuple or list (ip,port)
        toipaddr = destination[0]
        toport = destination[1]
        # ipaddr is in the form "EA" where E is the groupcode and A is the mac
        macto = toipaddr
        groupto = toipaddr[0] # this group's code is E
        # self.toport is the GPIO port of the receiving device/process
        # the protocol is "E" for now
        msg = bytearray_msg.decode('utf-8') # don't actually want a bytearray
        msg = str(msg)
        UDP_packet = str(self.myport)+str(toport)+msg
        UDPlen = self.changeBase(len(UDP_packet),36)
        packet = str(toipaddr)+str(self.myipaddr)+'E'+str(UDPlen)+UDP_packet
        self.network.sendMassage(macto,packet)
        # packet structure:
        # |DEST IP|SRC IP|PROTOCOL|LEN||SRC PORT|DEST PORT|MSG||
        # Everything within the double pipes is a UDP header, contained within
        # an IP header, which is then encapsulated by morse_code inside a MAC
        # header as such:
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
        return message,address

    def settimeout(self,timeout):
        self.timeout = timeout
        return

    def digit_to_char(self,digit):
        if digit < 10:
          return str(digit)
        return chr(ord('a') + digit - 10)

    def changeBase(self,number,base):
        number = int(number)
        if number < 0:
          return '-' + str_base(-number, base)
        (d, m) = divmod(number, base)
        if d > 0:
            return str_base(d, base) + digit_to_char(m)
        return self.digit_to_char(m)
