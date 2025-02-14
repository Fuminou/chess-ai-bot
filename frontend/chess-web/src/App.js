import React, { useState, useEffect } from "react";
import Chessboard from "chessboardjsx";
import axios from "axios";
import "./App.css";

//Load sound files
const moveSound = new Audio("/sounds/move.wav");
const captureSound = new Audio("/sounds/capture.wav");
const checkSound = new Audio("/sounds/check.wav");
const checkmateSound = new Audio("/sounds/checkmate.wav");
const castleSound = new Audio("/sounds/castle.wav");


const API_URL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:5000";

const playMoveSound = (move, checkmate, check, capture, castle) => {
  if (checkmate) {
      checkmateSound.play();
  } else if (check) {
      checkSound.play();
  } else if (capture) {
      captureSound.play();
  } else if (castle) {
      castleSound.play();
  } else {
      moveSound.play();
  }
};


function ChessApp() {
    const [fen, setFen] = useState("start");
    const [playerColor, setPlayerColor] = useState(null);
    const [isCheckmate, setIsCheckmate] = useState(false);
    const [winner, setWinner] = useState("");
    const [selectedSquare, setSelectedSquare] = useState(null);

    useEffect(() => {
        if (playerColor) {
            fetchBoard();
        }
    }, [playerColor]);

    const selectColor = async (color) => {
        try {
            const response = await axios.post(`${API_URL}/set_color`, { color });
            setPlayerColor(color);
            setFen(response.data.fen);
            setIsCheckmate(false);
        } catch (error) {
            console.error("Error setting player color:", error);
        }
    };

    const fetchBoard = async () => {
      try {
          const response = await axios.get(`${API_URL}/get_board`);
          setFen(response.data.fen);
  
          if (response.data.checkmate) {
              setIsCheckmate(true);
              setWinner(playerColor === "white" ? "Black Wins!" : "White Wins!");
          }
      } catch (error) {
          console.error("Error fetching board:", error);
      }
  };
  
    const restartGame = async () => {
        try {
            const response = await axios.post(`${API_URL}/set_color`, { color: playerColor });
            setFen(response.data.fen);
            setIsCheckmate(false);
        } catch (error) {
            console.error("Error restarting game:", error);
        }
    };

    const goBack = () => {
        setPlayerColor(null);
        setFen("start");
        setIsCheckmate(false);
    };

    //Handles both click and drag moves
    const makeMove = async (move) => {
      if (!playerColor || isCheckmate) return;
  
      try {
          const response = await axios.post(`${API_URL}/player_move`, { move });
  
          playMoveSound(
              move, 
              response.data.checkmate, 
              response.data.check, 
              response.data.capture, 
              response.data.castle
          );
  
          setFen(response.data.fen);
          await fetchBoard();
  
      } catch (error) {
          console.error("Illegal move:", error);
      }
      setSelectedSquare(null);
  };
  

    //Click-Based Movement Handling
    const handleSquareClick = async (square) => {
        if (!playerColor || isCheckmate) return;

        if (!selectedSquare) {
            setSelectedSquare(square); // Select piece
        } else {
            const move = selectedSquare + square;
            await makeMove(move); // Send move
        }
    };

    //Drag-and-Drop Movement Handling
    const onDrop = async ({ sourceSquare, targetSquare }) => {
        await makeMove(sourceSquare + targetSquare);
    };

    if (!playerColor) {
        return (
            <div className="container">
                <h1>Choose Your Side</h1>
                <button onClick={() => selectColor("white")}>Play as White</button>
                <button onClick={() => selectColor("black")}>Play as Black</button>
            </div>
        );
    }

    return (
        <div className="container">
            <h1>Chess AI Bot Project - Joon Yuan Chong</h1>
            <Chessboard 
                position={fen} 
                orientation={playerColor === "black" ? "black" : "white"} 
                onSquareClick={handleSquareClick} //Click-based movement
                onDrop={onDrop} //Drag-and-drop movement
                squareStyles={{
                    [selectedSquare]: { backgroundColor: "rgba(255, 255, 0, 0.5)" } //Highlight selected piece
                }}
            />
            <div className="buttons">
                <button onClick={restartGame}>Restart Game</button>
                <button onClick={goBack}>Go Back</button>
            </div>

            {/*Checkmate Modal Pop-up */}
            {isCheckmate && (
                <div className="modal">
                    <div className="modal-content">
                        <h2>Checkmate!</h2>
                        <p>{winner}</p>
                    </div>
                </div>
            )}
        </div>
    );
}

export default ChessApp;
