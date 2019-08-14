import socket


class networking:
    def __init__(self):
        pass

    def listen(self):
        host = "0.0.0.0"
        port = 5555
        addr = (host, port)
        buf = 1024
        TCPSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCPSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # enable reuse of address
        TCPSock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1) # enable keepalives
        TCPSock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 5) # time after which keepalive starts sending probes
        TCPSock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3) # keepalive probe intervals
        TCPSock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 40) # how often the server will retry. this all has to be on the clients of course.
        TCPSock.bind(addr)
        TCPSock.listen()
        print("starting to listen")
        while True:
            (conn, ipaddr) = TCPSock.accept()
            print("accepted connection from {}".format(ipaddr))
            print("waiting for data")
            data = str(conn.recv(buf).decode())
            print(data)
            conn.sendall("heart".encode())

