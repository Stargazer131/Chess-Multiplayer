import socket
import pickle
import threading
import chess
from utility import get_logger


class Server:
    def __init__(self, ip='127.0.0.1', port=5555):
        self.logger = get_logger()
        self.ip = ip
        self.port = port
        # AF_INET -> IPV4 | SOCK_STREAM -> TCP | SOCK_DGRAM -> UDP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.num_player = -1
        self.boards = {}
        self.game_states = {}
        self.connecting_clients = set()
        self.header_length = 4
        self.bind_socket()

    def bind_socket(self):
        try:
            self.server_socket.bind((self.ip, self.port))
            return True
        except socket.error as e:
            self.logger.error(str(e))
            return False

    def threaded_client(self, con: socket.socket, player_id: int):
        # first connect from client -> send back player id
        con.send(player_id.to_bytes(self.header_length, byteorder='big'))
        game_id = player_id // 2

        self.boards[game_id] = chess.Board() if (player_id % 2 == 1) else None
        self.game_states[game_id] = 'Ready' if (player_id % 2 == 1) else 'Not Ready'

        while True:
            try:
                opponent_id = player_id + 1 if (player_id % 2 == 0) else player_id - 1
                if opponent_id not in self.connecting_clients and self.game_states[game_id] == 'Ready':
                    self.game_states[game_id] = 'Disconnect'

                # receive data length first, data second
                receive_length = int.from_bytes(con.recv(self.header_length), byteorder='big')
                receive_data = pickle.loads(con.recv(receive_length))
                board = self.boards[game_id]

                try:
                    # current nth move make by both player (start from 0)
                    board_move = (board.fullmove_number - 1) * 2 + int(not board.turn)
                    data_move = (receive_data.fullmove_number - 1) * 2 + int(not receive_data.turn)
                except Exception as e:
                    board_move = data_move = -1

                # board_move < data_move -> update new board | board_move - data_move >= 4 -> reset board
                if board_move < data_move or board_move - data_move >= 4:
                    self.boards[game_id] = receive_data

                send_data = pickle.dumps({
                    'board': self.boards[game_id],
                    'state': self.game_states[game_id]
                })
                send_length = len(send_data)

                # send data length first, data second
                con.send(send_length.to_bytes(self.header_length, byteorder='big'))
                con.sendall(send_data)
            except Exception as er:
                self.logger.error(str(er))
                break

        self.connecting_clients.remove(player_id)
        self.logger.info(f'Player {player_id} disconnected')
        con.close()

    def start(self):
        self.server_socket.listen()
        self.logger.info("Waiting for connection, server started")
        while True:
            con, addr = self.server_socket.accept()
            self.num_player += 1
            self.connecting_clients.add(self.num_player)
            self.logger.info(f'Player {self.num_player} connected')
            thread = threading.Thread(target=self.threaded_client, args=(con, self.num_player),
                                      name=f'Player{self.num_player}')
            thread.start()
            self.logger.info(f'Number of current active players: {threading.active_count() - 1}')


if __name__ == '__main__':
    server = Server()
    server.start()
