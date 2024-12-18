import socket
from _thread import *
import pickle
from game import Game

server = "192.168.1.4"
port = 5010

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen()
print("Waiting for a connection, Server Started")

connected = set()
games = {}
idCount = 0
leaderboard = {}

def update_leaderboard(player_addr, won):
    """Update leaderboard data for a player."""
    global leaderboard

    if player_addr not in leaderboard:
        leaderboard[player_addr] = {"streak": 0}

    if won:
        leaderboard[player_addr]["streak"] += 1
    else:
        leaderboard[player_addr]["streak"] = 0

    # Sort leaderboard by streak in descending order
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1]["streak"], reverse=True)
    leaderboard = dict(sorted_leaderboard)

def threaded_client(conn, player, gameId):
    global idCount
    conn.send(str.encode(str(player)))

    reply = ""
    player_addr = str(conn.getpeername())  # Get client address

    while True:
        try:
            data = conn.recv(4096).decode()

            if gameId in games:
                game = games[gameId]

                if not data:
                    break
                else:
                    if data == "reset":
                        game.resetMove()
                    elif data != "get":
                        game.play(player, data)

                    if game.bothMoved():
                        winner = game.win()
                        if winner == player:
                            update_leaderboard(player_addr, won=True)
                        elif winner != -1:  # If it's not a tie, update opponent's loss
                            opponent_addr = str(conn.getpeername())  # Simulate opponent
                            update_leaderboard(opponent_addr, won=False)

                    # Add leaderboard to the game data
                    game.leaderboard = list(leaderboard.items())[:3]

                    conn.sendall(pickle.dumps(game))
            else:
                break
        except:
            break

    print("Lost connection")
    try:
        del games[gameId]
        print("Closing Game", gameId)
    except:
        pass
    idCount -= 1
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    idCount += 1
    p = 0
    gameId = (idCount - 1)//2
    if idCount % 2 == 1:
        games[gameId] = Game(gameId)
        print("Creating a new game...")
    else:
        games[gameId].ready = True
        p = 1


    start_new_thread(threaded_client, (conn, p, gameId))


