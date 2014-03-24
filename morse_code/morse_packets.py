class IP_Packet:
    def __init__(self):
        self.version = 0
        # Internet Protocol Version
        self.ihl = 5 # TODO fix this
        # Internet Header Length is the length of this header in 32 bit words,
        # and thus points to the beginning of the data. The minimum value is 5.
        self.type_of_service = 1
        # Type of Service provides an indication of the quality of service.
        self.length = None
        # The length of the datagram, measured in octets, including header and
        # data.
        self.identification = None
        # An ID value assigned by the sender to aid in assembling the fragments
        # of a datagram.
        self.flags = None # TODO should be 010 - not sure of endianism
        # Various control flags.
        # Bit 0: reserved, must be zero.
        # Bit 1: 0 = may fragment, 1 = don't fragment
        # Bit 2: 0 = last gragment, 1 = more fragments
        self.fragmentation_offset = 0
        # Indicates where in the datagram this fragment belongs.
        self.ttl = None
        # Max time the datagram is allowed to remain in the internet system.
        # If zero, datagram must be destroyed.
        self.protocol = None
        # Indicates the next level protocol used in the data portion of the
        # internet datagram.
        self.cksum = None
        # Checksum of the header only. Must be recomputed and verified at each
        # point, since some fields will change (e.g. TTL)
        self.source = None
        # Source address.
        self.destination = None
        # Destination address.
        self.options = None
        # Optional field.
        self.padding = None
        # Padding.
        self.data = None
        # The packet's data.

    def writeOut(self,protocol):
        # write all the data fields into a long string suitable for transmission
        # also do error checking
        if protocol == "morse":
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

            return str(self.ttl)+str(self.destination)+str(self.source)+str(self.length)+str(self.data)+str(self.cksum)

    def writeIn(self,packet):
        # take a text packet and parse it into this object
        # also do error checking

class UDP_Packet:
    def __init__(self):
        self.source = None
        # Source address.
        self.destination = None
        # Destination address.
        self.protocol = None
        # Indicates the next level protocol.
        self.data = None
        # Packet's payload.

    def writeOut(self):
        # write all the data fields into a long string suitable for transmission
        # also do error checking

    def writeIn(self,packet):
        # take a packet, parse it into this object
        # also error check
