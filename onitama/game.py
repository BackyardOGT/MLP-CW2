import copy

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


# TODO: properly
card1 = [[0, 0, 0, 0, 0],
         [0, 0, 1, 0, 0],
         [0, 1, 0, 1, 0],
         [0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0], ]
card2 = [[0, 0, 0, 1, 0],
         [0, 1, 0, 1, 0],
         [0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0], ]
card3 = [[0, 0, 0, 0, 0],
         [0, 1, 0, 0, 0],
         [0, 1, 0, 0, 0],
         [0, 1, 0, 0, 0],
         [1, 0, 0, 0, 0], ]


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
        return {self.player: {"king": self.king.get(), "pawns": self.pawns.get(), "cards": self.cards}}

    def step(self, move, card):
        if move["name"] == "king":
            self.king.move(move["pos"])
        elif move["name"] == "pawn":
            self.pawns.move(move["pos"], move["i"])
        # swap card
        self.cards[int(move["id"])] = card


class Game:
    def __init__(self):
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
                "spare_card": self.spare_card,
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

        curP, otherP = self.get_current_players()
        kingTaken = self.handle_take(otherP, move)
        newCards = self.handle_cards(curP, move)
        curP.step(move, newCards)
        if self.reached_goal(curP) or kingTaken:
            print("Done")
            return self.get(done=True)

        self.isPlayer1 = not self.isPlayer1
        return self.get()

    def reset(self):
        p1CardsInit = [card1, card2]
        p2CardsInit = [card1, card2]

        self.player1 = Player(True, p1CardsInit)
        self.player2 = Player(False, p2CardsInit)
        self.isPlayer1 = True

        self.spare_card = card3

    def check_valid_move(self, move):
        # TODO: can't move into check
        curP, otherP = self.get_current_players()
        return self.check_unoccupied(curP, move) and self.check_move_on_card(curP, move)

    def check_unoccupied(self, player, move):
        """
        Checks this is unoccupied by any of own pieces
        """
        piece = move["name"]
        pos = move["pos"]
        if piece == "king":
            for pawnPos in player.pawns.get():
                if np.all(pos == pawnPos):
                    return False
        elif piece == "pawn":
            i = int(move["i"])
            for j, pawnPos in enumerate(player.pawns.get()):
                if np.all(pos == pawnPos) and i != j:
                    return False
            if np.all(pos == player.king.get()):
                return False
        return True

    def handle_take_pawn(self, playerOther, move):
        pos = move["pos"]
        for pawnPos in playerOther.pawns.get():
            if np.all(pos == pawnPos):
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
            if player.cards[cardId][posOnCard[0]][posOnCard[1]]:  # 1s and 0s so T/F
                return True
        return False

    def get_current_players(self):
        current_player = self.player1 if self.isPlayer1 else self.player2
        other_player = self.player2 if self.isPlayer1 else self.player1
        return current_player, other_player

    def reached_goal(self, player):
        # this is post move so check if king in goal
        goalPos = [0, 2] if self.isPlayer1 else [4, 2]
        return np.all(player.king.get() == goalPos)

    def handle_cards(self, curP, move):
        """
        Updates current spare card, returns new card for player
        """
        cardId = move["id"]  # 0 or 1 so other is not cardId
        card = self.spare_card
        self.spare_card = curP.cards[cardId]
        return card

    def handle_take(self, otherP, move):
        """
        Returns true if king taken -> game is won
        """
        self.handle_take_pawn(otherP, move)
        return self.handle_take_king(otherP, move)

    def handle_take_king(self, otherP, move):
        """
        Takes king if can, return True if so as game won
        """
        if np.all(move["pos"] == otherP.king.get()):
            return True
        return False
