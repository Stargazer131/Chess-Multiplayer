import socket
import pickle
from _thread import start_new_thread

import chess


board = chess.Board()


def threaded_client(con: socket.socket, player_id: int):
    con.send(str(player_id).encode())

    global board
    while True:
        data = pickle.loads(con.recv(4096*8))
        try:
            if not data:
                break

            res1 = (board.fullmove_number - 1) * 2
            if board.turn:
                res1 += 1
            else:
                res1 += 2

            res2 = (data.fullmove_number - 1) * 2
            if data.turn:
                res2 += 1
            else:
                res2 += 2

            print(res1, res2)
            if res1 < res2:
                board = data
            con.sendall(pickle.dumps(board))
        except:
            break
    con.close()


class Server:
    def __init__(self, ip='127.0.0.1', port=5555):
        self.ip = ip
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.num_player = -1
        self.bind_socket()

    def bind_socket(self):
        try:
            self.server_socket.bind((self.ip, self.port))
            return True
        except socket.error as e:
            print(e)
            return False

    def start(self):
        while True:
            self.server_socket.listen()
            print("Waiting for connection, server started")
            con, addr = self.server_socket.accept()

            self.num_player += 1
            start_new_thread(threaded_client, (con, self.num_player))


server = Server()
server.start()
