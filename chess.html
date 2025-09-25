import React, { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { Chess } from "chess.js";

// ---------------- AI Lokal (Minimax + Alpha-Beta) ----------------
class ChessAI {
  constructor(depth = 2) {
    this.depth = depth;
  }

  evaluate(board) {
    const values = { p: 1, n: 3, b: 3, r: 5, q: 9, k: 0 };
    let score = 0;
    for (let row of board) {
      for (let piece of row) {
        if (!piece) continue;
        const val = values[piece.type] || 0;
        score += piece.color === "w" ? val : -val;
      }
    }
    return score;
  }

  search(game, depth, alpha, beta, maximizingPlayer) {
    if (depth === 0 || game.isGameOver()) {
      return this.evaluate(game.board());
    }
    const moves = game.moves();
    if (maximizingPlayer) {
      let maxEval = -Infinity;
      for (let move of moves) {
        game.move(move);
        const evalScore = this.search(game, depth - 1, alpha, beta, false);
        game.undo();
        maxEval = Math.max(maxEval, evalScore);
        alpha = Math.max(alpha, evalScore);
        if (beta <= alpha) break;
      }
      return maxEval;
    } else {
      let minEval = Infinity;
      for (let move of moves) {
        game.move(move);
        const evalScore = this.search(game, depth - 1, alpha, beta, true);
        game.undo();
        minEval = Math.min(minEval, evalScore);
        beta = Math.min(beta, evalScore);
        if (beta <= alpha) break;
      }
      return minEval;
    }
  }

  bestMove(game) {
    let bestMove = null;
    let bestEval = -Infinity;
    for (let move of game.moves()) {
      game.move(move);
      const evalScore = this.search(
        game,
        this.depth - 1,
        -Infinity,
        Infinity,
        false
      );
      game.undo();
      if (evalScore > bestEval) {
        bestEval = evalScore;
        bestMove = move;
      }
    }
    return bestMove;
  }
}

// ---------------- Komponen Catur ----------------
const files = ["a", "b", "c", "d", "e", "f", "g", "h"];

function Square({ piece, isBlack, onClick }) {
  return (
    <motion.div
      onClick={onClick}
      className={`w-16 h-16 flex items-center justify-center cursor-pointer ${
        isBlack ? "bg-green-700" : "bg-green-200"
      }`}
      whileTap={{ scale: 0.9 }}
    >
      {piece && (
        <span className="text-2xl">
          {piece.color === "w" ? piece.type.toUpperCase() : piece.type}
        </span>
      )}
    </motion.div>
  );
}

export default function ChessBoard() {
  const [game, setGame] = useState(new Chess());
  const [selected, setSelected] = useState(null);
  const [board, setBoard] = useState(game.board());
  const [status, setStatus] = useState("Game on!");

  const ai = new ChessAI(3); // depth = 3 (cukup kuat)

  const handleClick = (row, col) => {
    const square = files[col] + (8 - row);
    if (selected) {
      const move = { from: selected, to: square };
      const result = game.move(move);
      if (result) {
        setBoard(game.board());
        setSelected(null);
        setTimeout(() => makeAIMove(), 500);
      } else {
        setSelected(null);
      }
    } else {
      setSelected(square);
    }
  };

  const makeAIMove = () => {
    if (game.isGameOver()) {
      setStatus("Game Over");
      return;
    }
    const move = ai.bestMove(game);
    if (move) {
      game.move(move);
      setBoard(game.board());
    }
  };

  useEffect(() => {
    setBoard(game.board());
  }, [game]);

  return (
    <div className="flex flex-col items-center gap-4 p-4">
      <Card className="shadow-xl">
        <CardContent>
          <div className="grid grid-cols-8 border-4 border-brown-700">
            {board.map((row, rowIndex) =>
              row.map((piece, colIndex) => (
                <Square
                  key={rowIndex + "-" + colIndex}
                  piece={piece}
                  isBlack={(rowIndex + colIndex) % 2 === 1}
                  onClick={() => handleClick(rowIndex, colIndex)}
                />
              ))
            )}
          </div>
        </CardContent>
      </Card>
      <div className="flex gap-2">
        <Button onClick={() => window.location.reload()}>Restart</Button>
      </div>
      <p>{status}</p>
    </div>
  );
}
