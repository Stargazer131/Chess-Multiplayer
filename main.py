from client import Client
from game import Game

client = Client()
game = Game(client, client.client_id)
game.run_game()
