from morse_socket import morse_socket
sock = morse_socket(morse_socket.AF_INET,morse_socket.SOCK_DGRAM)
sock.bind(["EI",11])
print("Bound to address EI and ready to roll.")
