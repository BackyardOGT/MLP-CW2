import numpy as np


class RandomAgent:
    def __init__(self, isPlayer1=False):
        """
        Assumes player 2 as this is normal
        """
        self.isPlayer1 = isPlayer1
        np.random.seed(1123)

    def get_action(self, state):
        """
        State is a game object eg. PvP
        """
        player = state.player1 if self.isPlayer1 else state.player2
        ac = np.random.choice(state.get_valid_moves(player))
        return ac


class SimpleAgent:
    '''
    Simple agent objectives (in order of priority).
    1) Attempts to move king to enemy home or capture enemy king
    2) If own king is attackable: move king to random safe square
    2) Attempts to capture an enemy pawn without it being attackable
    3) Attempts to move a random piece without it being attackable
    4) Attempts to move a random piece
    BUG ALERT: 5) Edge case problem where no valid moves are possible not handled
    '''
    def __init__(self):
        np.random.seed(9753)

    def get_action(self, state):

        # The agent is player 2
        all_moves = state.get_valid_moves(state.player2)
        opponent_moves = state.get_valid_moves(state.player1)

        # Agent king, opponent king, and opponent pawn positions
        king = state.player2.king # [r,c]
        opp_king = state.player1.king # [r,c]
        opp_pawns = state.player1.pawns # [[r,c]]

        # Winning moves
        winning_moves = [move for move in all_moves if move.isKing and move.pos == [0,2]
                                                    or move.pos == opp_king.pos]

        # Safe moves are moves which end up on a square not attackable by an opponents piece
        safe_moves = [move for move in all_moves if move.pos not in [opp_move.pos for opp_move in opponent_moves]]

        # Safe captures are safe moves where a pawn is captured
        safe_captures = [move for move in safe_moves if move.pos in [opp_pawn.pos for opp_pawn in opp_pawns]]

        if len(winning_moves) > 0:
            return winning_moves[0]
        elif king.pos in [opponent_move.pos for opponent_move in opponent_moves]:
            king_moves = [move for move in safe_moves if move.isKing]
            if len(king_moves) > 0:
                return np.random.choice(king_moves)

        if len(safe_captures) > 0:
            return np.random.choice(safe_captures)
        elif len(safe_moves) > 0:
            return np.random.choice(safe_moves)
        else:
            return np.random.choice(all_moves)

    '''
    Simple Agent Problems:

    safe_moves: In the following setting where dashes are empty spaces, X are the
    random agent's pawns and O is an enemy pawn.
    Imagine both Xs can attack diagonally and the O can attack forwards. All pieces could move
    to the central square.
    The move by X to the middle square should be safe because our piece can recapture, but won't
    be in our list.
    [-, -, -, -, -]
    [-, -, O, -, -]
    [-, -, -, -, -]
    [-, X, -, X, -]
    [-, -, -, -, -]

    no attempt made to avoid enemy king winning by reaching our home
    '''
