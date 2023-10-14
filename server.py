import socket
import pickle
import threading
import chess
from utility import get_logger, Message
from collections import deque


class Server:
    def __init__(self, ip='127.0.0.1', port=5555):
        self.logger = get_logger()
        self.ip = ip
        self.port = port
        # AF_INET -> IPV4 | SOCK_STREAM -> TCP | SOCK_DGRAM -> UDP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.num_client = 0
        self.num_game = 0
        self.games = {
            0: {
                'board': None,
                'state': Message.IN_QUEUE,
                'white': None,
                'black': None
            }
        }
        self.client_queue = deque()
        # store client id and its corresponding game id
        self.connecting_clients = {}
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

        while True:
            try:
                receive_data = self.receive(con)
                game_id = self.connecting_clients[client_id]

                # if still in queue, send default waiting data
                if not game_id:
                    send_data = self.games[0]
                # find a game id -> not in queue
                else:
                    board = self.games[game_id]['board']
                    # noinspection PyTypeChecker
                    if self.is_new_data(board, receive_data):
                        self.games[game_id]['board'] = receive_data
                    send_data = self.games[game_id]

                self.send(con, send_data)
            except Exception as er:
                self.logger.error(str(er))
                break

        game_id = self.connecting_clients[client_id]
        if game_id:
            self.games[game_id]['state'] = Message.DISCONNECT
            if self.games[game_id]['white'] == client_id:
                self.games[game_id]['white'] = None
            else:
                self.games[game_id]['black'] = None

        if client_id in self.client_queue:
            self.client_queue.remove(client_id)
        self.connecting_clients.pop(client_id)
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

    def queue_handle(self):
        while True:
            if len(self.client_queue) >= 2:
                white = self.client_queue.popleft()
                black = self.client_queue.popleft()
                self.num_game += 1

                # noinspection PyTypeChecker
                self.games[self.num_game] = {
                    'board': chess.Board(),
                    'state': Message.READY,
                    'white': white,
                    'black': black
                }
                self.connecting_clients[white] = self.num_game
                self.connecting_clients[black] = self.num_game

    def start(self):
        self.server_socket.listen()
        self.logger.info("Waiting for connection, server started")
        queue_handler_thread = threading.Thread(target=self.queue_handle)
        queue_handler_thread.daemon = True
        queue_handler_thread.start()

        while True:
            con, addr = self.server_socket.accept()
            # this will be client id
            self.num_client += 1
            self.client_queue.append(self.num_client)
            self.connecting_clients[self.num_client] = None

            thread = threading.Thread(target=self.threaded_client, args=(con, self.num_client))
            thread.start()

            self.logger.info(f'Client {self.num_client} connected')
            self.logger.info(f'Number of current active clients: {threading.active_count() - 1}')

    @staticmethod
    def is_new_data(board: chess.Board, receive_data: chess.Board):
        try:
            # current nth move make by both client (start from 0)
            board_move = (board.fullmove_number - 1) * 2 + int(not board.turn)
            data_move = (receive_data.fullmove_number - 1) * 2 + int(not receive_data.turn)
        except AttributeError:
            board_move = data_move = -1

        # board_move < data_move -> update new board | board_move - data_move >= 4 -> reset board
        if board_move < data_move or board_move - data_move >= 4:
            return True
        return False


if __name__ == '__main__':
    server = Server()
    server.start()
