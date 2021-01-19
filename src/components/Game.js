import React, { useState } from "react";
import Card from "./Card";
import Board, { getInitBoard } from "./Board";
import * as mathjs from "mathjs";
import { pi } from "mathjs";

/*
 * TODO: reset button
 */

export default function Game({ state, sendMove }) {
  const [boardColours, setBoardColours] = useState(getInitBoard());
  const [pieceSelected, setPieceSelected] = useState(null);
  const [cardSelected, setCardSelected] = useState(0);
  const currentPlayer = state.player;

  const playerData = currentPlayer === 1 ? state.player1 : state.player2;

  // after move reset state
  function afterMove() {
    setBoardColours(getInitBoard());
    setPieceSelected(null);
    setCardSelected(0);
  }

  const bindSquares = (pos) => {
    console.log("Square clicked", pos, cardSelected, pieceSelected);
    if (pieceSelected) {
      const posInCard =
        currentPlayer === 2
          ? mathjs.add(mathjs.subtract(pieceSelected.pos, pos), [2, 2])
          : mathjs.add(mathjs.subtract(pos, pieceSelected.pos), [2, 2]);

      // check it's valid move = 1
      console.log("pieceSelected", pieceSelected.pos, "pos", pos);
      console.log(
        "posInCard",
        posInCard,
        playerData.cards[cardSelected][posInCard[0]][posInCard[1]]
      );
      if (playerData.cards[cardSelected][posInCard[0]][posInCard[1]]) {
        sendMove(pieceSelected, cardSelected, pos);
        afterMove();
      }
    }
    setPieceSelected(null);
  };

  const setPieceSelectedWrapped = (piece) => {
    // wraps to update board when piece selected
    setPieceSelected(piece);
    // can't use pieceSelected immediately
    console.log("setPieceSelectedWrapped");
    colourValidMoves(cardSelected, piece);
  };

  const setCardSelectedWrapped = (cardId) => {
    // wraps to update board when piece selected
    setCardSelected(cardId);
    // can't use pieceSelected immediately
    console.log("setCardSelectedWrapped");
    if (pieceSelected) colourValidMoves(cardId, pieceSelected);
  };

  const colourValidMoves = (card, piece) => {
    let newBoardColours = getInitBoard();
    // get card squares
    console.log("playerData", playerData, card);
    const cardData = playerData.cards[card];
    let i, j;
    for (i = 0; i < 5; i++) {
      for (j = 0; j < 5; j++) {
        // need to flip if other player
        let iFlipped = currentPlayer === 2 ? 5 - i - 1 : i;
        let jFlipped = currentPlayer === 2 ? 5 - j - 1 : j;
        // card values are 1 and 0
        if (cardData[iFlipped][jFlipped]) {
          // convert card to board
          const [iBoard, jBoard] = mathjs.add(
            piece.pos,
            mathjs.subtract([i, j], [2, 2])
          );
          if (0 <= iBoard && iBoard <= 4 && 0 <= jBoard && jBoard <= 4) {
            newBoardColours[iBoard][jBoard] = "orange";
          }
        }
      }
      console.log("newColours", newBoardColours);
      setBoardColours(newBoardColours);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        width: "100%",
        justifyContent: "space-around",
      }}
    >
      <Card
        data={state.player1.cards[0]}
        player={1}
        id={0}
        setCardSelected={setCardSelectedWrapped}
      />
      <Card
        data={state.player1.cards[1]}
        player={1}
        id={1}
        setCardSelected={setCardSelectedWrapped}
      />
      <Board
        state={state}
        boardColours={boardColours}
        bindSquares={bindSquares}
        setPieceSelected={setPieceSelectedWrapped}
        currentPlayer={currentPlayer}
        pieceSelected={pieceSelected}
      />
      <Card
        data={state.player2.cards[0]}
        player={2}
        id={0}
        setCardSelected={setCardSelectedWrapped}
      />
      <Card
        data={state.player1.cards[1]}
        player={2}
        id={1}
        setCardSelected={setCardSelectedWrapped}
      />
    </div>
  );
}
