class IP_Packet:
    def __init__(self):
        self.version = 0
        self.ihl = 5 # TODO fix this
        self.type_of_service = 1
        self.length = None
        self.ttl = None
        self.cksum = None
        self.source = None
        self.destination = None
        self.message = None # in practice this "message" is a UDP packet

    def writeOut(self):
        # write all the data fields into a long string suitable for transmission
        # also do error checking
        if self.length is None:
            return None
        if self.ttl is None:
            return None
        if self.cksum is None:
            return None
        if self.source is None:
            return None
        if self.destination is None:
            return None
        if self.message is None:
            return None

        return str(self.ttl)

    def writeIn(self,packet):
        # take a text packet and parse it into this object
        # also do error checking

class UDP_Packet:
    def __init__(self):
        self.source = None
        self.destination = None
        self.protocol = None
        self.message = None

    def writeOut(self):
        # write all the data fields into a long string suitable for transmission
        # also do error checking

    def writeIn(self,packet):
        # take a packet, parse it into this object
        # also error check
