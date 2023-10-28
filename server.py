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
        # ---------------------------------------
        self.num_games = 0
        self.games = {}
        self.player_queue = deque()
        self.num_players = 0
        self.connecting_players = {}
        self.num_viewers = 0
        self.connecting_viewers = {}
        # ---------------------------------------
        self.header_length = 4
        self.bind_socket()

    def bind_socket(self):
        try:
            self.server_socket.bind((self.ip, self.port))
            return True
        except socket.error as e:
            self.logger.error(str(e))
            return False

    def client_play(self, con: socket.socket, player_id: int):
        while True:
            try:
                receive_data = self.receive(con)
                if receive_data is None:
                    break

                game_id = self.connecting_players[player_id]['game_id']
                self.games[game_id]['board'] = receive_data
                if player_id == self.games[game_id]['white']:
                    opponent_id = self.games[game_id]['black']
                else:
                    opponent_id = self.games[game_id]['white']

                send_data = self.games[game_id]
                self.send(self.connecting_players[opponent_id]['connection'], send_data)
            except Exception as er:
                self.logger.error(str(er))
                break

        self.disconnect_player(player_id)
        con.close()

    # disconnect from server
    def disconnect_player(self, player_id):
        game_id = self.connecting_players[player_id]['game_id']
        # check if client already in a game
        if game_id is None:
            self.player_queue.remove(player_id)
        else:
            self.games[game_id]['state'] = Message.DISCONNECT
            white_id = self.games[game_id]['white']
            black_id = self.games[game_id]['black']
            if white_id is not None and black_id is not None:
                self.save_game_replay(game_id)

            if white_id == player_id:
                self.games[game_id]['white'] = None
                if black_id is not None:
                    self.send(self.connecting_players[black_id]['connection'], self.games[game_id])
            else:
                self.games[game_id]['black'] = None
                if white_id is not None:
                    self.send(self.connecting_players[white_id]['connection'], self.games[game_id])

        self.connecting_players.pop(player_id)
        self.logger.info(f'Player {player_id} disconnected')

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

    def send_int(self, con: socket.socket, data: int):
        try:
            con.sendall(data.to_bytes(self.header_length, byteorder='big'))
            return True
        except Exception as er:
            print(er)
            return False

    def receive_int(self, con: socket.socket):
        try:
            return int.from_bytes(con.recv(self.header_length), byteorder='big')
        except Exception as er:
            print(er)

    # matchmaking 2 player
    def player_queue_handle(self):
        while True:
            # match 2 player that are in queue
            if len(self.player_queue) >= 2:
                white = self.player_queue.popleft()
                black = self.player_queue.popleft()
                game_id = self.num_games
                self.num_games += 1
                self.games[game_id] = {
                    'board': chess.Board(),
                    'state': Message.READY,
                    'white': white,
                    'black': black,
                    'viewers': 0
                }
                self.connecting_players[white]['game_id'] = game_id
                self.connecting_players[black]['game_id'] = game_id

                # inform both player that game is ready
                self.games[game_id]['state'] = Message.READY
                self.send(self.connecting_players[white]['connection'], self.games[game_id])
                self.send(self.connecting_players[black]['connection'], self.games[game_id])

    def client_view(self, con: socket.socket, viewer_id: int):
        selection = -1
        while True:
            try:
                if selection == -1:
                    self.send(con, self.get_active_games())
                    selection = self.receive_int(con)

            except Exception as er:
                self.logger.error(str(er))
                break

        con.close()

    # return active game id and current viewer number
    def get_active_games(self):
        active_games = []
        for game_id in self.games:
            if self.games[game_id]['state'] == Message.READY:
                active_games.append((game_id, self.games[game_id]['viewers']))
        return active_games

    def start(self):
        self.server_socket.listen()
        self.logger.info("Waiting for connection, server started")
        player_queue_handler_thread = threading.Thread(target=self.player_queue_handle)
        player_queue_handler_thread.daemon = True
        player_queue_handler_thread.start()

        while True:
            con, addr = self.server_socket.accept()
            action = self.receive(con)

            # for play client
            if action == Message.PLAY:
                client_id = self.num_players
                self.send_int(con, client_id)

                self.connecting_players[client_id] = {'connection': con, 'game_id': None}
                thread = threading.Thread(target=self.client_play, args=(con, client_id))
                thread.start()
                self.player_queue.append(client_id)

                self.logger.info(f'Player {client_id} connected')
                self.num_players += 1
            else:
                client_id = self.num_viewers
                self.send_int(con, client_id)

                self.connecting_viewers[client_id] = {'connection': con, 'game_id': None}
                thread = threading.Thread(target=self.client_view, args=(con, client_id))
                thread.start()

                self.logger.info(f'Viewer {client_id} connected')
                self.num_viewers += 1


if __name__ == '__main__':
    server = Server()
    server.start()
