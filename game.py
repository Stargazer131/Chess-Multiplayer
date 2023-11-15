import threading
import time

import chess
import pygame
import pygame.gfxdraw
from utility import get_image_resources, Message


class Game:
    def __init__(self, client):
        self.client = client
        self.state = Message.IN_QUEUE
        self.game_id = -1
        self.is_white = True
        self.player_time = 60 * 15
        self.previous_player_time = self.player_time
        self.moves_information = []
        self.game_time = 60 * 20
        pygame.init()
        self.WIDTH = 650
        self.HEIGHT = 550+70
        self.screen = pygame.display.set_mode([self.WIDTH, self.HEIGHT])
        pygame.display.set_caption('Chess.io')
        icon = pygame.image.load('img/icon.png')
        pygame.display.set_icon(icon)
        self.timer = pygame.time.Clock()
        self.fps = 60
        self.selection = ''

        # load in game piece images (queen, king, rook, bishop, knight, pawn) x 2
        img_resources = get_image_resources()
        self.piece_size = img_resources['piece_size']
        self.pawn_size = img_resources['pawn_size']
        self.small_piece_size = img_resources['small_piece_size']
        self.piece_images = img_resources['piece_images']
        self.small_piece_images = img_resources['small_piece_images']
        self.piece_list = img_resources['piece']

        # board
        self.board = chess.Board()
        self.title_size = 60

    @staticmethod
    def decode_coordinate(str_coord: str):
        x = 7 - (ord(str_coord[0]) - ord('a'))
        y = 8 - int(str_coord[1])
        return x, y

    @staticmethod
    def encode_coordinate(coord: tuple):
        x, y = coord[0], coord[1]
        x = chr(7 - x + ord('a'))
        y = 8 - y
        return f'{x}{y}'

    # draw main game board
    def draw_board(self):
        self.draw_grids()
        self.draw_message_board()
        self.draw_info_board()

    def draw_grids(self):
        # all title
        color = 0
        for title_index in range(64):
            col = title_index % 8
            row = title_index // 8
            if color == 0:
                pygame.draw.rect(self.screen, '#ffcf9f', [
                    col * self.title_size, row * self.title_size,
                    self.title_size, self.title_size
                ])

            else:
                pygame.draw.rect(self.screen, '#d28c45', [
                    col * self.title_size, row * self.title_size,
                    self.title_size, self.title_size
                ])

            if col % 8 != 7:
                color = 1 - color

        # make the board grid like
        for i in range(8):
            pygame.draw.line(self.screen, 'black', (0, self.title_size * i),
                             (self.title_size * 8, self.title_size * i), 1)

            pygame.draw.line(self.screen, 'black', (self.title_size * i, 0),
                             (self.title_size * i, self.title_size * 8), 1)

    def draw_message_board(self):
        pygame.draw.rect(self.screen, '#ffcf9f', [
            0, self.title_size * 8,
            self.title_size * 8, self.HEIGHT - self.title_size * 8
        ])

        pygame.draw.rect(self.screen, 'black', [
            0, self.title_size * 8,
            self.title_size * 8, self.HEIGHT - self.title_size * 8
        ], 1)

        if self.board.turn:
            status_text = 'WHITE TURN'
            color = 'red'
        else:
            status_text = 'BLACK TURN'
            color = 'blue'

        font = pygame.font.Font('freesansbold.ttf', 25)
        text = font.render(status_text, True, color)
        x = (self.title_size * 8 - text.get_width()) // 2
        y = self.title_size * 8 + (self.HEIGHT - self.title_size * 8 - text.get_height()) // 2
        self.screen.blit(text, (x, y))

    def draw_info_board(self):
        # info board
        pygame.draw.rect(self.screen, 'black', [
            self.title_size * 8, 0,
            self.WIDTH - self.title_size * 8, self.HEIGHT
        ], 1)

        if self.is_white:
            color = 'red'
            player = 'WHITE'
        else:
            color = 'blue'
            player = 'BLACK'

        font = pygame.font.Font('freesansbold.ttf', 15)
        self.screen.blit(font.render(f'YOU ARE {player}', True, color),
                         (self.title_size * 8 + 10, 10))
        game_time_text = f'Game time: {self.game_time // 60:02d}:{self.game_time % 60:02d}'
        self.screen.blit(font.render(game_time_text, True, color), (self.title_size * 8 + 10, 30))

        player_time_text = f'Player time: {self.player_time // 60:02d}:{self.player_time % 60:02d}'
        self.screen.blit(font.render(player_time_text, True, color), (self.title_size * 8 + 10, 50))

    # draw pieces onto board
    def draw_pieces(self):
        self.draw_current_pieces()
        self.draw_selected_piece()
        self.draw_captured_pieces()
        self.draw_check()
        self.draw_last_move()
        self.draw_valid_moves()

    def draw_captured_pieces(self):
        white_index = 0
        black_index = 0
        white_x_coord = ((self.WIDTH - self.title_size * 8) // 2 - self.small_piece_size) // 2 + self.title_size * 8
        black_x_coord = ((self.WIDTH - self.title_size * 8) // 2 - self.small_piece_size) // 2 + \
                        (self.WIDTH - self.title_size * 8) // 2 + self.title_size * 8
        pad_y = 90
        for pair in self.moves_information:
            time_to_move, capture_piece = pair
            if capture_piece is not None:
                piece_name = capture_piece.symbol()
                index = self.piece_list.index(piece_name)
                # if black
                if piece_name.islower():
                    y_coord = pad_y + black_index * 30
                    self.screen.blit(self.small_piece_images[index], (black_x_coord, y_coord))
                    black_index += 1
                else:
                    y_coord = pad_y + white_index * 30
                    self.screen.blit(self.small_piece_images[index], (white_x_coord, y_coord))
                    white_index += 1

    def draw_current_pieces(self):
        piece_map = self.board.piece_map()

        for square, piece in piece_map.items():
            square_coord = chess.square_name(square)
            piece_name = piece.symbol()
            index = self.piece_list.index(piece_name)
            x_coord, y_coord = self.decode_coordinate(square_coord)
            pad_x = pad_y = (self.title_size - self.piece_images[index].get_width()) // 2
            self.screen.blit(self.piece_images[index],
                             (x_coord * self.title_size + pad_x, y_coord * self.title_size + pad_y))

    def draw_selected_piece(self):
        try:
            piece = self.board.piece_at(chess.parse_square(self.selection))
            if piece:
                if self.board.turn:
                    color = 'red'
                else:
                    color = 'blue'
                x, y = self.decode_coordinate(self.selection)
                pygame.draw.rect(self.screen, color, [
                    x * self.title_size, y * self.title_size,
                    self.title_size, self.title_size
                ], 2)
        except ValueError:
            pass

    def draw_check(self):
        if self.board.is_check():
            if self.board.turn:
                king_index = self.board.king(chess.WHITE)
            else:
                king_index = self.board.king(chess.BLACK)
            king_position = chess.square_name(king_index)
            coord = self.decode_coordinate(king_position)
            x, y = coord
            pygame.draw.rect(self.screen, 'gold', [
                x * self.title_size, y * self.title_size,
                self.title_size, self.title_size
            ], 3)

    # draw all possible move of the current selection
    def draw_valid_moves(self):
        if self.selection == '':
            return

        if self.board.turn:
            color = 'red'
        else:
            color = 'blue'

        legal_moves = list(self.board.legal_moves)
        valid_moves = [str(move) for move in legal_moves if str(move).startswith(self.selection)]
        valid_coord = [self.decode_coordinate(move[2:]) for move in valid_moves]
        for coord in valid_coord:
            x, y = coord
            pygame.draw.circle(self.screen, color, (
                x * self.title_size + self.title_size // 2,
                y * self.title_size + self.title_size // 2
            ), 5)

    # draw the last move
    def draw_last_move(self):
        if self.board.move_stack:
            last_move = self.board.peek()
            x_start, y_start = self.decode_coordinate(str(last_move)[:2])
            x_end, y_end = self.decode_coordinate(str(last_move)[2:])
            if self.board.turn:
                color = 'blue'
            else:
                color = 'red'

            pygame.draw.rect(self.screen, color, [
                x_start * self.title_size, y_start * self.title_size,
                self.title_size, self.title_size
            ], 3)
            pygame.draw.rect(self.screen, color, [
                x_end * self.title_size, y_end * self.title_size,
                self.title_size, self.title_size
            ], 3)

    def check_promotion(self, move: chess.Move):
        start, end = str(move)[:2], str(move)[2:]
        start_piece = self.board.piece_at(chess.parse_square(start))
        if start_piece.symbol().lower() != 'p':
            return False
        else:
            end_rank = chess.square_rank(chess.parse_square(end))
            if end_rank == 0 or end_rank == 7:
                return True
        return False

    def play(self, coord: tuple):
        # choose a piece
        if self.selection == '':
            self.selection = self.encode_coordinate(coord)
            piece = self.board.piece_at(chess.parse_square(self.selection))
            if not piece:
                self.selection = ''
            elif piece.symbol().islower() and not self.board.turn:
                pass
            elif piece.symbol().isupper() and self.board.turn:
                pass
            else:
                self.selection = ''
        # make a move
        else:
            destination = self.encode_coordinate(coord)
            piece = self.board.piece_at(chess.parse_square(destination))
            # choose another piece
            if piece and (
                    (piece.symbol().islower() and not self.board.turn) or
                    (piece.symbol().isupper() and self.board.turn)
            ):
                self.selection = destination
            else:
                if self.selection != destination:
                    legal_moves = set(self.board.legal_moves)
                    move = chess.Move.from_uci(self.selection + destination)
                    if self.check_promotion(move):
                        move = chess.Move.from_uci(str(move) + 'q')
                    if move in legal_moves:
                        captured_piece = None
                        if self.board.is_capture(move):
                            captured_piece = self.board.piece_at(move.to_square)
                        self.board.push(move)
                        self.moves_information.append(
                            (self.previous_player_time-self.player_time, captured_piece)
                        )
                        self.previous_player_time = self.player_time
                        data = {
                            'board': self.board,
                            'moves_information': self.moves_information
                        }
                        self.client.send(data)
                self.selection = ''

    def draw_game_over(self, winner: str, opponent_disconnected=False):
        width, height = 450, 120
        pygame.draw.rect(self.screen, 'black', [(self.WIDTH - width) // 2, (self.HEIGHT - height) // 2, width, height])

        if winner == 'WHITE':
            color = 'red'
        else:
            color = 'blue'

        font = pygame.font.Font('freesansbold.ttf', 15)
        state_text = font.render(f'{winner} won!', True, color)
        tip_text = font.render('You will be disconnected in 3s', True, 'white')

        if opponent_disconnected:
            state_text = font.render(f'{winner} won! Your opponent disconnected', True, color)

        self.screen.blit(state_text, (
            (self.WIDTH - width) // 2 + (width - state_text.get_width()) // 2,
            (self.HEIGHT - height) // 2 + (height - state_text.get_height()) // 3 * 1
        ))
        self.screen.blit(tip_text, (
            (self.WIDTH - width) // 2 + (width - tip_text.get_width()) // 2,
            (self.HEIGHT - height) // 2 + (height - tip_text.get_height()) // 3 * 2
        ))

    def draw_out_of_time(self):
        width, height = 450, 120
        pygame.draw.rect(self.screen, 'black', [(self.WIDTH - width) // 2, (self.HEIGHT - height) // 2, width, height])
        font = pygame.font.Font('freesansbold.ttf', 15)
        state_text = font.render('You ran out of time', True, 'white')
        tip_text = font.render('You will be disconnected in 3s', True, 'white')

        self.screen.blit(state_text, (
            (self.WIDTH - width) // 2 + (width - state_text.get_width()) // 2,
            (self.HEIGHT - height) // 2 + (height - state_text.get_height()) // 3 * 1
        ))
        self.screen.blit(tip_text, (
            (self.WIDTH - width) // 2 + (width - tip_text.get_width()) // 2,
            (self.HEIGHT - height) // 2 + (height - tip_text.get_height()) // 3 * 2
        ))

    def draw_waiting(self):
        background_image = pygame.image.load("img/waiting-background.png")
        width, height = 320, 40
        self.screen.blit(background_image, (0, 50))

        pygame.draw.rect(self.screen, '#ffcf9f', [
            (self.WIDTH - width) // 2, (self.HEIGHT - height) // 2, width, height
        ])
        font = pygame.font.Font('freesansbold.ttf', 30)
        text = font.render('Waiting for opponent', True, '#d28c45')

        self.screen.blit(text, (
            (self.WIDTH - width) // 2 + (width - text.get_width()) // 2,
            (self.HEIGHT - height) // 2 + (height - text.get_height()) // 2
        ))

    # wait for server to send data
    def fetch_data(self):
        while True:
            try:
                data = self.client.receive()
                self.board = data['board']
                self.is_white = (data['white'] == self.client.client_id)
                self.state = data['state']
                self.moves_information = data['moves_information']
                self.game_time = data['time']['game']
                if self.is_white:
                    self.player_time = data['time']['white']
                else:
                    self.player_time = data['time']['black']
            except Exception as er:
                print(er)
                break

    def countdown_player(self):
        while self.player_time != 0:
            try:
                if self.state == Message.READY and self.is_white == self.board.turn:
                    self.player_time -= 1
                    time.sleep(1)
            except Exception as er:
                print(er)
                break

    def countdown_game(self):
        while self.game_time != 0:
            try:
                if self.state == Message.READY:
                    self.game_time -= 1
                    time.sleep(1)
            except Exception as er:
                print(er)
                break

    def run_game(self):
        data_thread = threading.Thread(target=self.fetch_data, daemon=True)
        data_thread.start()

        player_timer_thread = threading.Thread(target=self.countdown_player, daemon=True)
        player_timer_thread.start()

        game_timer_thread = threading.Thread(target=self.countdown_game, daemon=True)
        game_timer_thread.start()

        run = True
        while run:
            self.timer.tick(self.fps)
            self.screen.fill('#ffcf9f')

            # wait for opponent
            if self.state == Message.IN_QUEUE:
                self.draw_waiting()
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                continue

            self.draw_board()
            self.draw_pieces()

            # out of time
            if self.player_time == 0:
                self.draw_out_of_time()
                pygame.display.flip()
                pygame.time.wait(3000)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pass
                break

            # opponent disconnect
            if self.state == Message.DISCONNECT:
                winner = 'WHITE' if self.is_white else 'BLACK'
                self.draw_game_over(winner, opponent_disconnected=True)
                pygame.display.flip()
                pygame.time.wait(3000)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pass
                break

            # end game
            if self.board.is_checkmate():
                winner = 'BLACK' if self.board.turn else 'WHITE'
                self.draw_game_over(winner)
                pygame.display.flip()
                pygame.time.wait(3000)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pass
                break

            # event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEBUTTONDOWN and self.is_white == self.board.turn:
                    x_cord = event.pos[0] // self.title_size
                    y_cord = event.pos[1] // self.title_size
                    if 0 <= x_cord <= 7 and 0 <= y_cord <= 7:
                        click_coord = (x_cord, y_cord)
                        self.play(click_coord)

            pygame.display.flip()

        self.client.client_socket.close()
        pygame.quit()


class GameView(Game):
    def __init__(self, client):
        super().__init__(client)
        pygame.display.set_caption('Room View Chess.io')
        self.data = {}

    def draw_info_board(self):
        # info board
        pygame.draw.rect(self.screen, 'black', [
            self.title_size * 8, 0,
            self.WIDTH - self.title_size * 8, self.HEIGHT - (self.HEIGHT - self.title_size * 8)
        ], 1)

        font = pygame.font.Font('freesansbold.ttf', 15)
        self.screen.blit(
            font.render(f'Current viewers: {self.data["viewers"]}', True, 'black'),
            (self.title_size * 8 + 10, 10)
        )

        game_time = self.data['time']['game']
        white_time = self.data['time']['white']
        black_time = self.data['time']['black']
        game_time_text = f'Game time: {game_time // 60:02d}:{game_time % 60:02d}'
        self.screen.blit(font.render(game_time_text, True, 'black'), (self.title_size * 8 + 10, 30))

        white_time_text = f'White time: {white_time // 60:02d}:{white_time % 60:02d}'
        self.screen.blit(font.render(white_time_text, True, 'red'), (self.title_size * 8 + 10, 50))

        black_time_text = f'Black time: {black_time // 60:02d}:{black_time % 60:02d}'
        self.screen.blit(font.render(black_time_text, True, 'blue'), (self.title_size * 8 + 10, 70))

    def draw_pieces(self):
        self.draw_current_pieces()
        self.draw_captured_pieces()
        self.draw_check()
        self.draw_last_move()

    def run_game(self):
        run = True
        while run:
            self.timer.tick(self.fps)
            self.screen.fill('#ffcf9f')
            self.client.send(Message.VIEWING)
            self.data = self.client.receive()

            self.board = self.data['board']
            self.moves_information = self.data['moves_information']
            self.draw_board()
            self.draw_pieces()

            # game ended
            if self.data['state'] == Message.DISCONNECT:
                winner = self.data['winner']
                self.draw_game_over(winner)
                pygame.display.flip()
                pygame.time.wait(3000)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pass
                break

            # event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            pygame.display.flip()

        self.client.send(Message.STOP_VIEWING)
        pygame.quit()


class GameReplay(Game):
    def __init__(self, client, board: chess.Board, moves_information: list[tuple], winner: str):
        super().__init__(client)
        pygame.display.set_caption('Game Replay Chess.io')
        self.board = chess.Board()
        self.winner = winner
        self.move_list = board.move_stack
        self.moves_information = moves_information
        self.current_move = 0
        self.max_move = len(self.move_list)
        self.autoplay = False

        self.previous_button, self.next_button, self.play_button, self.pause_button = self.load_button_image()
        self.x_previous = self.title_size * 8 // 2 - 90  # Điều chỉnh giá trị này để thay đổi vị trí của nút previous
        self.y_previous = self.title_size * 8 + (self.HEIGHT - self.title_size * 8 - 55) // 2 + 20  # pad for text
        self.x_next = self.title_size * 8 // 2 + 40  # Điều chỉnh giá trị này để thay đổi vị trí của nút next
        self.y_next = self.title_size * 8 + (self.HEIGHT - self.title_size * 8 - 55) // 2 + 20  # pad for text

        self.x_play = self.title_size * 8 // 2 - 25
        self.y_play = self.title_size * 8 + (self.HEIGHT - self.title_size * 8 - 60) // 2 + 20  # pad for text
        self.x_pause = self.title_size * 8 // 2 - 25
        self.y_pause = self.title_size * 8 + (self.HEIGHT - self.title_size * 8 - 60) // 2 + 20  # pad for text

        self.game_time = 60*20
        self.white_time = 60*15
        self.black_time = 60*15
        self.game_timestamps, self.white_timestamps, self.black_timestamps = self.timestamp_list()

    def timestamp_list(self):
        game_time = self.game_time
        white_time = self.white_time
        black_time = self.black_time

        game = [game_time]
        white = [white_time]
        black = [black_time]
        for index, pair in enumerate(self.moves_information):
            game_time -= pair[0]
            if index % 2 == 0:
                white_time -= pair[0]
            else:
                black_time -= pair[0]
            game.append(game_time)
            white.append(white_time)
            black.append(black_time)
        return game, white, black

    @staticmethod
    def load_button_image():
        next_image = pygame.image.load('img/next.png')
        previous_image = pygame.image.load('img/previous.png')
        play_image = pygame.image.load('img/play.png')
        pause_image = pygame.image.load('img/pause.png')
        return previous_image, next_image, play_image, pause_image

    def draw_message_board(self):
        pygame.draw.rect(self.screen, '#ffcf9f', [
            0, self.title_size * 8,
            self.title_size * 8, self.HEIGHT - self.title_size * 8
        ])

        pygame.draw.rect(self.screen, 'black', [
            0, self.title_size * 8,
            self.title_size * 8, self.HEIGHT - self.title_size * 8
        ], 1)

        if self.board.turn:
            status_text = 'WHITE TURN'
            color = 'red'
        else:
            status_text = 'BLACK TURN'
            color = 'blue'

        font = pygame.font.Font('freesansbold.ttf', 25)
        text = font.render(status_text, True, color)
        x = (self.title_size * 8 - text.get_width()) // 2
        y = 500
        self.screen.blit(text, (x, y))

        if self.autoplay is False:  # Draw buttons only if not in autoplay mode
            self.screen.blit(self.previous_button, (self.x_previous, self.y_previous))
            self.screen.blit(self.next_button, (self.x_next, self.y_next))
            self.screen.blit(self.play_button, (self.x_play, self.y_play))
        else:  # Draw disabled buttons if in autoplay mode
            faded_color = (128, 128, 128, 128)  # Adjust alpha channel for faded appearance

            disabled_previous = self.previous_button.copy()
            disabled_previous.fill(faded_color, special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(disabled_previous, (self.x_previous, self.y_previous))

            disabled_next = self.next_button.copy()
            disabled_next.fill(faded_color, special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(disabled_next, (self.x_next, self.y_next))

            self.screen.blit(self.pause_button, (self.x_pause, self.y_pause))

    def draw_info_board(self):
        # info board
        pygame.draw.rect(self.screen, 'black', [
            self.title_size * 8, 0,
            self.WIDTH - self.title_size * 8, self.HEIGHT
        ], 1)

        font = pygame.font.Font('freesansbold.ttf', 15)
        self.screen.blit(font.render(f'Current move: {self.current_move}', True, 'black'),
                         (self.title_size * 8 + 10, 10))
        game_time_text = f'Game time: {self.game_time // 60:02d}:{self.game_time % 60:02d}'
        self.screen.blit(font.render(game_time_text, True, 'black'), (self.title_size * 8 + 10, 30))

        white_time_text = f'White time: {self.white_time // 60:02d}:{self.white_time % 60:02d}'
        self.screen.blit(font.render(white_time_text, True, 'red'), (self.title_size * 8 + 10, 50))

        black_time_text = f'Black time: {self.black_time // 60:02d}:{self.black_time % 60:02d}'
        self.screen.blit(font.render(black_time_text, True, 'blue'), (self.title_size * 8 + 10, 70))

    def handle_button_click(self, x_cord: int, y_cord: int):
        if not self.autoplay:  # Allow button clicks only if not in autoplay mode
            if self.x_previous <= x_cord <= self.x_previous + 50 and self.y_previous \
                    <= y_cord <= self.y_previous + 50:
                self.previous()
            elif self.x_next <= x_cord <= self.x_next + 50 and self.y_next \
                    <= y_cord <= self.y_next + 50:
                self.next()
            elif self.x_play <= x_cord <= self.x_play + 55 and self.y_play \
                    <= y_cord <= self.y_play + 55:
                self.autoplay = True
        else:
            if self.x_pause <= x_cord <= self.x_pause + 55 and self.y_pause \
                 <= y_cord <= self.y_pause + 55:
                self.autoplay = False

    def previous(self):
        if self.current_move == 0:
            return

        self.current_move -= 1
        # extra last move -> last move => Don't pop
        if self.current_move != self.max_move:
            self.game_time = self.game_timestamps[self.current_move]
            self.white_time = self.white_timestamps[self.current_move]
            self.black_time = self.black_timestamps[self.current_move]
            self.board.pop()

    def next(self):
        if self.current_move == self.max_move+1:
            return

        self.current_move += 1
        # last move -> extra last move => Don't push
        if self.current_move != self.max_move+1:
            self.game_time = self.game_timestamps[self.current_move]
            self.white_time = self.white_timestamps[self.current_move]
            self.black_time = self.black_timestamps[self.current_move]
            self.board.push(self.move_list[self.current_move - 1])

    def draw_pieces(self):
        self.draw_current_pieces()
        self.draw_captured_pieces()
        self.draw_check()
        self.draw_last_move()

    def draw_captured_pieces(self):
        white_index = 0
        black_index = 0
        white_x_coord = ((self.WIDTH - self.title_size * 8) // 2 - self.small_piece_size) // 2 + self.title_size * 8
        black_x_coord = ((self.WIDTH - self.title_size * 8) // 2 - self.small_piece_size) // 2 + \
                        (self.WIDTH - self.title_size * 8) // 2 + self.title_size * 8
        pad_y = 90
        for pair in self.moves_information[:self.current_move]:
            time_to_move, capture_piece = pair
            if capture_piece is not None:
                piece_name = capture_piece.symbol()
                index = self.piece_list.index(piece_name)
                # if black
                if piece_name.islower():
                    y_coord = pad_y + black_index * 30
                    self.screen.blit(self.small_piece_images[index], (black_x_coord, y_coord))
                    black_index += 1
                else:
                    y_coord = pad_y + white_index * 30
                    self.screen.blit(self.small_piece_images[index], (white_x_coord, y_coord))
                    white_index += 1

    def draw_game_over(self, winner: str, opponent_disconnected=False):
        width, height = 450, 120
        pygame.draw.rect(self.screen, 'black', [(self.WIDTH - width) // 2, (self.HEIGHT - height) // 2, width, height])

        if winner == 'WHITE':
            color = 'red'
        else:
            color = 'blue'

        font = pygame.font.Font('freesansbold.ttf', 20)
        state_text = font.render(f'{winner} won!', True, color)

        self.screen.blit(state_text, (
            (self.WIDTH - width) // 2 + (width - state_text.get_width()) // 2,
            (self.HEIGHT - height) // 2 + (height - state_text.get_height()) // 2
        ))

    def run_game(self):
        run = True

        previous_time = pygame.time.get_ticks()
        while run:
            self.timer.tick(self.fps)
            self.screen.fill('#ffcf9f')

            self.draw_board()
            self.draw_pieces()

            if self.current_move == self.max_move+1:
                self.draw_game_over(self.winner)

            if pygame.time.get_ticks() - previous_time >= 1000:
                previous_time = pygame.time.get_ticks()
                if self.autoplay:
                    next_move = self.current_move + 1
                    if next_move != self.max_move + 1:
                        if self.current_move % 2 == 0:
                            self.white_time -= 1
                        else:
                            self.black_time -= 1
                        self.game_time -= 1

                    if next_move == self.max_move + 1:
                        pygame.time.wait(500)
                        self.autoplay = False
                        self.next()
                    elif self.game_time == self.game_timestamps[next_move]:
                        self.next()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    x_cord = event.pos[0]
                    y_cord = event.pos[1]
                    self.handle_button_click(x_cord, y_cord)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT and not self.autoplay:
                        self.next()
                    elif event.key == pygame.K_LEFT and not self.autoplay:
                        self.previous()
                    elif event.key == pygame.K_SPACE:
                        self.autoplay = not self.autoplay  # Toggle autoplay on/off

            pygame.display.flip()

        pygame.quit()
