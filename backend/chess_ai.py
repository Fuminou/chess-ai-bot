import os
import chess
import pygame

# Initialize Pygame
pygame.init()

# Disable sound if running on Render (headless server)
USE_SOUND = "RENDER" not in os.environ

if USE_SOUND:
    pygame.mixer.init()
else:
    pygame.mixer.quit()

piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Advanced piece-square tables for different game phases
piece_square_tables = {
    chess.PAWN: [
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ],
    chess.KNIGHT: [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50
    ],
    chess.BISHOP: [
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20
    ],
    chess.ROOK: [
        0,  0,  0,  0,  0,  0,  0,  0,
        5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        5, 10, 10, 10, 10, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ],
    chess.QUEEN: [
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
        -5,  0,  5,  5,  5,  5,  0, -5,
        0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
    ],
    chess.KING: [
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
        20, 20,  0,  0,  0,  0, 20, 20,
        20, 30, 10,  0,  0, 10, 30, 20
    ]
}

# Endgame piece-square tables (when few pieces remain)
endgame_piece_square_tables = {
    chess.PAWN: [
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        30, 30, 30, 30, 30, 30, 30, 30,
        20, 20, 20, 20, 20, 20, 20, 20,
        10, 10, 10, 10, 10, 10, 10, 10,
        5,  5,  5,  5,  5,  5,  5,  5,
        0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0
    ],
    chess.KING: [
        -50,-40,-30,-20,-20,-30,-40,-50,
        -30,-20,-10,  0,  0,-10,-20,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-30,  0,  0,  0,  0,-30,-30,
        -50,-30,-30,-30,-30,-30,-30,-50
    ]
}


# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_DIR = os.path.join(BASE_DIR, "static", "sounds")
PIECES_DIR = os.path.join(BASE_DIR, "static", "pieces")

# Load sound effects
if USE_SOUND:
    move_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "move.wav"))
    capture_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "capture.wav"))
    check_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "check.wav"))
    checkmate_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "checkmate.wav"))
    castle_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "castle.wav"))

# Initialize chess board
board = chess.Board()
player_color = chess.WHITE  # Default to White; will be set by frontend

# Transposition table for better performance
transposition_table = {}

# Move history to prevent repetition
move_history = []

# Strategic opening book with development principles
opening_book = {
    # Starting position
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": ["e2e4", "d2d4", "g1f3", "c2c4"],
    
    # After 1.e4
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1": ["e7e5", "c7c5", "e7e6", "c7c6"],
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": ["g1f3", "f1c4", "b1c3"],
    "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3": ["f1c4", "b1c3", "d2d3"],
    
    # After 1.d4
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1": ["d7d5", "g8f6", "e7e6", "c7c5"],
    "rnbqkb1r/pppppppp/5n2/8/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 0 2": ["c2c4", "b1c3", "g1f3"],
    
    # After 1.Nf3
    "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq - 0 1": ["d7d5", "g8f6", "c7c5", "e7e6"],
}

def set_player_color(color):
    """Sets the player color based on frontend input."""
    global player_color, board, transposition_table, move_history
    print(f"Setting player color to: {color}")
    player_color = chess.WHITE if color == "white" else chess.BLACK
    board = chess.Board()  # Reset board
    transposition_table.clear()  # Clear transposition table for new game
    move_history.clear()  # Clear move history for new game
    print(f"Player color set to: {player_color}, Board FEN: {board.fen()}")

    # If the user chooses Black, AI plays first
    if player_color == chess.BLACK:
        print("Player chose Black, AI will make first move")
        ai_move()
    else:
        print("Player chose White, player will move first")

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
    global board, move_history
    print(f"ai_move called. Game over: {board.is_game_over()}, Turn: {board.turn}")
    
    if board.is_game_over():
        print("Game is over, AI cannot move")
        return
        
    legal_moves = list(board.legal_moves)
    print(f"AI thinking... Turn: {board.turn}, Legal moves: {len(legal_moves)}")
    
    if not legal_moves:
        print("No legal moves available!")
        return
        
    # Get the best move
    best_move = get_best_move(board)
    
    if best_move and best_move in legal_moves:
        print(f"AI playing: {best_move.uci()}")
        # Verify the move is still legal
        if best_move in board.legal_moves:
            play_move_sound(best_move)
            board.push(best_move)
            # Track move history for anti-repetition
            move_history.append(best_move.uci())
            # Keep only recent moves (last 20 moves)
            if len(move_history) > 20:
                move_history.pop(0)
            print(f"Board after AI move: {board.fen()}")
        else:
            print("Move became illegal, playing first legal move")
            board.push(legal_moves[0])
            move_history.append(legal_moves[0].uci())
    else:
        print("AI found no valid move, playing first legal move")
        board.push(legal_moves[0])
        move_history.append(legal_moves[0].uci())

