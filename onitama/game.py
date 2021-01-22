import numpy as np

from cards import get_init_cards


KING_ID = -1
# Pawn ids = [0, 4]

class Piece:
    def __init__(self, pos, id):
        self.id = id
        self.pos = pos

    def get(self):
        return self.pos

    def move(self, pos):
        self.pos = pos


class Move:
    """
    Parses json to move object
    """
    def __init__(self, json):
        self.pos = json["pos"]  # [row, col]
        self.isKing = json["name"] == "king"  # T/F
        self.i = -1 if self.isKing else int(json["i"])  # [0-4] for pawn, KING_ID for king
        self.cardId = int(json["id"])  # 0 / 1 for card


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
        self.king = Piece([row, 2], KING_ID)
        self.pawns = [Piece([row, i],  i) for i in range(5) if i != 2]

    def to_dict(self):
        return {self.player: {"king": self.king.get(), "pawns": [p.get() for p in self.pawns], "cards": self.cards}}

    def step(self, move, card):
        """
        Updates piece and card objects, validation etc. done in Game class
        """
        if move.isKing:
            self.king.move(move.pos)
        else:  # it's pawn
            self.pawns[move.i].move(move.pos)
        # swap card
        self.cards[int(move.cardId)] = card


class Game:
    def __init__(self):
        self.reset()

    def get(self, done=False):
        """
        Returns dict with positions in [row, col], zero-indexed
        In API format for front end, for each player:
        player1 : { king : [2], pawns : [[2], ..., [2]], cards: [ [5x5],  [5x5]]}
        player: 1 / 2        // which player
        spare_card: [5 x 5]  // card data
        done: false / true   // when game done
        """
        return {**self.player1.to_dict(),
                **self.player2.to_dict(),
                "player": 1 if self.isPlayer1 else 2,
                "spare_card": self.spare_card,
                "done": done}

    def stepApi(self, moveJson):
        move = Move(moveJson)
        return self.step(move)

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
        p1CardsInit, p2CardsInit, [spare_card] = get_init_cards()

        self.player1 = Player(True, p1CardsInit)
        self.player2 = Player(False, p2CardsInit)
        self.isPlayer1 = True

        self.spare_card = spare_card

    def check_valid_move(self, move):
        curP, otherP = self.get_current_players()
        return self.check_unoccupied(curP, move) and self.check_move_on_card(curP, move)

    def check_unoccupied(self, player, move):
        """
        Checks this is unoccupied by any of own pieces
        """
        if move.isKing:
            for pawn in player.pawns:
                if np.all(move.pos == pawn.get()):
                    return False
        else:
            i = int(move.i)
            for j, pawn in enumerate(player.pawns):
                if np.all(move.pos == pawn.get) and i != j:
                    return False
            if np.all(move.pos == player.king.get()):
                return False
        return True

    def check_move_on_card(self, player, move):
        if move.isKing:
            piecePos = player.king.get()
        else:  # pawn
            i = int(move.i)
            piecePos = player.pawns[i].get()
        posOnCard = np.subtract(np.add(move.pos, [2, 2]), piecePos)
        if not self.isPlayer1:
            posOnCard = np.subtract([4, 4], posOnCard)
        if np.all(posOnCard >= 0) and np.all(posOnCard <= 4):
            if player.cards[move.cardId][posOnCard[0]][posOnCard[1]]:  # 1s and 0s so T/F
                return True
        return False

    def get_current_players(self):
        """
        :return: each player object current player (whose turn it is), and other player
        """
        current_player = self.player1 if self.isPlayer1 else self.player2
        other_player = self.player2 if self.isPlayer1 else self.player1
        return current_player, other_player

    def reached_goal(self, player):
        """
        Called post movement so check if king in goal
        """
        goalPos = [0, 2] if self.isPlayer1 else [4, 2]
        return np.all(player.king.get() == goalPos)

    def handle_cards(self, curP, move):
        """
        Updates current spare card, returns new card for player
        """
        cardId = move.cardId  # 0 or 1 so other is not cardId
        card = self.spare_card
        self.spare_card = curP.cards[cardId]
        return card

    def handle_take(self, otherP, move):
        """
        Returns true if king taken -> game is won
        """
        self.handle_take_pawn(otherP, move)
        return self.check_take_king(otherP, move)

    def handle_take_pawn(self, playerOther, move):
        for pawn in playerOther.pawns:
            if np.all(move.pos == pawn.get()):
                playerOther.pawns.taken(pawn.get())

    def check_take_king(self, otherP, move):
        """
         If move takes king, return True, game is won
        """
        if np.all(move.pos == otherP.king.get()):
            return True
        return False
