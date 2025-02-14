import os
import chess
import pygame

# Initialize Pygame
pygame.init()

# Disable sound if running on a headless server like Render
if "RENDER" in os.environ:
    pygame.mixer.quit()
else:
    pygame.mixer.init()


piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Piece values with positional evaluation bonus
piece_square_tables = {
    chess.PAWN: [
        0, 5, 5, 0, 5, 10, 50, 0,
        0, 10, -5, 0, 5, 10, 50, 0,
        0, 10, 10, 20, 20, 10, 50, 0,
        0, 20, 20, 35, 35, 20, 50, 0,
        0, 20, 20, 35, 35, 20, 50, 0,
        0, 10, 10, 20, 20, 10, 50, 0,
        0, 10, -5, 0, 5, 10, 50, 0,
        0, 5, 5, 0, 5, 10, 50, 0
    ],
    chess.KNIGHT: [
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20, 0, 5, 5, 0, -20, -40,
        -30, 5, 10, 15, 15, 10, 5, -30,
        -30, 0, 15, 20, 20, 15, 0, -30,
        -30, 5, 15, 20, 20, 15, 5, -30,
        -30, 0, 10, 15, 15, 10, 0, -30,
        -40, -20, 0, 0, 0, 0, -20, -40,
        -50, -40, -30, -30, -30, -30, -40, -50
    ],
}


# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_DIR = os.path.join(BASE_DIR, "static", "sounds")
PIECES_DIR = os.path.join(BASE_DIR, "static", "pieces")

# Load sound effects
move_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "move.wav"))
capture_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "capture.wav"))
check_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "check.wav"))
checkmate_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "checkmate.wav"))
castle_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "castle.wav"))

# Initialize chess board
board = chess.Board()
player_color = chess.WHITE  # Default to White; will be set by frontend

def set_player_color(color):
    """Sets the player color based on frontend input."""
    global player_color, board
    player_color = chess.WHITE if color == "white" else chess.BLACK
    board = chess.Board()  # Reset board

    # If the user chooses Black, AI plays first
    if player_color == chess.BLACK:
        ai_move()

def get_board_fen():
    """Returns the current FEN string of the board for the frontend."""
    return board.fen()

def make_move(move):
    """Processes the player's move if it's legal."""
    if move in [m.uci() for m in board.legal_moves]:
        play_move_sound(move)
        board.push(chess.Move.from_uci(move))
        return True
    return False

def ai_move():
    """Generates and plays AI's best move."""
    if not board.is_game_over():
        best_move = get_best_move(board)
        if best_move:
            play_move_sound(best_move.uci())
            board.push(best_move)

def play_move_sound(move):
    """Plays the correct sound effect based on the move type before making the move."""
    move_obj = chess.Move.from_uci(move)
    target_square = move_obj.to_square  # Square where the piece is moving
    is_capture = board.piece_at(target_square) is not None  # Check BEFORE move is made

    if board.is_checkmate():
        checkmate_sound.play()
    elif board.is_check():
        check_sound.play()
    elif is_capture:
        capture_sound.play()
    elif is_castling(move):
        castle_sound.play()
    else:
        move_sound.play()

def is_castling(move):
    """Checks if a move is a castling move."""
    move_obj = chess.Move.from_uci(move)
    return abs(move_obj.from_square - move_obj.to_square) == 2

def get_best_move(board, depth=3):
    """Returns the best move using Minimax with Alpha-Beta Pruning."""
    if board.is_game_over():
        return None

    best_move = None
    best_value = float('-inf') if board.turn == chess.WHITE else float('inf')

    for move in board.legal_moves:
        board.push(move)
        move_value = evaluate_board(board)
        board.pop()

        if board.turn == chess.WHITE and move_value > best_value:
            best_value = move_value
            best_move = move
        elif board.turn == chess.BLACK and move_value < best_value:
            best_value = move_value
            best_move = move

    return best_move

# Evaluate board state
def evaluate_board(board):
    """
    Evaluates the board by considering material values and positional bonuses.
    """
    if board.is_checkmate():
        return -100000 if board.turn else 100000
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_value = piece_values.get(piece.piece_type, 0)
            position_bonus = piece_square_tables.get(piece.piece_type, [0] * 64)[square] if piece.piece_type in piece_square_tables else 0
            piece_score = piece_value + position_bonus
            score += piece_score if piece.color == chess.WHITE else -piece_score

    return score

def order_moves(board):
    """
    Orders moves to improve alpha-beta pruning efficiency.
    Prioritizes captures and checks.
    """
    moves = list(board.legal_moves)
    scored_moves = []

    for move in moves:
        board.push(move)
        move_score = evaluate_board(board)
        board.pop()
        scored_moves.append((move_score, move))

    scored_moves.sort(reverse=board.turn, key=lambda x: x[0])  # Sort high to low if maximizing
    return [move for _, move in scored_moves]

def quiescence_search(board, alpha, beta):
    """
    Extends Minimax when in a capture sequence to prevent horizon effect.
    """
    stand_pat = evaluate_board(board)
    if stand_pat >= beta:
        return beta
    alpha = max(alpha, stand_pat)

    for move in order_moves(board):
        if board.is_capture(move):
            board.push(move)
            score = -quiescence_search(board, -beta, -alpha)
            board.pop()
            if score >= beta:
                return beta
            alpha = max(alpha, score)

    return alpha


# Minimax with Alpha-Beta Pruning
def minimax(board, depth, alpha, beta, maximizing):
    """
    Minimax Algorithm with Alpha-Beta Pruning, Move Ordering, and Quiescence Search.
    """
    if depth == 0 or board.is_game_over():
        return quiescence_search(board, alpha, beta)

    legal_moves = order_moves(board)

    if maximizing:
        max_eval = float('-inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cutoff
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha cutoff
        return min_eval
    
