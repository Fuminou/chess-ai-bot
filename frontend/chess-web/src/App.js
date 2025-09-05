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
    const [showPromotionModal, setShowPromotionModal] = useState(false);
    const [pendingMove, setPendingMove] = useState(null);

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
          // Step 1: Make the player's move
          const playerResponse = await axios.post(`${API_URL}/player_move`, { move });
          
          // Check if this move requires promotion
          if (playerResponse.data.promotion) {
              setPendingMove(move);
              setShowPromotionModal(true);
              return;
          }
          
          // Update board with player's move immediately
          setFen(playerResponse.data.fen);
  
          // Play player move sound
          if (playerResponse.data.checkmate) {
              playSound("checkmate");
              setIsCheckmate(true);
              setWinner("Checkmate! You won against the bot! 🎉");
              setSelectedSquare(null);
              return;
          } else if (playerResponse.data.check) {
              playSound("check");
          } else if (playerResponse.data.capture) {
              playSound("capture");
          } else if (playerResponse.data.castling) {
              playSound("castling");
          } else {
              playSound("move");
          }
          
          // Step 2: Get AI move after a short delay
          setTimeout(async () => {
              try {
                  const aiResponse = await axios.get(`${API_URL}/ai_move`);
                  
                  if (aiResponse.data.status === "success") {
                      // Update board with AI move
                      setFen(aiResponse.data.fen);
                      
                      // Play AI move sound
                      if (aiResponse.data.checkmate) {
                          playSound("checkmate");
                          setIsCheckmate(true);
                          setWinner("Checkmate! You lost to the bot! 🤖");
                      } else if (aiResponse.data.check) {
                          playSound("check");
                      } else if (aiResponse.data.capture) {
                          playSound("capture");
                      } else if (aiResponse.data.castling) {
                          playSound("castling");
                      } else {
                          playSound("move");
                      }
                  }
              } catch (error) {
                  console.error("Error getting AI move:", error);
              }
          }, 500); // 500ms delay before AI moves
          
      } catch (error) {
          console.error("Illegal move");
      }
  
      setSelectedSquare(null);
  };

    const handlePromotion = async (promotionPiece) => {
        if (!pendingMove) return;
        
        try {
            // Step 1: Handle promotion move
            const promotionResponse = await axios.post(`${API_URL}/promote`, { 
                move: pendingMove, 
                promotion: promotionPiece 
            });
            
            setFen(promotionResponse.data.fen);
            setShowPromotionModal(false);
            setPendingMove(null);
            
            // Play promotion sound
            playSound("move");
            
            // Check for checkmate after promotion
            if (promotionResponse.data.checkmate) {
                playSound("checkmate");
                setIsCheckmate(true);
                setWinner("Checkmate! You won against the bot! 🎉");
                return;
            }
            
            // Step 2: Get AI move after promotion
            setTimeout(async () => {
                try {
                    const aiResponse = await axios.get(`${API_URL}/ai_move`);
                    
                    if (aiResponse.data.status === "success") {
                        // Update board with AI move
                        setFen(aiResponse.data.fen);
                        
                        // Play AI move sound
                        if (aiResponse.data.checkmate) {
                            playSound("checkmate");
                            setIsCheckmate(true);
                            setWinner("Checkmate! You lost to the bot! 🤖");
                        } else if (aiResponse.data.check) {
                            playSound("check");
                        } else if (aiResponse.data.capture) {
                            playSound("capture");
                        } else if (aiResponse.data.castling) {
                            playSound("castling");
                        } else {
                            playSound("move");
                        }
                    }
                } catch (error) {
                    console.error("Error getting AI move after promotion:", error);
                }
            }, 500); // 500ms delay before AI moves
            
        } catch (error) {
            console.error("Error promoting pawn:", error);
        }
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
                        <h2>Game Over!</h2>
                        <p className={winner.includes("lost to the bot") ? "bot-win" : winner.includes("won against the bot") ? "player-win" : ""}>
                            {winner}
                        </p>
                        <button 
                            className="close-button" 
                            onClick={() => {
                                setIsCheckmate(false);
                                setWinner("");
                            }}
                        >
                            Close
                        </button>
                    </div>
                </div>
            )}

            {/*Promotion Modal */}
            {showPromotionModal && (
                <div className="modal">
                    <div className="modal-content">
                        <h2>Choose Promotion Piece</h2>
                        <div className="promotion-pieces">
                            <button 
                                className="promotion-piece" 
                                onClick={() => handlePromotion('q')}
                            >
                                ♕ Queen
                            </button>
                            <button 
                                className="promotion-piece" 
                                onClick={() => handlePromotion('r')}
                            >
                                ♖ Rook
                            </button>
                            <button 
                                className="promotion-piece" 
                                onClick={() => handlePromotion('b')}
                            >
                                ♗ Bishop
                            </button>
                            <button 
                                className="promotion-piece" 
                                onClick={() => handlePromotion('n')}
                            >
                                ♘ Knight
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default ChessApp;
