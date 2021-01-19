import React from "react";
import king2 from "../assets/pieces/king2.png";
import king1 from "../assets/pieces/king1.png";
import pawn2 from "../assets/pieces/pawn2.png";
import pawn1 from "../assets/pieces/pawn1.png";

function Piece({
  name,
  pos,
  player,
  i,
  currentPlayer,
  clickSquare,
  setPieceSelected,
}) {
  let [row, col] = pos;
  const clickHandler = () => {
    console.log("Piece clicked", name, pos, currentPlayer, player);
    if (currentPlayer === player) {
      setPieceSelected({ name, player, i, pos });
    } else if (player !== currentPlayer) {
      // try to take
      clickSquare(pos);
    }
  };
  return (
    <div
      onClick={clickHandler}
      style={{
        gridRow: row + 1,
        gridColumn: col + 1,
        height: "100%",
        width: "100%",
        overflow: "hidden",
      }}
    >
      <img
        style={{
          height: "100%",
        }}
        src={
          player === 1
            ? name === "king"
              ? king1
              : pawn1
            : name === "king"
            ? king2
            : pawn2
        }
        alt={name}
      />
    </div>
  );
}

function King(props) {
  return <Piece {...props} name={"king"} />;
}

function Pawn(props) {
  return <Piece {...props} name={"pawn"} />;
}

export { King, Pawn };
