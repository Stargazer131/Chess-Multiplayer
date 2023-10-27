import pickle
import socket


class Client:
    def __init__(self, server_ip='127.0.0.1', server_port=5555):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = server_ip
        self.server_port = server_port
        self.header_length = 4
        self.client_id = self.connect()

    def connect(self):
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            return int.from_bytes(self.client_socket.recv(self.header_length), byteorder='big')
        except Exception as er:
            print(er)
            return -1

    # send data length first, data second
    def send(self, data):
        try:
            send_data = pickle.dumps(data)
            send_length = len(send_data)
            self.client_socket.sendall(send_length.to_bytes(self.header_length, byteorder='big'))
            self.client_socket.sendall(send_data)
            return True
        except Exception as er:
            print(er)
            return False

    # receive data length first, data second
    def receive(self):
        try:
            receive_length = int.from_bytes(self.client_socket.recv(self.header_length), byteorder='big')
            receive_data = pickle.loads(self.client_socket.recv(receive_length))
            return receive_data
        except Exception as er:
            print(er)


if __name__ == '__main__':
    pass
