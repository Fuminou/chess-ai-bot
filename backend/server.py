from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import chess
import os
import chess_ai  # Import AI logic

app = Flask(__name__, static_folder="static")
CORS(app)

board = chess.Board()

@app.route("/set_color", methods=["POST"])
def set_color():
    """Sets the player's color from frontend."""
    data = request.get_json()
    color = data.get("color")
    if color in ["white", "black"]:
        chess_ai.set_player_color(color)
        return jsonify({"status": "success", "fen": chess_ai.get_board_fen()})
    return jsonify({"status": "error", "message": "Invalid color"}), 400


# ------------------------- GAME ROUTES -------------------------

@app.route("/new_game", methods=["POST"])
def new_game():
    """Resets the chess game."""
    global board
    board = chess.Board()
    return jsonify({"message": "Game restarted", "fen": board.fen()})

@app.route("/get_board", methods=["GET"])
def get_board():
    """Returns the current board state (FEN) and checkmate status."""
    return jsonify({
        "fen": chess_ai.get_board_fen(),
        "checkmate": chess_ai.board.is_checkmate()
    })

@app.route("/player_move", methods=["POST"])
def player_move():
    """Handles player moves."""
    data = request.get_json()
    move = data.get("move")
    
    if chess_ai.make_move(move):
        chess_ai.ai_move()  # AI responds after player's move
        return jsonify({"fen": chess_ai.get_board_fen()})
    return jsonify({"error": "Invalid move"}), 400

@app.route("/ai_move", methods=["GET"])
def ai_move():
    """Handles AI move using Minimax from chess_ai.py."""
    global board
    if board.is_game_over():
        return jsonify({"status": "game over", "message": board.result()})

    move = chess_ai.get_best_move(board)
    board.push(move)
    return jsonify({"status": "success", "move": move.uci(), "fen": board.fen()})

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
    app.run(debug=True)
