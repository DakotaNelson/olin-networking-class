from morse_socket import morse_socket
sock = morse_socket(morse_socket.AF_INET,morse_socket.SOCK_DGRAM)
mac = input("Enter the server's two character MAC:")
mac = mac.upper()
sock.bind(["EI",11])
print("This node's address is EI.")
while True:
    msg = input("Enter a message to send to the server, composed of only alphanumerics... and no spaces or punctuation:")
    sock.sendto(bytearray(msg.upper()),[mac,11])
    msg,address = sock.recvfrom()
    while msg is not None:
        print("Recieved message \"" + msg "\" from" + str(address))
        msg,address = sock.recvfrom()
