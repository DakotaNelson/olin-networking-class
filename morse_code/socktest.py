from morse_socket import morse_socket
sock = morse_socket(morse_socket.AF_INET,morse_socket.SOCK_DGRAM)
sock.bind(["EE",11])
sock.network.off()
sock.sendto(bytearray('H'.encode('utf-8')),['EI',11])
