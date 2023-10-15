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
        self.games = {}
        self.client_queue = deque()
        # store client id and its corresponding game id, connection
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
                game_id = self.connecting_clients[client_id]['game_id']
                self.games[game_id]['board'] = receive_data
                if client_id == self.games[game_id]['white']:
                    opponent_id = self.games[game_id]['black']
                else:
                    opponent_id = self.games[game_id]['white']

                send_data = self.games[game_id]
                self.send(self.connecting_clients[opponent_id]['connection'], send_data)
            except Exception as er:
                self.logger.error(str(er))
                break

        # disconnect from server
        game_id = self.connecting_clients[client_id]['game_id']
        # check if client already in a game
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

    # matchmaking 2 player
    def queue_handle(self):
        # match 2 player that are in queue
        while True:
            if len(self.client_queue) >= 2:
                white = self.client_queue.popleft()
                black = self.client_queue.popleft()
                self.num_game += 1
                self.games[self.num_game] = {
                    'board': chess.Board(),
                    'state': Message.NOT_READY,
                    'white': white,
                    'black': black
                }
                self.connecting_clients[white]['game_id'] = self.num_game
                self.connecting_clients[black]['game_id'] = self.num_game

    def message_handle(self):
        while True:
            # using list for a copy -> avoid using iterator
            for game_id, game in list(self.games.items()):

                # send ready message for both client
                if game['state'] == Message.NOT_READY:
                    white_id, black_id = game['white'], game['black']
                    if not white_id or not black_id:
                        continue

                    white_game_id = self.connecting_clients[white_id]['game_id']
                    black_game_id = self.connecting_clients[black_id]['game_id']
                    if not white_game_id or not black_game_id:
                        continue

                    self.games[game_id]['state'] = Message.READY
                    self.send(self.connecting_clients[white_id]['connection'], self.games[game_id])
                    self.send(self.connecting_clients[black_id]['connection'], self.games[game_id])

                # inform other client if the other has left
                elif game['state'] == Message.DISCONNECT:
                    try:
                        if game['white'] and not game['black']:
                            self.send(self.connecting_clients[game['white']]['connection'], game)
                        elif not game['white'] and game['black']:
                            self.send(self.connecting_clients[game['black']]['connection'], game)
                    except Exception as er:
                        self.logger.error(str(er))

    def start(self):
        self.server_socket.listen()
        self.logger.info("Waiting for connection, server started")
        queue_handler_thread = threading.Thread(target=self.queue_handle)
        queue_handler_thread.daemon = True
        queue_handler_thread.start()

        message_handler_thread = threading.Thread(target=self.message_handle)
        message_handler_thread.daemon = True
        message_handler_thread.start()

        while True:
            con, addr = self.server_socket.accept()
            # this will be client id
            self.num_client += 1
            self.client_queue.append(self.num_client)
            self.connecting_clients[self.num_client] = {
                'connection': con,
                'game_id': None
            }

            thread = threading.Thread(target=self.threaded_client, args=(con, self.num_client))
            thread.start()

            self.logger.info(f'Client {self.num_client} connected')
            self.logger.info(f'Number of current active clients: {threading.active_count() - 1}')


if __name__ == '__main__':
    server = Server()
    server.start()
