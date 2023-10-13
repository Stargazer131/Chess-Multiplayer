import socket
import pickle
from _thread import start_new_thread
import chess


class Server:
    def __init__(self, ip='127.0.0.1', port=5555):
        self.ip = ip
        self.port = port
        # AF_INET -> IPV4 | SOCK_STREAM -> TCP | SOCK_DGRAM -> UDP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.num_player = -1
        self.boards = {}
        self.game_states = {}
        self.connecting_clients = set()
        self.bind_socket()

    def bind_socket(self):
        try:
            self.server_socket.bind((self.ip, self.port))
            return True
        except socket.error as e:
            print(e)
            return False

    def threaded_client(self, con: socket.socket, player_id: int):
        # first connect from client -> send back player id
        con.send(str(player_id).encode())
        game_id = player_id // 2

        self.boards[game_id] = chess.Board() if (player_id % 2 == 1) else None
        self.game_states[game_id] = 'Ready' if (player_id % 2 == 1) else 'Not Ready'

        while True:
            try:
                opponent_id = player_id + 1 if (player_id % 2 == 0) else player_id - 1
                if opponent_id not in self.connecting_clients and self.game_states[game_id] == 'Ready':
                    self.game_states[game_id] = 'Disconnect'
                data = pickle.loads(con.recv(4096))
                board = self.boards[game_id]

                try:
                    # current nth move make by both player (start from 0)
                    board_move = (board.fullmove_number - 1) * 2 + int(not board.turn)
                    data_move = (data.fullmove_number - 1) * 2 + int(not data.turn)
                except Exception as e:
                    board_move = data_move = -1
                    print(e)

                # board_move < data_move -> update new board | board_move - data_move >= 4 -> reset board
                if board_move < data_move or board_move - data_move >= 4:
                    self.boards[game_id] = data

                con.sendall(pickle.dumps({
                    'board': self.boards[game_id],
                    'state': self.game_states[game_id]
                }))
            except Exception as er:
                print(er)
                break

        self.connecting_clients.remove(player_id)
        print(f'Player {player_id} disconnected')
        con.close()

    def start(self):
        self.server_socket.listen()
        print("Waiting for connection, server started")
        while True:
            con, addr = self.server_socket.accept()
            self.num_player += 1
            self.connecting_clients.add(self.num_player)
            print(f'Player {self.num_player} connected')
            start_new_thread(self.threaded_client, (con, self.num_player))


if __name__ == '__main__':
    server = Server()
    server.start()
