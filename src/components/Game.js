import React, { useState, useEffect } from "react";
import Card from "./Card";
import Board, { Square } from "./Board";
import * as mathjs from "mathjs";
import "./Game.css";
/*
 * TODO: clean up and comment
 *  TODO: corner case: It is possible that you will find that you cannot use any of your cards to make a legal move. If this happens - and only then - you must pass your turn.
 *    None of your pawns will move. But like the river that constantly flows, you cannot remain unchanged: you must still choose one of the two cards in front of you, place it to the left of the playmat and rotate it, then take the card from the right side of the board.
 */

export default function Game({ state, sendMove, resetGame }) {
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

  function validMove(pos) {
    if (pieceSelected) {
      const [i, j] = pos;
      const cardData = cardSelected.data;
      // where on card is this wrt selected piece
      const [iCard, jCard] = mathjs.subtract(
        mathjs.add([i, j], [2, 2]),
        pieceSelected.pos
      );
      // need to flip if other player
      let iFlipped = currentPlayer === 2 ? 4 - iCard : iCard;
      let jFlipped = currentPlayer === 2 ? 4 - jCard : jCard;
      // card values are 1 and 0
      if (0 <= iFlipped && iFlipped <= 4 && 0 <= jFlipped && jFlipped <= 4) {
        if (cardData[iFlipped][jFlipped]) {
          return true;
        }
      }
    }
    return false;
  }

  function bindSquares(pos) {
    // note this can be called from squares and from pieces
    // where pieces need to propagate click down eg. when taking
    // check occupied done in squares / pieces
    // here we just check it's a valid move on the card
    if (validMove(pos)) {
      sendMove(pieceSelected, cardSelected, pos);
      afterMove();
    } else {
      setPieceSelected(null);
    }
  }

  return (
    <div
      style={{
        marginTop: 25,
        display: "flex",
        flexDirection: "column",
        height: "100%",
        width: "100%",
        justifyContent: "space-around",
      }}
    >
      <div
        style={{
          display: "flex",
          width: "100%",
          justifyContent: "space-around",
        }}
      >
        <div className="cardDiv">
          <h2>Player 1</h2>
          <Card
            data={state.player1.cards[0]}
            player={1}
            id={0}
            setCardSelected={setCardSelected}
            currentPlayer={currentPlayer}
            cardSelected={cardSelected}
          />
          <Card
            data={state.player1.cards[1]}
            player={1}
            id={1}
            setCardSelected={setCardSelected}
            currentPlayer={currentPlayer}
            cardSelected={cardSelected}
          />
        </div>
        <Board
          state={state}
          bindSquares={bindSquares}
          setPieceSelected={setPieceSelected}
          currentPlayer={currentPlayer}
          pieceSelected={pieceSelected}
          cardSelected={cardSelected}
          playerData={playerData}
        />
        <div className="cardDiv">
          <h2>Player 2</h2>
          <Card
            data={state.player2.cards[0]}
            player={2}
            id={0}
            setCardSelected={setCardSelected}
            currentPlayer={currentPlayer}
            cardSelected={cardSelected}
          />
          <Card
            data={state.player1.cards[1]}
            player={2}
            id={1}
            setCardSelected={setCardSelected}
            currentPlayer={currentPlayer}
            cardSelected={cardSelected}
          />
        </div>
      </div>
      <div
        style={{
          display: "flex",
          margin: "0 auto",
          marginTop: 25,
          width: "50%",
          justifyContent: "space-around",
        }}
      >
        <Card data={state.spare_card} player={1} currentPlayer={1} id="next" />
        <div
          style={{
            margin: 10,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
          }}
        >
          <button onClick={resetGame}>Reset</button>
          <p>Turn: Player {currentPlayer}</p>
        </div>
      </div>
    </div>
  );
}
