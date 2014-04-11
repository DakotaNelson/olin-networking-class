from morse_socket import morse_socket
sock = morse_socket(morse_socket.AF_INET,morse_socket.SOCK_DGRAM)
sock.network.off()
mac = input("Enter the target server's two character MAC:")
mac = mac.upper()
sock.bind(["EI",11])
while True:
    msg = input("Enter a message to send to the server, composed of only alphanumerics... and no spaces or punctuation:")
    print(msg)
    msg = str(msg).encode('utf-8').upper()
    sock.sendto(bytearray(msg),[mac,11])
    msg,address = sock.recvfrom()
    while msg is not None:
        print("Recieved message \"" + msg + "\" from" + str(address))
        msg,address = sock.recvfrom()