def play_move_sound(move):
    if not USE_SOUND:
        return  # No sound on Render

    # Handle both string (UCI) and move object inputs
    if isinstance(move, str):
        move_obj = chess.Move.from_uci(move)
    else:
        move_obj = move
    
    target_square = move_obj.to_square
    is_capture = board.piece_at(target_square) is not None  

    if board.is_checkmate():
        checkmate_sound.play()
    elif board.is_check():
        check_sound.play()
    elif is_capture:
        capture_sound.play()
    elif is_castling(move_obj):
        castle_sound.play()
    else:
        move_sound.play()

def is_castling(move):
    """Checks if a move is a castling move."""
    return abs(move.from_square - move.to_square) == 2

def get_best_move(board, depth=3):
    """Returns the best move using simple Minimax with Alpha-Beta Pruning."""
    if board.is_game_over():
        return None

    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None

    # Check opening book first (only in first 5 moves)
    if board.fullmove_number <= 5:
        current_fen = board.fen()
        if current_fen in opening_book:
            book_moves = opening_book[current_fen]
            for move_uci in book_moves:
                try:
                    move = chess.Move.from_uci(move_uci)
                    if move in legal_moves:
                        print(f"Using opening book move: {move_uci}")
                        return move
                except:
                    continue

    # Smart move selection with anti-repetition
    move_scores = []
    
    for move in legal_moves:
        # Make a copy of the board for evaluation
        board_copy = board.copy()
        board_copy.push(move)
        
        # Evaluate the position after this move
        move_value = simple_minimax(board_copy, depth - 1, float('-inf'), float('inf'), board.turn == chess.BLACK)
        
        # Anti-repetition: penalize moves that repeat recent positions
        repetition_penalty = 0
        recent_moves = move_history[-6:] if len(move_history) >= 6 else move_history
        move_uci = move.uci()
        
        # Count how often this move was played recently
        repetition_count = recent_moves.count(move_uci)
        if repetition_count > 0:
            repetition_penalty = repetition_count * 100  # Heavy penalty for repetition
        
        # Adjust move value based on repetition
        if board.turn == chess.WHITE:
            adjusted_value = move_value - repetition_penalty
        else:
            adjusted_value = move_value + repetition_penalty
            
        move_scores.append((adjusted_value, move))
    
    # Sort moves by score
    if board.turn == chess.WHITE:
        move_scores.sort(key=lambda x: x[0], reverse=True)  # Highest score first
    else:
        move_scores.sort(key=lambda x: x[0])  # Lowest score first
    
    # Select the best non-repetitive move
    best_move = move_scores[0][1] if move_scores else legal_moves[0]
    
    return best_move

