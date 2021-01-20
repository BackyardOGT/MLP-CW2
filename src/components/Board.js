import React, { useState, useEffect } from "react";
import { King, Pawn } from "./Pieces";
import * as mathjs from "mathjs";

export default function Board({
  state,
  bindSquares,
  setPieceSelected,
  currentPlayer,
  pieceSelected,
  cardSelected,
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
          pieceSelected={pieceSelected}
          bindSquares={bindSquares}
          cardSelected={cardSelected}
          currentPlayer={currentPlayer}
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

export function Square({
  pos,
  pieceSelected,
  currentPlayer,
  cardSelected,
  bindSquares,
}) {
  const [i, j] = pos;
  const initColour = (i + j) % 2 === 0 ? "red" : "transparent";
  const [colour, setColour] = useState(initColour);

  const clickHandler = () => {
    if (bindSquares) bindSquares(pos);
  };

  useEffect(() => {
    const colourValidMove = () => {
      let newColour = initColour;
      const cardData = cardSelected.data;
      // where on card is this wrt selected piece
      const [iCard, jCard] = mathjs.subtract(
        mathjs.add([i, j], [2, 2]),
        pieceSelected.pos
      );
      // need to flip if other player
      let iFlipped = currentPlayer === 2 ? 5 - iCard - 1 : iCard;
      let jFlipped = currentPlayer === 2 ? 5 - jCard - 1 : jCard;
      // card values are 1 and 0
      if (0 <= iFlipped && iFlipped <= 4 && 0 <= jFlipped && jFlipped <= 4) {
        if (cardData[iFlipped][jFlipped]) {
          newColour = "orange";
        }
      }
      setColour(newColour);
    };

    if (pieceSelected && cardSelected) {
      colourValidMove();
    } else {
      setColour(initColour);
    }
  }, [initColour, pieceSelected, cardSelected, i, j, currentPlayer]);

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
