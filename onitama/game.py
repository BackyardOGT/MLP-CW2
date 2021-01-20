import numpy as np


class Piece:
    def __init__(self, name, state):
        self.name = name
        self.state = state

    def get(self):
        return self.state

    def set(self, state):
        self.state = state


class King(Piece):
    def __init__(self, state):
        super().__init__("king", state)

    def move(self, pos):
        self.set(pos)


class Pawns(Piece):
    def __init__(self, state):
        super().__init__("pawns", state)

    def move(self, pos, i):
        newState = self.state
        newState[i] = pos
        self.set(newState)

    def taken(self, item):
        self.state.remove(item)


class Cards:
    def __init__(self):
        self.card1 = [[0, 0, 0, 0, 0],
                      [0, 0, 1, 0, 0],
                      [0, 1, 0, 1, 0],
                      [0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0], ]
        self.card2 = [[0, 0, 0, 1, 0],
                      [0, 1, 0, 1, 0],
                      [0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0], ]

    def get(self):
        return [self.card1, self.card2]


class Player:
    def __init__(self, isPlayer1, cards):
        if isPlayer1:
            row = 4
            self.player = "player1"
        else:
            row = 0
            self.player = "player2"
        self.cards = cards
        # init pieces
        self.king = King([row, 2])
        self.pawns = Pawns([[row, i] for i in range(5) if i != 2])

    def to_dict(self):
        return {self.player: {"king": self.king.get(), "pawns": self.pawns.get(), "cards": self.cards.get()}}

    def step(self, move, cards):
        if move["name"] == "king":
            self.king.move(move["pos"])
        elif move["name"] == "pawn":
            self.pawns.move(move["pos"], move["i"])
        self.cards = cards


class Game:
    def __init__(self):
        # TODO
        self.reset()

    def get(self, done=False):
        """
        Returns dict with positions in [row, col], zero-indexed
        In API format for front end, for each player:
        player1 : { king : [2], pawns : [[2], ..., [2]], cards: [ [5x5],  [5x5]]}
        player: 1 / 2
        done: false / true when game done
        """
        return {**self.player1.to_dict(),
                **self.player2.to_dict(),
                "player": 1 if self.isPlayer1 else 2,
                "done": done}

    def step(self, move):
        """
        :param move:
            name: king / pawn
            id: card played
            i: (pawns only) index of pawn
            player: 1 / 2
            pos: position moved to
        :return: self.get()
        """
        if not self.check_valid_move(move):
            print("Invalid move")
            return self.get()

        if self.isPlayer1:
            self.player1.step(move, Cards())
        else:
            self.player2.step(move, Cards())

        if self.check_win(move):
            return self.get(done=True)

        self.handle_take_pawn(move)
        self.isPlayer1 = not self.isPlayer1
        return self.get()

    def reset(self):
        p1CardsInit = Cards()
        p2CardsInit = Cards()

        self.player1 = Player(True, p1CardsInit)
        self.player2 = Player(False, p2CardsInit)
        self.isPlayer1 = True

    def check_valid_move(self, move):
        # TODO: test
        if (self.isPlayer1):
            return self.check_unoccupied(self.player1, move) and self.check_move_on_card(self.player1, move)
        else:
            return self.check_unoccupied(self.player2, move) and self.check_move_on_card(self.player2, move)

    def check_unoccupied(self, player, move):
        piece = move["name"]
        pos = move["pos"]
        if piece == "king":
            for pawnPos in player.pawns.get():
                if pos == pawnPos:
                    return False
        elif piece == "pawn":
            i = int(move["i"])
            for pawnPos, j in enumerate(player.pawns.get()):
                if pos == pawnPos and i != j:
                    return False
            return not pos == player.king.get()
        return True

    def check_win(self, move):
        return False

    def handle_take_pawn(self, move):
        if (self.isPlayer1):
            self._handle_take_pawn(self.player2, move)
        else:
            self._handle_take_pawn(self.player1, move)

    def _handle_take_pawn(self, playerOther, move):
        pos = move["pos"]
        for pawnPos in playerOther.pawns.get():
            if pos == pawnPos:
                playerOther.pawns.taken(pawnPos)


    def check_move_on_card(self, player, move):
        cardId = int(move["id"])
        pos = move["pos"]
        piece = move["name"]
        if piece == "king":
            piecePos = player.king.get()
        else:  # pawn
            i = int(move["i"])
            piecePos = player.pawns.get()[i]
        posOnCard = np.subtract(np.add(pos, [2, 2]), piecePos)
        if not self.isPlayer1:
            posOnCard = np.subtract([4, 4], posOnCard)
        if np.all(posOnCard >= 0) and np.all(posOnCard <= 4):
            if player.cards.get()[cardId][posOnCard[0]][posOnCard[1]]:  # 1s and 0s so T/F
                return True
        return False
