import React, { useState } from "react";
import { King, Pawn } from "./Pieces";
import { bin } from "mathjs";
import * as mathjs from "mathjs";

export default function Board({
  state,
  bindSquares,
  boardColours,
  setPieceSelected,
  currentPlayer,
  pieceSelected,
}) {
  // 5 x 5 grid of divs
  let i, j;
  let squares = [];
  for (i = 0; i < 5; i++) {
    for (j = 0; j < 5; j++) {
      squares.push(
        <Square
          key={i + ", " + j}
          pos={[i, j]}
          colour={boardColours[i][j]}
          bindSquares={bindSquares}
        />
      );
    }
  }

  // place pieces
  let pieces = [];
  const placePlayer = (data, player) => {
    // king
    pieces.push(
      <King
        key={player + "king"}
        player={player}
        pos={data.king}
        clickSquare={bindSquares}
        setPieceSelected={setPieceSelected}
        currentPlayer={currentPlayer}
        pieceSelected={pieceSelected}
      />
    );
    // pawns
    data.pawns.map((pos, i) =>
      pieces.push(
        <Pawn
          key={player + "pawn" + i}
          pos={pos}
          i={i}
          player={player}
          clickSquare={bindSquares}
          setPieceSelected={setPieceSelected}
          currentPlayer={currentPlayer}
          pieceSelected={pieceSelected}
        />
      )
    );
  };

  placePlayer(state.player1, 1);
  placePlayer(state.player2, 2);

  return (
    <div
      style={{
        width: 500,
        height: 500,
        display: "grid",
        gridTemplateRows: "1fr ".repeat(5),
        gridTemplateColumns: "1fr ".repeat(5),
      }}
    >
      {squares}
      {pieces}
    </div>
  );
}

export function getInitBoard() {
  let initBoardColours = Array.from({ length: 5 }, () =>
    Array.from({ length: 5 }, () => "transparent")
  );
  // chess board pattern
  let i, j;
  for (i = 0; i < 5; i++) {
    for (j = 0; j < 5; j++) {
      if ((i + j) % 2 === 0) {
        // coloured squares
        // +1 bc css grids are 1-indexed
        initBoardColours[i][j] = "red";
      }
    }
  }
  return initBoardColours;
}

export function Square({ pos, colour, bindSquares }) {
  const clickHandler = () => {
    if (bindSquares) bindSquares(pos);
  };

  return (
    <div
      style={{
        background: colour,
        gridRow: pos[0] + 1,
        gridColumn: pos[1] + 1,
      }}
      onClick={clickHandler}
    />
  );
}
