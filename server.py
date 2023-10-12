import socket
import pickle
from _thread import start_new_thread
import chess

boards = {}


def threaded_client(con: socket.socket, player_id: int):
    global boards
    con.send(str(player_id).encode())
    game_id = player_id // 2
    if game_id not in boards:
        print(f'Game {game_id} created!')
        boards[game_id] = chess.Board()

    while True:
        try:
            data = pickle.loads(con.recv(4096))
            board = boards[game_id]

            board_move = (board.fullmove_number - 1) * 2
            if board.turn:
                board_move += 1
            else:
                board_move += 2
            data_move = (data.fullmove_number - 1) * 2
            if data.turn:
                data_move += 1
            else:
                data_move += 2

            if board_move < data_move or board_move - data_move >= 4:
                boards[game_id] = data
            con.sendall(pickle.dumps(boards[game_id]))
        except:
            break

    print(f'Player {player_id} disconnected')
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
        self.server_socket.listen()
        print("Waiting for connection, server started")
        while True:
            con, addr = self.server_socket.accept()
            self.num_player += 1
            print(f'Player {self.num_player} connected')
            start_new_thread(threaded_client, (con, self.num_player))


if __name__ == '__main__':
    server = Server()
    server.start()
