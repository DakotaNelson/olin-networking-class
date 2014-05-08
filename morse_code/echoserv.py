from transport_layer import morse_socket
from threading import Thread
from time import sleep

# Set up our socket
sock = morse_socket(morse_socket.AF_INET,morse_socket.SOCK_DGRAM)
sock.network.off()
sock.bind(["EE",11])

# Function to recieve messages
def recv():
    while True:
        try:
            msg,address = sock.recvfrom()
        except:
            msg = None
        while msg is not None:
            print("Recieved message \"" + msg + "\" from " + str(address))
            try:
                msg,address = sock.recvfrom()
            except:
                msg = None
        sleep(10)  # wait a while before we check again 

# Get ready to recieve
recvThread = Thread(target=recv)
recvThread.daemon = True
recvThread.start()

# Pick an address to send to
#mac = input("Enter the target server's two character MAC: ")
#mac = mac.upper()

while True:
    userinput = input("Enter a target address, a comma, then a message composed of only alphanumerics (EE,msg): \n")
    userinput = userinput.split(',')
    mac = userinput[0].upper().strip()
    msg = userinput[1].upper().strip()
    mac = ''.join(mac)
    msg = ''.join(msg)
    if msg.isalnum() and mac.isalpha() and len(mac) is 2:
        msg = str(msg).encode('utf-8')
        sock.sendto(bytearray(msg),[mac,11])
    else: print("Please enter only alpha characters for the MAC and only alphanumerics for the message.")
