class morse_socket:
    def __init__(self,family,dtype):
        # check that family,dytype = 2,2
        pass

    def bind(self,address):
        self.myipaddr=address[0]
        self.myport = address[1]
        return

    def send_to(address,msg):
        self.toipaddr = address[0]
        self.toport = address[1]
        self.msg = msg