def simple_evaluate(board):
    """
    Smart chess evaluation with opening principles and strategic factors.
    """
    if board.is_checkmate():
        return -10000 if board.turn == chess.WHITE else 10000
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    
    # Material evaluation
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_value = piece_values.get(piece.piece_type, 0)
            if piece.color == chess.WHITE:
                score += piece_value
            else:
                score -= piece_value

    # Opening principles (first 15 moves)
    if board.fullmove_number <= 15:
        score += evaluate_opening_principles(board)
    
    # Strategic factors
    score += evaluate_piece_activity(board)
    score += evaluate_king_safety_simple(board)
    score += evaluate_center_control_simple(board)
    
    # Anti-repetition: penalize moving the same piece repeatedly
    score += evaluate_piece_development(board)

    return score

def evaluate_opening_principles(board):
    """Evaluate adherence to opening principles."""
    score = 0
    
    # Reward piece development
    developed_pieces = 0
    
    # Check if knights and bishops are developed
    for square in [chess.B1, chess.G1]:  # White knights
        piece = board.piece_at(square)
        if not piece or piece.piece_type != chess.KNIGHT:
            developed_pieces += 1
    
    for square in [chess.C1, chess.F1]:  # White bishops
        piece = board.piece_at(square)
        if not piece or piece.piece_type != chess.BISHOP:
            developed_pieces += 1
            
    for square in [chess.B8, chess.G8]:  # Black knights
        piece = board.piece_at(square)
        if not piece or piece.piece_type != chess.KNIGHT:
            developed_pieces -= 1
    
    for square in [chess.C8, chess.F8]:  # Black bishops
        piece = board.piece_at(square)
        if not piece or piece.piece_type != chess.BISHOP:
            developed_pieces -= 1
    
    score += developed_pieces * 30
    
    # Reward castling
    if board.has_castling_rights(chess.WHITE):
        if not board.has_kingside_castling_rights(chess.WHITE) and not board.has_queenside_castling_rights(chess.WHITE):
            score += 50  # Already castled
    else:
        score += 20  # Lost castling rights but might have castled
        
    if board.has_castling_rights(chess.BLACK):
        if not board.has_kingside_castling_rights(chess.BLACK) and not board.has_queenside_castling_rights(chess.BLACK):
            score -= 50  # Already castled
    else:
        score -= 20  # Lost castling rights but might have castled
    
    # Penalize early queen moves
    white_queen_square = None
    black_queen_square = None
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.QUEEN:
            if piece.color == chess.WHITE:
                white_queen_square = square
            else:
                black_queen_square = square
    
    if white_queen_square and white_queen_square != chess.D1:
        score -= 20  # Penalize early queen development
    if black_queen_square and black_queen_square != chess.D8:
        score += 20  # Penalize opponent's early queen development
    
    return score

def evaluate_piece_activity(board):
    """Evaluate piece activity and mobility."""
    score = 0
    
    # Count legal moves (mobility)
    white_mobility = 0
    black_mobility = 0
    
    if board.turn == chess.WHITE:
        white_mobility = len(list(board.legal_moves))
        # Switch turns to count black mobility
        board_copy = board.copy()
        board_copy.push(chess.Move.null()) if hasattr(chess.Move, 'null') else None
        if hasattr(chess.Move, 'null'):
            black_mobility = len(list(board_copy.legal_moves))
    else:
        black_mobility = len(list(board.legal_moves))
    
    score += (white_mobility - black_mobility) * 2
    
    return score

def evaluate_king_safety_simple(board):
    """Simple king safety evaluation."""
    score = 0
    
    # Penalize king in center during opening/middlegame
    if board.fullmove_number <= 20:
        white_king = board.king(chess.WHITE)
        black_king = board.king(chess.BLACK)
        
        center_squares = [chess.D4, chess.D5, chess.E4, chess.E5, chess.C4, chess.C5, chess.F4, chess.F5]
        
        if white_king in center_squares:
            score -= 50
        if black_king in center_squares:
            score += 50
    
    return score

def evaluate_center_control_simple(board):
    """Simple center control evaluation."""
    score = 0
    center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
    
    for square in center_squares:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE:
                score += 20
            else:
                score -= 20
    
    return score

