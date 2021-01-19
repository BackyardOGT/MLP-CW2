import React from "react";
import { Square } from "./Board";

function getInitCard(card, player) {
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
      // if it's valid then blue
      // server is row, col
      if (card[player === 2 ? 5 - i - 1 : i][player === 2 ? 5 - j - 1 : j]) {
        initBoardColours[i][j] = "blue";
      }
      if (i === j && i === 2) {
        initBoardColours[i][j] = "green";
      }
    }
  }
  return initBoardColours;
}

export default function Card({ data, id, player, setCardSelected }) {
  const onClick = () => {
    console.log("Card", id);
    setCardSelected(id);
  };

  const cardColours = getInitCard(data, player);
  // 5 x 5 grid of divs
  let i, j;
  let squares = [];
  for (i = 0; i < 5; i++) {
    for (j = 0; j < 5; j++) {
      squares.push(
        <Square
          key={"card" + player + id + i + ", " + j}
          pos={[i, j]}
          colour={cardColours[i][j]}
        />
      );
    }
  }
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
      }}
    >
      <div
        style={{
          width: 300,
          height: 300,
          display: "grid",
          gridTemplateRows: "1fr ".repeat(5),
          gridTemplateColumns: "1fr ".repeat(5),
        }}
        onClick={onClick}
      >
        {squares}
      </div>
      Player {player}
    </div>
  );
}
