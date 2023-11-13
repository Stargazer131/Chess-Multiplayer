import socket
import pickle
import threading
import time
from datetime import datetime

import chess

import utility
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
        self.num_replays = 0
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
                self.games[game_id]['board'] = receive_data['board']
                self.games[game_id]['moves_information'] = receive_data['moves_information']
                if self.games[game_id]['board'].is_checkmate():
                    if self.games[game_id]['board'].turn:
                        self.games[game_id]['winner'] = 'BLACK'
                    else:
                        self.games[game_id]['winner'] = 'WHITE'

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

    def countdown_game(self, game_id: int):
        while self.games[game_id]['state'] == Message.READY:
            try:
                self.games[game_id]['time']['game'] -= 1
                time.sleep(1)
            except Exception as er:
                self.logger.error(str(er))

    def countdown_white(self, game_id: int):
        while self.games[game_id]['state'] == Message.READY:
            try:
                if self.games[game_id]['board'].turn:
                    self.games[game_id]['time']['white'] -= 1
                    time.sleep(1)
            except Exception as er:
                self.logger.error(str(er))

    def countdown_black(self, game_id: int):
        while self.games[game_id]['state'] == Message.READY:
            try:
                if not self.games[game_id]['board'].turn:
                    self.games[game_id]['time']['black'] -= 1
                    time.sleep(1)
            except Exception as er:
                self.logger.error(str(er))

    def disconnect_player(self, player_id):
        game_id = self.connecting_players[player_id]['game_id']
        # check if client already in a game
        if game_id is None:
            self.player_queue.remove(player_id)
        else:
            self.games[game_id]['state'] = Message.DISCONNECT
            white_id = self.games[game_id]['white']
            black_id = self.games[game_id]['black']
            if self.games[game_id]['winner'] == '':
                if self.games[game_id]['white'] == player_id:
                    self.games[game_id]['winner'] = 'BLACK'
                else:
                    self.games[game_id]['winner'] = 'WHITE'

            if white_id is not None and black_id is not None:
                self.save_game_replay(game_id)

            if white_id == player_id:
                self.games[game_id]['white'] = None
                try:
                    self.send(self.connecting_players[black_id]['connection'], self.games[game_id])
                except Exception as er:
                    self.logger.error(er)
            else:
                self.games[game_id]['black'] = None
                try:
                    self.send(self.connecting_players[white_id]['connection'], self.games[game_id])
                except Exception as er:
                    self.logger.error(er)

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
            return True
        except Exception as er:
            self.logger.error(str(er))
            return False

    # receive data length first, data second
    def receive(self, con: socket.socket):
        try:
            receive_length = int.from_bytes(con.recv(self.header_length), byteorder='big')
            receive_data = pickle.loads(con.recv(receive_length))
            return receive_data
        except Exception as er:
            self.logger.error(er)

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
                    'game_id': game_id,
                    'board': chess.Board(),
                    'state': Message.READY,
                    'moves_information': [],
                    'white': white,
                    'black': black,
                    'viewers': 0,
                    'winner': '',
                    'time': {
                        'game': 60*20,
                        'white': 60*15,
                        'black': 60*15
                    }
                }
                self.connecting_players[white]['game_id'] = game_id
                self.connecting_players[black]['game_id'] = game_id

                # inform both player that game is ready
                self.send(self.connecting_players[white]['connection'], self.games[game_id])
                self.send(self.connecting_players[black]['connection'], self.games[game_id])

                # start the timer
                game_timer_thread = threading.Thread(target=self.countdown_game, args=(game_id,), daemon=True)
                game_timer_thread.start()
                white_timer_thread = threading.Thread(target=self.countdown_white, args=(game_id,), daemon=True)
                white_timer_thread.start()
                black_timer_thread = threading.Thread(target=self.countdown_black, args=(game_id,), daemon=True)
                black_timer_thread.start()

    def client_view(self, con: socket.socket, viewer_id: int):
        selection = Message.NO_SELECTION
        while True:
            try:
                if selection == Message.NO_SELECTION:
                    message = self.receive(con)
                    if message == Message.ALL_DATA:
                        self.send(con, self.get_active_games())
                    else:
                        selection = message
                else:
                    self.games[selection]['viewers'] += 1
                    while True:
                        if self.receive(con) == Message.VIEWING:
                            self.send(con, self.games[selection])
                        else:
                            self.games[selection]['viewers'] -= 1
                            break
                    selection = Message.NO_SELECTION
                    break
            except Exception as er:
                self.logger.error(str(er))
                break

        self.logger.info(f'Viewer {viewer_id} disconnected')
        con.close()

    # return active game id and current viewer number
    def get_active_games(self):
        active_games = []
        for game_id in self.games:
            if self.games[game_id]['state'] == Message.READY:
                active_games.append((game_id, self.games[game_id]['viewers']))
        return active_games

    def client_replay(self, con: socket.socket, replay_id: int):
        selection = Message.NO_SELECTION
        while True:
            try:
                if selection == Message.NO_SELECTION:
                    message = self.receive(con)
                    if message == Message.ALL_DATA:
                        self.send(con, self.get_all_games())
                    else:
                        selection = message
                else:
                    with open(f'replay/{selection}.pkl', 'rb') as file:
                        send_data = pickle.load(file)
                    self.send(con, send_data)
                    selection = Message.NO_SELECTION
            except Exception as er:
                self.logger.error(str(er))
                break

        self.logger.info(f'Replay {replay_id} disconnected')
        con.close()

    # return all played games
    @staticmethod
    def get_all_games():
        all_games = [file_name[:-4] for file_name in utility.get_all_file_names('replay')]
        return all_games

    def start(self):
        self.server_socket.listen()
        self.logger.info("Waiting for connection, server started")
        player_queue_handler_thread = threading.Thread(target=self.player_queue_handle, daemon=True)
        player_queue_handler_thread.start()

        while True:
            con, addr = self.server_socket.accept()
            action = self.receive(con)

            # for play client
            if action == Message.PLAY:
                client_id = self.num_players
                self.send(con, client_id)

                self.connecting_players[client_id] = {'connection': con, 'game_id': None}
                thread = threading.Thread(target=self.client_play, args=(con, client_id))
                thread.start()
                self.player_queue.append(client_id)

                self.logger.info(f'Player {client_id} connected')
                self.num_players += 1

            # for view client
            elif action == Message.VIEW:
                client_id = self.num_viewers
                self.send(con, client_id)

                thread = threading.Thread(target=self.client_view, args=(con, client_id))
                thread.start()

                self.logger.info(f'Viewer {client_id} connected')
                self.num_viewers += 1

            # for replay client
            else:
                client_id = self.num_replays
                self.send(con, client_id)

                thread = threading.Thread(target=self.client_replay, args=(con, client_id))
                thread.start()

                self.logger.info(f'Replay {client_id} connected')
                self.num_replays += 1


if __name__ == '__main__':
    server = Server()
    server.start()
