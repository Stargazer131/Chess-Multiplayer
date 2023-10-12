import chess
import pygame
from utility import get_image_resources, encode_coordinate, decode_coordinate


pygame.init()
WIDTH = 650
HEIGHT = 550
screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
fps = 60
selection = ''

# load in game piece images (queen, king, rook, bishop, knight, pawn) x 2
img_resources = get_image_resources()

piece_size = img_resources['piece_size']
pawn_size = img_resources['pawn_size']
small_piece_size = img_resources['small_piece_size']
piece_images = img_resources['piece_images']
small_piece_images = img_resources['small_piece_images']
piece_list = img_resources['piece']

# board

board = chess.Board()

# draw main game board
title_size = 60
def draw_board():
    color = 0
    for title_index in range(64):
        col = title_index % 8
        row = title_index // 8
        if color == 0:
            pygame.draw.rect(screen, 'light gray', [col * title_size, row * title_size, title_size, title_size])
        else:
            pygame.draw.rect(screen, 'dark gray', [col * title_size, row * title_size, title_size, title_size])

        if col % 8 != 7:
            color = 1 - color

    # message board
    pygame.draw.rect(screen, 'gray', [0, title_size*8, WIDTH, HEIGHT-title_size*8])
    pygame.draw.rect(screen, 'black', [0, title_size*8, WIDTH, HEIGHT-title_size*8], 1)

    if board.turn:
        status_text = 'WHITE TURN'
        color = 'red'
    else:
        status_text = 'BLACK TURN'
        color = 'blue'

    font = pygame.font.Font('freesansbold.ttf', 25)
    text = font.render(status_text, True, color)
    x = (WIDTH - text.get_width()) // 2
    y = title_size * 8 + (HEIGHT-title_size*8 - text.get_height()) // 2
    screen.blit(text, (x, y))

    # captured board
    pygame.draw.rect(screen, 'black', [title_size*8, 0, WIDTH-title_size*8, HEIGHT-(HEIGHT-title_size*8)], 1)

    # make the board grid like
    for i in range(8):
        pygame.draw.line(screen, 'black', (0, title_size * i), (title_size * 8, title_size * i), 1)
        pygame.draw.line(screen, 'black', (title_size * i, 0), (title_size * i, title_size * 8), 1)


# draw pieces onto board
def draw_pieces():
    piece_map = board.piece_map()

    for square, piece in piece_map.items():
        square_coord = chess.square_name(square)
        piece_name = piece.symbol()
        index = piece_list.index(piece_name)
        x_coord, y_coord = decode_coordinate(square_coord)
        pad_x = pad_y = (title_size - piece_images[index].get_width()) // 2
        screen.blit(piece_images[index], (x_coord * title_size + pad_x, y_coord * title_size + pad_y))

    # draw the selected piece border
    try:
        piece = board.piece_at(chess.parse_square(selection))
        if piece:
            if board.turn:
                color = 'red'
            else:
                color = 'blue'
            x, y = decode_coordinate(selection)
            pygame.draw.rect(screen, color, [
                x * title_size, y * title_size,
                title_size, title_size
            ], 2)
    except ValueError:
        pass

    # draw check
    if board.is_check():
        if board.turn:
            king_index = board.king(chess.WHITE)
        else:
            king_index = board.king(chess.BLACK)
        king_position = chess.square_name(king_index)
        coord = decode_coordinate(king_position)
        x, y = coord
        pygame.draw.rect(screen, 'gold', [
            x * title_size, y * title_size,
            title_size, title_size
        ], 3)


# draw all possible move of the current selection
def draw_valid_moves():
    if board.turn:
        color = 'red'
    else:
        color = 'blue'

    legal_moves = list(board.legal_moves)
    valid_moves = [str(move) for move in legal_moves if str(move).startswith(selection)]
    valid_coords = [decode_coordinate(move[2:]) for move in valid_moves]
    for coord in valid_coords:
        x, y = coord
        pygame.draw.circle(screen, color, (
            x * title_size + title_size // 2,
            y * title_size + title_size // 2
        ), 5)


def play(coord: tuple):
    global selection
    # choose a piece
    if selection == '':
        selection = encode_coordinate(click_coord)
        piece = board.piece_at(chess.parse_square(selection))
        if not piece:
            selection = ''
        elif piece.symbol().islower() and not board.turn:
            pass
        elif piece.symbol().isupper() and board.turn:
            pass
        else:
            selection = ''
    # make a move
    else:
        destination = encode_coordinate(click_coord)
        piece = board.piece_at(chess.parse_square(destination))
        # choose another piece
        if piece and ((piece.symbol().islower() and not board.turn) or (piece.symbol().isupper() and board.turn)):
            selection = destination
        else:
            if selection != destination:
                legal_moves = set(board.legal_moves)
                move = chess.Move.from_uci(selection + destination)
                if move in legal_moves:
                    board.push(move)
            selection = ''


def draw_game_over():
    width, height = 400, 70
    pygame.draw.rect(screen, 'black', [(WIDTH-width)//2, (HEIGHT-height)//2, width, height])

    if not board.turn:
        winner = 'WHITE'
        color = 'red'
    else:
        winner = 'BLACK'
        color = 'blue'

    font = pygame.font.Font('freesansbold.ttf', 10)
    winner_text = font.render(f'{winner} won the game!', True, color)
    tip_text = font.render(f'Press ENTER to Restart!', True, 'white')

    screen.blit(winner_text, (
        (WIDTH-width)//2 + (width-winner_text.get_width())//2,
        (HEIGHT-height)//2 + (height-winner_text.get_height())//3*1
    ))
    screen.blit(tip_text, (
        (WIDTH-width)//2 + (width-tip_text.get_width())//2,
        (HEIGHT-height)//2 + (height-tip_text.get_height())//3*2
    ))


run = True
while run:
    timer.tick(fps)
    screen.fill('light gray')
    draw_board()
    draw_pieces()

    if selection != '':
        draw_valid_moves()

    if board.is_checkmate():
        draw_game_over()

    # event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not board.is_checkmate():
            x_cord = event.pos[0] // title_size
            y_cord = event.pos[1] // title_size
            click_coord = (x_cord, y_cord)
            play(click_coord)

        if event.type == pygame.KEYDOWN and board.is_checkmate():
            if event.key == pygame.K_RETURN:
                board = chess.Board()
                selection = ''

    pygame.display.flip()
pygame.quit()