def evaluate_piece_development(board):
    """Reward piece development and penalize repetitive moves."""
    score = 0
    
    # Count pieces on starting squares (penalize underdevelopment)
    starting_squares = {
        chess.A1: chess.ROOK, chess.H1: chess.ROOK,
        chess.B1: chess.KNIGHT, chess.G1: chess.KNIGHT,
        chess.C1: chess.BISHOP, chess.F1: chess.BISHOP,
        chess.A8: chess.ROOK, chess.H8: chess.ROOK,
        chess.B8: chess.KNIGHT, chess.G8: chess.KNIGHT,
        chess.C8: chess.BISHOP, chess.F8: chess.BISHOP,
    }
    
    for square, expected_piece in starting_squares.items():
        piece = board.piece_at(square)
        if piece and piece.piece_type == expected_piece:
            if piece.color == chess.WHITE:
                score -= 10  # Penalize underdeveloped white pieces
            else:
                score += 10  # Reward opponent's underdeveloped pieces
    
    return score

# Evaluate board state
def evaluate_board(board):
    """
    Evaluates the board by considering material values, positional bonuses, and tactical factors.
    """
    if board.is_checkmate():
        return -100000 if board.turn else 100000
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    
    # Determine game phase (opening/middlegame vs endgame)
    total_pieces = sum(1 for square in chess.SQUARES if board.piece_at(square))
    is_endgame = total_pieces <= 12  # Endgame when 12 or fewer pieces remain
    
    # Material and positional evaluation
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_value = piece_values.get(piece.piece_type, 0)
            
            # Use different piece-square tables based on game phase
            if is_endgame and piece.piece_type in endgame_piece_square_tables:
                position_bonus = endgame_piece_square_tables[piece.piece_type][square]
            else:
                position_bonus = piece_square_tables.get(piece.piece_type, [0] * 64)[square] if piece.piece_type in piece_square_tables else 0
            
            piece_score = piece_value + position_bonus
            score += piece_score if piece.color == chess.WHITE else -piece_score

    # Additional positional factors
    score += evaluate_mobility(board)
    score += evaluate_king_safety(board)
    score += evaluate_pawn_structure(board)
    score += evaluate_center_control(board)
    
    return score

def evaluate_mobility(board):
    """Evaluate piece mobility (how many squares each piece can move to)."""
    try:
        # Simple mobility evaluation - just count current player's legal moves
        mobility = len(board.legal_moves)
        return mobility * 2  # Reward mobility
    except:
        return 0

def evaluate_king_safety(board):
    """Evaluate king safety based on pawn shield and piece attacks."""
    score = 0
    white_king_square = board.king(chess.WHITE)
    black_king_square = board.king(chess.BLACK)
    
    if white_king_square is not None:
        # Count pawns protecting the king
        white_king_rank = chess.square_rank(white_king_square)
        white_king_file = chess.square_file(white_king_square)
        white_pawn_shield = 0
        for file_offset in [-1, 0, 1]:
            if 0 <= white_king_file + file_offset <= 7:
                pawn_square = chess.square(white_king_file + file_offset, white_king_rank - 1)
                if board.piece_at(pawn_square) == chess.Piece(chess.PAWN, chess.WHITE):
                    white_pawn_shield += 1
        score += white_pawn_shield * 10
    
    if black_king_square is not None:
        # Count pawns protecting the king
        black_king_rank = chess.square_rank(black_king_square)
        black_king_file = chess.square_file(black_king_square)
        black_pawn_shield = 0
        for file_offset in [-1, 0, 1]:
            if 0 <= black_king_file + file_offset <= 7:
                pawn_square = chess.square(black_king_file + file_offset, black_king_rank + 1)
                if board.piece_at(pawn_square) == chess.Piece(chess.PAWN, chess.BLACK):
                    black_pawn_shield += 1
        score -= black_pawn_shield * 10
    
    return score

