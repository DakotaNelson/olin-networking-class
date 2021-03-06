from transport_layer import morse_socket
import CN_Sockets

lanNAT = {'83':'ES','73':'EI','69':'EE','84':'ET'}
wanNAT = {'T2':'51','T3':'52','IR':'82','T1':'50','II':'73','IN':'78','ID':'68'}
# NOTE: wanNAT will have collisions VERY SOON. This is a stopgap that relies on
# having very few IP addresses and thus no collisions of the last IP entry.
portLookup = {'84':'A','69':'11','73':'E'}

socket, AF_INET, SOCK_DGRAM, timeout = CN_Sockets.CN_Socket, CN_Sockets.AF_INET, CN_Sockets.SOCK_DGRAM, CN_Sockets.timeout

lan = morse_socket(2,2)
with socket(AF_INET, SOCK_DGRAM) as wan:
#wan = morse_socket.morse_socket(2,2)

    wan.settimeout(0.1)
    lan.settimeout(0.1)

    lan.network.router = True

    while True:
        try:
            msg,addr = lan.recvfrom()
        except:
            #print("No LAN messages.")
            msg = None
            pass

        if msg is not None:
            print("Got a message from the LAN.")
            print([msg,addr])
            destip = address[0]
            destip = destip.split('.') # split the IP into its component octets
            #destport = address[1]
            print(address)
            groupCode = str(destip[-2])
            deviceCode = str(destip[-1])
            if groupcode is not '69':
                destmac = wanNAT[deviceCode]
                destport = portLookup[groupCode]
                print("Sending message to:")
                print(msg)
                print([destmac,destport])
                msglen = changeBase(len(msg)+4,36)
                # |IPTO|IPFROM|PROTOCOL|LEN|PORTTO|PORTFROM|MSG|
                wan.sendto(bytearray(ipto+ipfrom+E+msglen+destport+'11'+msg),[destmac,destport])

        try:
            bytearray_msg, addr = wan.recvfrom(1024)
            msg = bytearray_msg.decode("UTF-8")
        except:
            #print("No WAN messages.")
            msg = None
            pass

        if msg is not None:
        # determine recipient of the message
        # if it's to E, route it into the network
            print("Got a message from the WAN.")
            print([msg,addr])
            destip = addr[0]
            destport = addr[1]
            destip = destip.split('.') # split the IP into its component bytes
            groupCode = str(destip[-2])
            deviceCode = str(destip[-1])
            if groupCode is '69':
                destmac = lanNAT[deviceCode]
                print("Sending message to:")
                print(msg)
                print([destmac,11])
                lan.sendto(bytearray(msg),[destmac,11])




def changeBase(x,base):
    y = ''
    lessThanBase = x < base
    while x//base !=0 or lessThanBase:
        if(x%base != 0):
            y=chr(self.getChar(x//base))+chr(self.getChar(x%base))+y
        else:
            y=chr(self.getChar(x//base))+'0'+y
        x//=base
        lessThanBase = False
    if len(y) == 1:
        return '0'+y
    return y

def getChar(x):
    if x< 10: return x+48
    else: return x+55
