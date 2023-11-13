import logging
import colorlog
import pygame
import glob
import os


def get_all_file_names(folder_path: str):
    file_paths = glob.glob(os.path.join(folder_path, '*'))
    return [os.path.basename(file_path) for file_path in file_paths]


# load in game piece images (queen, king, rook, bishop, knight, pawn) x 2
def get_image_resources():
    small_piece_size = 30
    piece_size = 50

    black_queen = pygame.image.load('img/black-queen.png')
    black_queen_small = pygame.transform.scale(black_queen, (small_piece_size, small_piece_size))
    black_king = pygame.image.load('img/black-king.png')
    black_king_small = pygame.transform.scale(black_king, (small_piece_size, small_piece_size))
    black_rook = pygame.image.load('img/black-rook.png')
    black_rook_small = pygame.transform.scale(black_rook, (small_piece_size, small_piece_size))
    black_bishop = pygame.image.load('img/black-bishop.png')
    black_bishop_small = pygame.transform.scale(black_bishop, (small_piece_size, small_piece_size))
    black_knight = pygame.image.load('img/black-knight.png')
    black_knight_small = pygame.transform.scale(black_knight, (small_piece_size, small_piece_size))
    black_pawn = pygame.image.load('img/black-pawn.png')
    black_pawn_small = pygame.transform.scale(black_pawn, (small_piece_size, small_piece_size))

    white_queen = pygame.image.load('img/white-queen.png')
    white_queen_small = pygame.transform.scale(white_queen, (small_piece_size, small_piece_size))
    white_king = pygame.image.load('img/white-king.png')
    white_king_small = pygame.transform.scale(white_king, (small_piece_size, small_piece_size))
    white_rook = pygame.image.load('img/white-rook.png')
    white_rook_small = pygame.transform.scale(white_rook, (small_piece_size, small_piece_size))
    white_bishop = pygame.image.load('img/white-bishop.png')
    white_bishop_small = pygame.transform.scale(white_bishop, (small_piece_size, small_piece_size))
    white_knight = pygame.image.load('img/white-knight.png')
    white_knight_small = pygame.transform.scale(white_knight, (small_piece_size, small_piece_size))
    white_pawn = pygame.image.load('img/white-pawn.png')
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
        'piece_size': piece_size,
        'pawn_size': 50,
        'small_piece_size': small_piece_size,
        'piece_images': piece_images,
        'small_piece_images': small_piece_images,
        'piece': piece_list
    }
    return result


def get_logger():
    # Create a custom logger
    logger = logging.getLogger("server_logger")

    # sets the log level to DEBUG, which is one of the lowest log levels
    # and will include messages of all severity levels,
    # including DEBUG, INFO, WARNING, ERROR, and CRITICAL.
    logger.setLevel(logging.DEBUG)

    # Create a log formatter
    # Create a colored log formatter
    log_formatter = colorlog.ColoredFormatter(
        '%(white)s%(asctime)s - %(log_color)s%(levelname)s - %(message)s',
        log_colors={
            'DEBUG': 'blue',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white'
        }
    )

    # Create a console (stdout) handler
    log_console_handler = logging.StreamHandler()

    # Set the formatter for the console handler
    log_console_handler.setFormatter(log_formatter)

    logger.addHandler(log_console_handler)
    return logger


class Message:
    DISCONNECT = -1
    READY = 1
    IN_QUEUE = 0
    PLAY = 'PLAY'
    VIEW = 'VIEW'
    REPLAY = 'REPLAY'
    NO_SELECTION = 999_999_999
    ALL_DATA = 'ALL DATA'
    VIEWING = 'VIEWING'
    STOP_VIEWING = 'STOP_VIEWING'


if __name__ == '__main__':
    pass
