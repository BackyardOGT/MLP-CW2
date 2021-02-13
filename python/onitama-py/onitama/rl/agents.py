import numpy as np


class RandomAgent:
    def __init__(self, seed, isPlayer1=False):
        """
        Assumes player 2 as this is normal
        """
        self.isPlayer1 = isPlayer1
        print(seed, type(seed))
        np.random.seed(seed)

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
    3) Attempts to capture an enemy pawn without it being attackable
    4) Attempts to move a random piece without it being attackable
    5) Attempts to move a random piece
    '''

    def __init__(self, seed):
        np.random.seed(seed)

    def get_action(self, state):

        # The agent is player 2
        all_moves = state.get_valid_moves(state.player2)
        opp_moves = state.get_valid_moves(state.player1)

        # Agent king, opponent king, and opponent pawn positions
        king = state.player2.king  # [r,c]
        opp_king = state.player1.king  # [r,c]
        opp_pawns = state.player1.pawns  # [[r,c]]

        # Winning moves
        winning_moves = [move for move in all_moves if move.isKing and move.pos == [0, 2]
                         or move.pos == opp_king.pos]

        # Safe moves are moves which end up on a square not attackable by an opponents piece
        safe_moves = [move for move in all_moves if move.pos not in [opp_move.pos for opp_move in opp_moves]]

        # Safe captures are safe moves where a pawn is captured
        safe_captures = [move for move in safe_moves if move.pos in [opp_pawn.pos for opp_pawn in opp_pawns]]

        if len(winning_moves) > 0:
            return winning_moves[0]
        elif king.pos in [opp_move.pos for opp_move in opp_moves]:
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


class CarefulSimpleAgent:
    '''
    Same as above - but cares about it's own pawns!

    Careful Simple agent objectives (in order of priority).
    1) Attempts to move king to enemy home or capture enemy king
    2) If own king is attackable: move king to random safe square
    3) Attempts to capture an enemy pawn without it being attackable
    4) If own pawn is attackable: move pawn to random safe square
    5) Attempts to move a random piece without it being attackable
    6) Attempts to move a random piece
    '''

    def __init__(self, seed):
        np.random.seed(seed)

    def get_action(self, state):

        # The agent is player 2
        all_moves = state.get_valid_moves(state.player2)
        opp_moves = state.get_valid_moves(state.player1)

        # Agent king, opponent king, and opponent pawn positions
        king = state.player2.king  # [r,c]
        pawns = state.player2.pawns  # [[r,c]]
        opp_king = state.player1.king  # [r,c]
        opp_pawns = state.player1.pawns  # [[r,c]]

        # Winning moves
        winning_moves = [move for move in all_moves if move.isKing and move.pos == [0, 2]
                         or move.pos == opp_king.pos]

        # Safe moves are moves which end up on a square not attackable by an opponents piece
        safe_moves = [move for move in all_moves if move.pos not in [opp_move.pos for opp_move in opp_moves]]

        # Safe retreats are safe moves where our pawn was under attack
        threatened_pawn_positions = [opp_move.pos for opp_move in opp_moves if opp_move.pos in [pawn.pos for pawn in pawns]]
        threatened_pawn_ids = [pawn.id for pawn in pawns if pawn.pos in threatened_pawn_positions]
        safe_retreats = [move for move in safe_moves if move.i in threatened_pawn_ids]

        # Safe captures are safe moves where a pawn is captured
        safe_captures = [move for move in safe_moves if move.pos in [opp_pawn.pos for opp_pawn in opp_pawns]]

        if len(winning_moves) > 0:
            return winning_moves[0]
        elif king.pos in [opp_move.pos for opp_move in opp_moves]:
            king_moves = [move for move in safe_moves if move.isKing]
            if len(king_moves) > 0:
                return np.random.choice(king_moves)

        if len(safe_captures) > 0:
            return np.random.choice(safe_captures)
        elif len(safe_retreats) > 0:
            return np.random.choice(safe_retreats)
        elif len(safe_moves) > 0:
            return np.random.choice(safe_moves)
        else:
            return np.random.choice(all_moves)
