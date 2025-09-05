from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import chess
import os
import chess_ai  # Import AI logic
get_best_move = chess_ai.get_best_move
is_castling = chess_ai.is_castling

app = Flask(__name__, static_folder="static")
CORS(app)

@app.route("/")
def home():
    return "Chess AI Backend is Running!"


@app.route("/set_color", methods=["POST"])
def set_color():
    """Sets the player color and resets the board."""
    data = request.json
    color = data.get("color")

    if color not in ["white", "black"]:
        return jsonify({"error": "Invalid color"}), 400

    # Use the AI module's function to set color and reset board
    chess_ai.set_player_color(color)
    
    return jsonify({"fen": chess_ai.get_board_fen()})


# ------------------------- GAME ROUTES -------------------------

@app.route("/new_game", methods=["POST"])
def new_game():
    """Resets the chess game."""
    chess_ai.board = chess.Board()
    chess_ai.transposition_table.clear()
    return jsonify({"message": "Game restarted", "fen": chess_ai.board.fen()})

@app.route("/get_board", methods=["GET"])
def get_board():
    """Returns the current board state (FEN) and checkmate status."""
    return jsonify({
        "fen": chess_ai.get_board_fen(),
        "checkmate": chess_ai.board.is_checkmate()
    })

@app.route("/player_move", methods=["POST"])
def player_move():
    data = request.get_json()
    move_uci = data.get("move")

    # Check if this is a promotion move without actually making it
    if len(move_uci) == 4:  # Basic move without promotion
        move = chess.Move.from_uci(move_uci)
        if (chess_ai.board.piece_at(move.from_square) and 
            chess_ai.board.piece_at(move.from_square).piece_type == chess.PAWN and
            ((move.to_square >= 56 and chess_ai.board.turn == chess.WHITE) or 
             (move.to_square <= 7 and chess_ai.board.turn == chess.BLACK))):
            # This is a promotion move, return promotion flag
            return jsonify({
                "fen": chess_ai.board.fen(),
                "promotion": True,
                "move": move_uci
            })
    
    # For non-promotion moves, proceed normally
    if move_uci not in [m.uci() for m in chess_ai.board.legal_moves]:
        return jsonify({"error": "Illegal move"}), 400

    move = chess.Move.from_uci(move_uci)
    
    #Check if move is a capture or castling
    is_capture = chess_ai.board.is_capture(move)
    is_castle = is_castling(chess.Move.from_uci(move_uci))
    chess_ai.board.push(move)  #Push move to board

    is_checkmate = chess_ai.board.is_checkmate()
    is_check = chess_ai.board.is_check()

    return jsonify({
        "fen": chess_ai.board.fen(),
        "checkmate": is_checkmate,
        "check": is_check,
        "capture": is_capture,  
        "castling": is_castle,
        "promotion": False,
        "last_move": move_uci
    })


@app.route("/promote", methods=["POST"])
def promote():
    """Handles pawn promotion."""
    data = request.get_json()
    move_uci = data.get("move")
    promotion_piece = data.get("promotion", "q")
    
    # Create the full move with promotion
    full_move_uci = move_uci + promotion_piece
    
    if full_move_uci not in [m.uci() for m in chess_ai.board.legal_moves]:
        return jsonify({"error": "Illegal promotion move"}), 400
    
    move = chess.Move.from_uci(full_move_uci)
    chess_ai.board.push(move)
    
    is_checkmate = chess_ai.board.is_checkmate()
    is_check = chess_ai.board.is_check()
    
    return jsonify({
        "fen": chess_ai.board.fen(),
        "checkmate": is_checkmate,
        "check": is_check,
        "promotion": True,
        "promoted_piece": promotion_piece
    })

@app.route("/ai_move", methods=["GET"])
def ai_move():
    """Handles AI move using Minimax from chess_ai.py."""
    if chess_ai.board.is_game_over():
        return jsonify({
            "status": "game over", 
            "message": chess_ai.board.result(),
            "fen": chess_ai.board.fen()
        })

    # Get AI move
    best_move = chess_ai.get_best_move(chess_ai.board)
    
    if not best_move:
        return jsonify({
            "status": "no move", 
            "message": "No legal moves available",
            "fen": chess_ai.board.fen()
        })
    
    # Check move properties before making it
    is_capture = chess_ai.board.is_capture(best_move)
    is_castle = chess_ai.is_castling(best_move)
    is_promotion = best_move.promotion is not None
    
    # Make the AI move
    chess_ai.board.push(best_move)
    
    # Check game state after AI move
    is_checkmate = chess_ai.board.is_checkmate()
    is_check = chess_ai.board.is_check()
    
    return jsonify({
        "status": "success",
        "move": best_move.uci(),
        "fen": chess_ai.board.fen(),
        "checkmate": is_checkmate,
        "check": is_check,
        "capture": is_capture,
        "castling": is_castle,
        "promotion": is_promotion
    })

# ------------------------- STATIC FILES -------------------------

@app.route("/pieces/<filename>")
def get_piece_image(filename):
    """Serves chess piece images from static/pieces/."""
    return send_from_directory(os.path.join(app.static_folder, "pieces"), filename)

@app.route("/sounds/<filename>")
def get_sound(filename):
    """Serves sound files from static/sounds/."""
    return send_from_directory(os.path.join(app.static_folder, "sounds"), filename)

# ------------------------- RUN SERVER -------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use Render's PORT
    app.run(debug=True)
