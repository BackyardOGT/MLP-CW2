import React, { useEffect, useState } from "react";

export function CardSquare({ pos, player, data }) {
  const [i, j] = pos;
  const initColour = (i + j) % 2 === 0 ? "red" : "transparent";
  const [colour, setColour] = useState(initColour);

  useEffect(() => {
    // if it's valid then blue
    // server is row, col
    if (data[player === 2 ? 5 - i - 1 : i][player === 2 ? 5 - j - 1 : j]) {
      setColour("blue");
    }
    if (i === j && i === 2) {
      setColour("green");
    }
  }, [data, player, i, j]);

  return (
    <div
      style={{
        background: colour,
        gridRow: pos[0] + 1,
        gridColumn: pos[1] + 1,
      }}
    />
  );
}

export default function Card({
  data,
  id,
  player,
  currentPlayer,
  setCardSelected,
}) {
  const onClick = () => {
    if (player === currentPlayer) setCardSelected({ id, data });
  };

  // 5 x 5 grid of divs
  let i, j;
  let squares = [];
  for (i = 0; i < 5; i++) {
    for (j = 0; j < 5; j++) {
      squares.push(
        <CardSquare
          key={"card" + player + id + i + ", " + j}
          pos={[i, j]}
          player={player}
          data={data}
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
