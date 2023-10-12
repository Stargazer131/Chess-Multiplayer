import chess

# Create a chess board
board = chess.Board()

# Make moves
board.push(chess.Move.from_uci('e2e4'))  # White's move
board.push(chess.Move.from_uci('e7e5'))  # Black's move
board.push(chess.Move.from_uci('e4e5'))  # White's move

# Access the total number of full moves
total_moves = board.fullmove_number

print(f"Total number of moves: {total_moves}")