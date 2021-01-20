import React, { useState, useEffect } from "react";
import Card from "./Card";
import Board from "./Board";
import * as mathjs from "mathjs";

/*
 * TODO: reset button
 */

export default function Game({ state, sendMove }) {
  const [pieceSelected, setPieceSelected] = useState(null);
  const [cardSelected, setCardSelected] = useState(null);
  const currentPlayer = state.player;

  const playerData = currentPlayer === 1 ? state.player1 : state.player2;

  useEffect(() => {
    // init to 1st card
    setCardSelected({ id: 0, data: playerData.cards[0] });
  }, [playerData]);

  // after move reset state
  function afterMove() {
    setPieceSelected(null);
    setCardSelected(0);
  }

  const bindSquares = (pos) => {
    if (pieceSelected) {
      const posInCard =
        currentPlayer === 2
          ? mathjs.add(mathjs.subtract(pieceSelected.pos, pos), [2, 2])
          : mathjs.add(mathjs.subtract(pos, pieceSelected.pos), [2, 2]);

      // check it's valid move = 1
      if (playerData.cards[cardSelected.id][posInCard[0]][posInCard[1]]) {
        sendMove(pieceSelected, cardSelected.id, pos);
        afterMove();
      }
    }
    setPieceSelected(null);
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
        setCardSelected={setCardSelected}
      />
      <Card
        data={state.player1.cards[1]}
        player={1}
        id={1}
        setCardSelected={setCardSelected}
      />
      <Board
        state={state}
        bindSquares={bindSquares}
        setPieceSelected={setPieceSelected}
        currentPlayer={currentPlayer}
        pieceSelected={pieceSelected}
        cardSelected={cardSelected}
      />
      <Card
        data={state.player2.cards[0]}
        player={2}
        id={0}
        setCardSelected={setCardSelected}
      />
      <Card
        data={state.player1.cards[1]}
        player={2}
        id={1}
        setCardSelected={setCardSelected}
      />
    </div>
  );
}
