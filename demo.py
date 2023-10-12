import chess

board = chess.Board()

print(board)



# square_to_check = chess.square(0, 0)
#
# # Use the piece_at method to get the piece on the specified square
# piece_on_square = board.piece_at(square_to_check)
#
# if piece_on_square is not None:
#     print(f"Piece on square {chess.square_name(square_to_check)}: {piece_on_square.symbol()}")
# else:
#     print(f"No piece on square {chess.square_name(square_to_check)}")


# move = chess.Move.from_uci("e2e6")
#
# if move in board.legal_moves:
#     board.push(move)
#     print("Valid move.")
# else:
#     print("Invalid move.")


# Get a dictionary of all pieces and their positions on the board
piece_map = board.piece_map()

for square, piece in piece_map.items():
    print(f"Square: {chess.square_name(square)}, Piece: {piece.symbol()}")

for move in board.legal_moves:
    print(move)


# # Specify the square you want to check (e.g., e2)
# square_to_check = chess.square(4, 1)  # This represents square e2
#
# # Use the piece_at method to get the piece on the specified square
# piece_on_square = board.piece_at(square_to_check)
#
# if piece_on_square is not None:
#     print(f"Piece on square {chess.square_name(square_to_check)}: {piece_on_square.symbol()}")
# else:
#     print(f"No piece on square {chess.square_name(square_to_check)}")