class morse_socket:

    def __init__(self,family,dtype):
        if family == 2 && dtype == 2:
            import morse_code
            self.network = morse_code.morseNet

    def bind(self,address):
        self.myipaddr=address[0]
        self.myport = address[1]
        return

    def send_to(address,msg):
        self.toipaddr = address[0]
        self.toport = address[1]
        self.msg = msg
        # ipaddr is in the form groupcode.mac
        # self.toport is the GPIO port of the receiving device/process
        # the protocol is "1" for now
        packet = "E"+self.toipaddr.split('.')[1]+self.toport+self.myport+"1"+msg
        self.network.sendMassage(macto,packet)
        # packet structure:
        # |GROUP CODE|MAC TO|GPIO TO|GPIO FROM|PROTOCOL|MSG|
        # which is then encapsulated by morse_code into
        # |TTL|TO|FROM|LEN|THIS PACKET|CKSUM|

    def rcv_from(buflen):
        # call the morse code recieve function
        network.returnMessage(false)
        return (self.fromipaddr,self.fromport)
