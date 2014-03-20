import morse_socket
import morse_ethernet

lan = morse_socket(lan.AF_INET,lan.SOCK_DGRAM)
wan = morse_ethernet()

lan.bind(["E.EE",80]) # this is universal among all E team routers
wan.bind([wanip,wanport])
# Since we're doing all broadcasts, this may not be necessary
# (i.e. only if we want to address the router itself for some reason)

lan.settimeout(0.1)
wan.settimeout(0.1)

while True:
    try:
        addr,msg = lan.recvfrom()
    except timeout:
        #print("No LAN messages.")
    if msg is not None:
        # determine recipient of the message here
        # if it's to a groupcode other than E, route it out
        wan.sendto(msg,[destip,destport])

    try:
        addr,msg = wan.recvfrom()
    except timeout:
        #print("No WAN messages.")
    if msg is not None:
        # determine recipient of the message here
        # if it's to E, route it in to the network
        lan.sendto(msg,[destip,destport])
