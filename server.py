import socket
from _thread import start_new_thread
import sys

server = "192.168.203.165"
port = 5555


s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server,port))

except socket.error as e:
    print(e)


# no args means unlimited connection
# we need 2 users to get connected...so we will pass 2
s.listen(2)

print("Waiting for a connection, server started")

def threaded_client(conn):

    conn.send(str.encode("Connected"))
    reply=""
    while True:
        try:
            # larger the size, longer the processing time
            data=conn.recv(2048)
            reply=data.decode("utf-8")

            if not data:
                print("Disconnected")
                break
            else:
                print("Received: ", reply)
                print("Sending: ", reply)

            conn.sendall(str.encode(reply))
        except conn.error as e:
            print(e)

    print("Lost connection")
    conn.close()

while True:
    # addr : IP address
    conn, addr=s.accept()
    print("connected to:",addr)

    start_new_thread(threaded_client,(conn,))