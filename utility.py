# load in game piece images (queen, king, rook, bishop, knight, pawn) x 2
import pygame


def get_image_resources():
    piece_size = 50
    pawn_size = 50
    small_piece_size = 25

    black_queen = pygame.image.load('img/black-queen.png')
    black_queen = pygame.transform.scale(black_queen, (piece_size, piece_size))
    black_queen_small = pygame.transform.scale(black_queen, (small_piece_size, small_piece_size))
    black_king = pygame.image.load('img/black-king.png')
    black_king = pygame.transform.scale(black_king, (piece_size, piece_size))
    black_king_small = pygame.transform.scale(black_king, (small_piece_size, small_piece_size))
    black_rook = pygame.image.load('img/black-rook.png')
    black_rook = pygame.transform.scale(black_rook, (piece_size, piece_size))
    black_rook_small = pygame.transform.scale(black_rook, (small_piece_size, small_piece_size))
    black_bishop = pygame.image.load('img/black-bishop.png')
    black_bishop = pygame.transform.scale(black_bishop, (piece_size, piece_size))
    black_bishop_small = pygame.transform.scale(black_bishop, (small_piece_size, small_piece_size))
    black_knight = pygame.image.load('img/black-knight.png')
    black_knight = pygame.transform.scale(black_knight, (piece_size, piece_size))
    black_knight_small = pygame.transform.scale(black_knight, (small_piece_size, small_piece_size))
    black_pawn = pygame.image.load('img/black-pawn.png')
    black_pawn = pygame.transform.scale(black_pawn, (pawn_size, pawn_size))
    black_pawn_small = pygame.transform.scale(black_pawn, (small_piece_size, small_piece_size))

    white_queen = pygame.image.load('img/white-queen.png')
    white_queen = pygame.transform.scale(white_queen, (piece_size, piece_size))
    white_queen_small = pygame.transform.scale(white_queen, (small_piece_size, small_piece_size))
    white_king = pygame.image.load('img/white-king.png')
    white_king = pygame.transform.scale(white_king, (piece_size, piece_size))
    white_king_small = pygame.transform.scale(white_king, (small_piece_size, small_piece_size))
    white_rook = pygame.image.load('img/white-rook.png')
    white_rook = pygame.transform.scale(white_rook, (piece_size, piece_size))
    white_rook_small = pygame.transform.scale(white_rook, (small_piece_size, small_piece_size))
    white_bishop = pygame.image.load('img/white-bishop.png')
    white_bishop = pygame.transform.scale(white_bishop, (piece_size, piece_size))
    white_bishop_small = pygame.transform.scale(white_bishop, (small_piece_size, small_piece_size))
    white_knight = pygame.image.load('img/white-knight.png')
    white_knight = pygame.transform.scale(white_knight, (piece_size, piece_size))
    white_knight_small = pygame.transform.scale(white_knight, (small_piece_size, small_piece_size))
    white_pawn = pygame.image.load('img/white-pawn.png')
    white_pawn = pygame.transform.scale(white_pawn, (pawn_size, pawn_size))
    white_pawn_small = pygame.transform.scale(white_pawn, (small_piece_size, small_piece_size))

    piece_images = [white_pawn, white_queen, white_king, white_knight, white_rook, white_bishop,
                    black_pawn, black_queen, black_king, black_knight, black_rook, black_bishop]
    small_piece_images = [white_pawn_small, white_queen_small, white_king_small,
                          white_knight_small, white_rook_small, white_bishop_small,
                          black_pawn_small, black_queen_small, black_king_small,
                          black_knight_small, black_rook_small, black_bishop_small]
    piece_list = ['P', 'Q', 'K', 'N', 'R', 'B',
                  'p', 'q', 'k', 'n', 'r', 'b']

    result = {
        'piece_size': 50,
        'pawn_size': 50,
        'small_piece_size': 25,
        'piece_images': piece_images,
        'small_piece_images': small_piece_images,
        'piece': piece_list
    }
    return result


def decode_coordinate(str_coord: str):
    x = 7 - (ord(str_coord[0]) - ord('a'))
    y = 8 - int(str_coord[1])
    return x, y


def encode_coordinate(coord: tuple):
    x, y = coord[0], coord[1]
    x = chr(7 - x + ord('a'))
    y = 8 - y
    return f'{x}{y}'


if __name__ == '__main__':
    pass