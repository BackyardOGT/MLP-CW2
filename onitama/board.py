# TODO: game logic, see react code

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
        p1CardsInit = Cards()
        p2CardsInit = Cards()

        self.player1 = Player(True, p1CardsInit)
        self.player2 = Player(False, p2CardsInit)
        self.isPlayer1 = True

    def get(self):
        """
        Returns dict with positions in [row, col], zero-indexed
        In API format for front end, for each player:
        player1 : { king : [2], pawns : [[2], ..., [2]], cards: [ [5x5],  [5x5]]}
        """
        print({**self.player1.to_dict(), **self.player2.to_dict()})
        return {**self.player1.to_dict(), **self.player2.to_dict(), "player": 1 if self.isPlayer1 else 2}

    def step(self, move):
        print(move)
        if self.isPlayer1:
            self.player1.step(move, Cards())
        else:
            self.player2.step(move, Cards())
        self.isPlayer1 = not self.isPlayer1
        return self.get()
