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
        self.num_client = -1
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

    def threaded_client(self, con: socket.socket, client_id: int):
        # first connect from client -> send back client id
        con.send(client_id.to_bytes(self.header_length, byteorder='big'))
        game_id = client_id // 2

        self.boards[game_id] = chess.Board() if (client_id % 2 == 1) else None
        self.game_states[game_id] = 'Ready' if (client_id % 2 == 1) else 'Not Ready'

        while True:
            try:
                opponent_id = client_id + 1 if (client_id % 2 == 0) else client_id - 1
                if opponent_id not in self.connecting_clients and self.game_states[game_id] == 'Ready':
                    self.game_states[game_id] = 'Disconnect'

                receive_data = self.receive(con)
                board = self.boards[game_id]
                if self.is_new_data(board, receive_data):
                    self.boards[game_id] = receive_data

                self.send(con, {
                    'board': self.boards[game_id],
                    'state': self.game_states[game_id]
                })
            except Exception as er:
                self.logger.error(str(er))
                break

        self.connecting_clients.remove(client_id)
        self.logger.info(f'Client {client_id} disconnected')
        con.close()

    # send data length first, data second
    def send(self, con: socket.socket, data):
        send_data = pickle.dumps(data)
        send_length = len(send_data)
        con.send(send_length.to_bytes(self.header_length, byteorder='big'))
        con.sendall(send_data)

    # receive data length first, data second
    def receive(self, con: socket.socket):
        receive_length = int.from_bytes(con.recv(self.header_length), byteorder='big')
        receive_data = pickle.loads(con.recv(receive_length))
        return receive_data

    def start(self):
        self.server_socket.listen()
        self.logger.info("Waiting for connection, server started")
        while True:
            con, addr = self.server_socket.accept()
            self.num_client += 1
            self.connecting_clients.add(self.num_client)
            self.logger.info(f'Client {self.num_client} connected')
            thread = threading.Thread(target=self.threaded_client, args=(con, self.num_client),
                                      name=f'Client{self.num_client}')
            thread.start()
            self.logger.info(f'Number of current active clients: {threading.active_count() - 1}')

    @staticmethod
    def is_new_data(board: chess.Board, receive_data: chess.Board):
        try:
            # current nth move make by both client (start from 0)
            board_move = (board.fullmove_number - 1) * 2 + int(not board.turn)
            data_move = (receive_data.fullmove_number - 1) * 2 + int(not receive_data.turn)
        except Exception as e:
            board_move = data_move = -1

        # board_move < data_move -> update new board | board_move - data_move >= 4 -> reset board
        if board_move < data_move or board_move - data_move >= 4:
            return True
        return False


if __name__ == '__main__':
    server = Server()
    server.start()
