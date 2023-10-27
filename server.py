import os
import socket
import pickle
import threading
from datetime import datetime

import chess
from utility import get_logger, Message
from collections import deque


class Server:
    def __init__(self, ip='127.0.0.1', port=5555):
        self.logger = get_logger()
        self.ip = ip
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lock = threading.Lock()
        self.num_game = 0
        self.games = {}
        self.client_queue = deque()
        self.num_client = 0
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

    def client_play_handler(self, con: socket.socket, client_id: int):
        con.sendall(client_id.to_bytes(self.header_length, byteorder='big'))
        self.client_queue.append(client_id)

        while True:
            try:
                receive_data = self.receive(con)
                if receive_data is None:
                    break

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

        self.disconnect(client_id)
        con.close()

    # disconnect from server
    def disconnect(self, client_id):
        game_id = self.connecting_clients[client_id]['game_id']
        # check if client already in a game
        if game_id is None:
            self.client_queue.remove(client_id)
        else:
            self.games[game_id]['state'] = Message.DISCONNECT
            white_id = self.games[game_id]['white']
            black_id = self.games[game_id]['black']
            if white_id is not None and black_id is not None:
                self.save_game_replay(game_id)

            if white_id == client_id:
                self.games[game_id]['white'] = None
                if black_id is not None:
                    self.send(self.connecting_clients[black_id]['connection'], self.games[game_id])
            else:
                self.games[game_id]['black'] = None
                if white_id is not None:
                    self.send(self.connecting_clients[white_id]['connection'], self.games[game_id])

        self.connecting_clients.pop(client_id)
        self.logger.info(f'Client {client_id} disconnected')

    def save_game_replay(self, game_id: int):
        current_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        file_path = f'replay/{current_time}_{game_id}.pkl'
        with open(file_path, 'wb') as file:
            pickle.dump(self.games[game_id], file)

    # send data length first, data second
    def send(self, con: socket.socket, data):
        try:
            send_data = pickle.dumps(data)
            send_length = len(send_data)
            con.sendall(send_length.to_bytes(self.header_length, byteorder='big'))
            con.sendall(send_data)
        except Exception as er:
            self.logger.error(str(er))

    # receive data length first, data second
    def receive(self, con: socket.socket):
        try:
            receive_length = int.from_bytes(con.recv(self.header_length), byteorder='big')
            receive_data = pickle.loads(con.recv(receive_length))
            return receive_data
        except Exception as er:
            self.logger.error(er)

    # matchmaking 2 player
    def queue_handle(self):
        while True:
            # match 2 player that are in queue
            if len(self.client_queue) >= 2:
                white = self.client_queue.popleft()
                black = self.client_queue.popleft()
                game_id = self.num_game
                self.num_game += 1
                self.games[game_id] = {
                    'board': chess.Board(),
                    'state': Message.READY,
                    'white': white,
                    'black': black
                }
                self.connecting_clients[white]['game_id'] = game_id
                self.connecting_clients[black]['game_id'] = game_id

                # inform both player that game is ready
                self.games[game_id]['state'] = Message.READY
                self.send(self.connecting_clients[white]['connection'], self.games[game_id])
                self.send(self.connecting_clients[black]['connection'], self.games[game_id])

    def locked_action(self, func, args):
        with self.lock:
            func(*args)

    def start(self):
        self.server_socket.listen()
        self.logger.info("Waiting for connection, server started")
        queue_handler_thread = threading.Thread(target=self.queue_handle)
        queue_handler_thread.daemon = True
        queue_handler_thread.start()

        while True:
            con, addr = self.server_socket.accept()
            client_id = self.num_client

            self.connecting_clients[client_id] = {
                'connection': con,
                'game_id': None
            }

            thread = threading.Thread(target=self.client_play_handler, args=(con, client_id))
            thread.start()

            self.logger.info(f'Client {client_id} connected')
            self.logger.info(f'Number of current active clients: {threading.active_count() - 2}')
            self.num_client += 1


if __name__ == '__main__':
    server = Server()
    server.start()
