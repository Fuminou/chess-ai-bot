import React, { useState, useEffect } from "react";
import Chessboard from "chessboardjsx";
import axios from "axios";
import "./App.css";


const API_URL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:5000";

function playSound(type) {
  let sound = "";
  switch (type) {
      case "move":
          sound = "move.wav";
          break;
      case "capture":
          sound = "capture.wav";
          break;
      case "check":
          sound = "check.wav";
          break;
      case "checkmate":
          sound = "checkmate.wav";
          break;
      case "castle":
          sound = "castle.wav";
          break;
      default:
          return;
  }

  const audio = new Audio(`/sounds/${sound}`);
  audio.volume = 1.0; // Set volume
  audio.play().catch(e => console.error("Audio Play Error:", e));
}


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
    if (!playerColor) return;

    try {
        const response = await axios.post(`${API_URL}/set_color`, { color: playerColor });
        setFen(response.data.fen);
        setIsCheckmate(false);
        setWinner("");
    } catch (error) {
        console.error("Error restarting game:", error);
    }
};

    const goBack = () => {
        setPlayerColor(null);
        setFen("start");
        setIsCheckmate(false);
    };

    const makeMove = async (move) => {
      if (!playerColor || isCheckmate) return;
  
      try {
          const response = await axios.post(`${API_URL}/player_move`, { move });
          setFen(response.data.fen);
  
          //Play correct sound effect
          if (response.data.checkmate) {
              playSound("checkmate");
              setIsCheckmate(true);
              setWinner(playerColor === "white" ? "Black Wins!" : "White Wins!");
          } else if (response.data.check) {
              playSound("check");
          } else if (response.data.capture) {
              playSound("capture");
          } else if (response.data.castling) {
              playSound("castling");
          } else {
              playSound("move");
          }
  
          //Play AI move sounds with delay
          if (response.data.ai_last_move) {
              setTimeout(() => {
                  if (response.data.ai_capture) {
                      playSound("capture");
                  } else if (response.data.ai_castling) {
                      playSound("castling");
                  } else {
                      playSound("move");
                  }
              }, 1); // Delay for AI move
          }
      } catch (error) {
          console.error("Illegal move");
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
