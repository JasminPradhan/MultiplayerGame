import socket
from _thread import *
import pickle
from game import Game

server = "192.168.184.165"
port = 5050

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen()
print("Waiting for a connection, Server Started")

connected=set()
games={}
idCount=0

def threaded_client(conn, player, gameId):
    global idCount
    conn.send(str.encode(str(player)))

    reply=""

    while True:
        try:
            data = conn.recv(2048*8).decode('utf-8')


            if gameId in games:
                game=games[gameId]
                # print(type(data))
                if not data:
                    break
                else:
                    if data=="reset":
                        game.resetMove()
                    elif data != "get":
                        game.play(player,data)

                    conn.sendall(pickle.dumps(game))

            else:
                break
        except:
            break


    print("Lost connection")

    try:
        del games[gameId]
        print("closing game", gameId)
    except:
        pass
    idCount-=1
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    idCount+=1
    p=0

    gameId = (idCount-1)//2

    if idCount%2==1:
        games[gameId]=Game(gameId) #gameId which is the key in games is now equals to the new game object
        print("Creating an new game.....")
    else:
        games[gameId].ready=True
        p=1
    start_new_thread(threaded_client, (conn,p, gameId))
