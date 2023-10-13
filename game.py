import chess
import pygame
from utility import get_image_resources


class Game:
    def __init__(self, client, player_id: int):
        self.client = client
        self.player_id = player_id
        self.is_white = True if (player_id % 2 == 0) else False

        pygame.init()
        self.WIDTH = 650
        self.HEIGHT = 550
        self.screen = pygame.display.set_mode([self.WIDTH, self.HEIGHT])
        pygame.display.set_caption('Chess.io')
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
                pygame.draw.rect(self.screen, 'light gray', [
                    col * self.title_size, row * self.title_size,
                    self.title_size, self.title_size
                ])

            else:
                pygame.draw.rect(self.screen, 'dark gray', [
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
        pygame.draw.rect(self.screen, 'gray', [
            0, self.title_size * 8,
            self.WIDTH, self.HEIGHT - self.title_size * 8
        ])

        pygame.draw.rect(self.screen, 'black', [
            0, self.title_size * 8,
            self.WIDTH, self.HEIGHT - self.title_size * 8
        ], 1)

        if self.board.turn:
            status_text = 'WHITE TURN'
            color = 'red'
        else:
            status_text = 'BLACK TURN'
            color = 'blue'

        font = pygame.font.Font('freesansbold.ttf', 25)
        text = font.render(status_text, True, color)
        x = (self.WIDTH - text.get_width()) // 2
        y = self.title_size * 8 + (self.HEIGHT - self.title_size * 8 - text.get_height()) // 2
        self.screen.blit(text, (x, y))

    def draw_info_board(self):
        # info board
        pygame.draw.rect(self.screen, 'black', [
            self.title_size * 8, 0,
            self.WIDTH - self.title_size * 8, self.HEIGHT - (self.HEIGHT - self.title_size * 8)
        ], 1)

        if self.player_id % 2 == 0:
            color = 'red'
            player = 'WHITE'
        else:
            color = 'blue'
            player = 'BLACK'

        font = pygame.font.Font('freesansbold.ttf', 15)
        self.screen.blit(font.render(f'Game Id: {self.player_id // 2}', True, 'black'),
                         (self.title_size * 8 + 10, 10))
        self.screen.blit(font.render(f'Player Id: {self.player_id}', True, 'black'),
                         (self.title_size * 8 + 10, 30))
        self.screen.blit(font.render(f'YOU ARE {player}', True, color),
                         (self.title_size * 8 + 10, 50))

    # draw pieces onto board
    def draw_pieces(self):
        self.draw_current_pieces()
        self.draw_selected_piece()
        self.draw_check()
        self.draw_last_move()
        self.draw_valid_moves()

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
            if piece and ((piece.symbol().islower() and not self.board.turn) or (piece.symbol().isupper() and self.board.turn)):
                self.selection = destination
            else:
                if self.selection != destination:
                    legal_moves = set(self.board.legal_moves)
                    move = chess.Move.from_uci(self.selection + destination)
                    if self.check_promotion(move):
                        move = chess.Move.from_uci(str(move) + 'q')
                    if move in legal_moves:
                        self.board.push(move)
                self.selection = ''

    def draw_game_over(self, winner: str, opponent_disconnected=False):
        width, height = 450, 120
        pygame.draw.rect(self.screen, 'black', [(self.WIDTH - width) // 2, (self.HEIGHT - height) // 2, width, height])

        if winner == 'WHITE':
            color = 'red'
        else:
            color = 'blue'

        font = pygame.font.Font('freesansbold.ttf', 15)
        winner_text = font.render(f'{winner} won the game!', True, color)
        tip_text = font.render('Press enter to continue', True, 'white')

        if opponent_disconnected:
            winner_text = font.render(f'{winner} won the game! Your opponent disconnected', True, color)
            tip_text = font.render('You will be disconnected in 3s', True, 'white')

        self.screen.blit(winner_text, (
            (self.WIDTH - width) // 2 + (width - winner_text.get_width()) // 2,
            (self.HEIGHT - height) // 2 + (height - winner_text.get_height()) // 3 * 1
        ))
        self.screen.blit(tip_text, (
            (self.WIDTH - width) // 2 + (width - tip_text.get_width()) // 2,
            (self.HEIGHT - height) // 2 + (height - tip_text.get_height()) // 3 * 2
        ))

    def draw_waiting(self):
        width, height = 400, 70
        pygame.draw.rect(self.screen, 'white', [(self.WIDTH - width) // 2, (self.HEIGHT - height) // 2, width, height])

        font = pygame.font.Font('freesansbold.ttf', 30)
        text = font.render('Waiting for opponent', True, 'black')

        self.screen.blit(text, (
            (self.WIDTH - width) // 2 + (width - text.get_width()) // 2,
            (self.HEIGHT - height) // 2 + (height - text.get_height()) // 2
        ))

    def run_game(self):
        run = True
        while run:
            self.timer.tick(self.fps)
            self.screen.fill('light gray')

            received_data = self.client.send(self.board)
            self.board = received_data['board']
            state = received_data['state']

            # wait for opponent
            if state == 'Not Ready':
                self.draw_waiting()
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                continue

            self.draw_board()
            self.draw_pieces()

            # opponent disconnect
            if state == 'Disconnect':
                winner = 'WHITE' if (self.player_id % 2 == 0) else 'BLACK'
                self.draw_game_over(winner, opponent_disconnected=True)
                pygame.display.flip()
                pygame.time.wait(3000)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pass
                break

            if self.board.is_checkmate():
                winner = 'BLACK' if self.board.turn else 'WHITE'
                self.draw_game_over(winner)

            # event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEBUTTONDOWN and not self.board.is_checkmate() \
                        and self.is_white == self.board.turn:
                    x_cord = event.pos[0] // self.title_size
                    y_cord = event.pos[1] // self.title_size
                    if 0 <= x_cord <= 7 and 0 <= y_cord <= 7:
                        click_coord = (x_cord, y_cord)
                        self.play(click_coord)

                if event.type == pygame.KEYDOWN and self.board.is_checkmate():
                    if event.key == pygame.K_RETURN:
                        self.board = chess.Board()
                        self.selection = ''

            pygame.display.flip()
        pygame.quit()