def evaluate_pawn_structure(board):
    """Evaluate pawn structure (doubled, isolated, passed pawns)."""
    score = 0
    
    # Check for doubled pawns
    for file in range(8):
        white_pawns = 0
        black_pawns = 0
        for rank in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.PAWN:
                if piece.color == chess.WHITE:
                    white_pawns += 1
                else:
                    black_pawns += 1
        if white_pawns > 1:
            score -= (white_pawns - 1) * 20  # Penalty for doubled pawns
        if black_pawns > 1:
            score += (black_pawns - 1) * 20  # Penalty for doubled pawns
    
    return score

def evaluate_center_control(board):
    """Evaluate control of center squares."""
    try:
        center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
        score = 0
        
        for square in center_squares:
            # Check if current player controls this square
            current_attacks = any(move.to_square == square for move in board.legal_moves if board.piece_at(move.from_square) and board.piece_at(move.from_square).color == board.turn)
            
            if current_attacks:
                score += 20 if board.turn == chess.WHITE else -20
        
        return score
    except:
        return 0

def order_moves(board):
    """
    Orders moves using MVV-LVA (Most Valuable Victim - Least Valuable Attacker).
    Prioritizes captures, checks, and promotions for better alpha-beta pruning.
    """
    moves = list(board.legal_moves)
    scored_moves = []

    # Piece values for MVV-LVA
    piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, 
                   chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 100}

    for move in moves:
        score = 0
        
        # MVV-LVA for captures
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            attacking_piece = board.piece_at(move.from_square)
            if captured_piece and attacking_piece:
                victim_value = piece_values.get(captured_piece.piece_type, 0)
                attacker_value = piece_values.get(attacking_piece.piece_type, 0)
                score += 10000 + victim_value * 10 - attacker_value
        
        # Check bonus
        if board.gives_check(move):
            score += 1000
        
        # Promotion bonus
        if move.promotion:
            score += 2000 + piece_values.get(move.promotion, 0) * 100
        
        # Center control bonus
        center_squares = [27, 28, 35, 36]  # d4, e4, d5, e5
        if move.to_square in center_squares:
            score += 50
        
        # Castling bonus
        if board.is_castling(move):
            score += 100
        
        scored_moves.append((score, move))

    scored_moves.sort(reverse=True, key=lambda x: x[0])  # Sort high to low
    return [move for _, move in scored_moves]

def quiescence_search(board, alpha, beta, depth=0):
    """
    Extends Minimax when in a capture sequence to prevent horizon effect.
    """
    if depth >= 6:  # Limit quiescence depth
        return evaluate_board(board)
        
    stand_pat = evaluate_board(board)
    if stand_pat >= beta:
        return beta
    alpha = max(alpha, stand_pat)

    # Get all captures and checks
    moves = []
    for move in board.legal_moves:
        if board.is_capture(move) or board.gives_check(move):
            moves.append(move)
    
    # Order moves by MVV-LVA
    moves = order_moves(board)
    
    for move in moves:
        if board.is_capture(move) or board.gives_check(move):
            board.push(move)
            score = -quiescence_search(board, -beta, -alpha, depth + 1)
            board.pop()
            if score >= beta:
                return beta
            alpha = max(alpha, score)

    return alpha


def simple_minimax(board, depth, alpha, beta, maximizing):
    """
    Simple Minimax Algorithm with Alpha-Beta Pruning using board copies.
    """
    if depth == 0 or board.is_game_over():
        return simple_evaluate(board)

    legal_moves = list(board.legal_moves)
    
    if maximizing:
        max_eval = float('-inf')
        for move in legal_moves:
            # Use board copy to avoid modifying original
            board_copy = board.copy()
            board_copy.push(move)
            eval_score = simple_minimax(board_copy, depth - 1, alpha, beta, False)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Beta cutoff
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            # Use board copy to avoid modifying original
            board_copy = board.copy()
            board_copy.push(move)
            eval_score = simple_minimax(board_copy, depth - 1, alpha, beta, True)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Alpha cutoff
        return min_eval
    
