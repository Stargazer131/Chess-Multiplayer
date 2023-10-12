import pickle
import socket

from game import Game


class Client:
    def __init__(self, server_ip='127.0.0.1', server_port=5555):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_id = int(self.connect())

    def connect(self):
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            return self.client_socket.recv(128).decode()
        except:
            pass

    def send(self, data):
        try:
            self.client_socket.sendall(pickle.dumps(data))
            return pickle.loads(self.client_socket.recv(4096))
        except socket.error as er:
            print(er)


if __name__ == '__main__':
    client = Client()
    game = Game(client, client.client_id)
    game.run_game()