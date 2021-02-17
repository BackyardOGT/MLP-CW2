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
        ac = np.random.choice(state.get_valid_moves(player, self.isPlayer1))
        return ac


class SimpleAgent:
    '''
    Simple agent objectives (in order of priority).
    1) Attempts to move king to enemy home or capture enemy king
    2) If own king is attackable: i) if pawn can be attacked - take the pawn
                                  ii) move king to random safe square
    3) If own pawn is attackable: i) if pawn can be attacked - take the pawn
                                  ii) move pawn to random safe square
    3) Attempts to capture an enemy pawn without it being attackable
    4) Attempts to move a random piece without it being attackable
    5) Attempts to move a random piece
    '''

    def __init__(self, seed, isPlayer1=False):
        assert not isPlayer1, "Simple Agent as player 1 not supported"
        self.isPlayer1 = isPlayer1
        print(seed, type(seed))
        np.random.seed(seed)

    def get_action(self, state):
        agent_player = state.player1 if self.isPlayer1 else state.player2
        opp_player = state.player2 if self.isPlayer1 else state.player1

        all_moves = state.get_valid_moves(agent_player, isPlayer1=self.isPlayer1)
        opp_moves = state.get_valid_moves(opp_player, isPlayer1=not self.isPlayer1)

        # Agent king, opponent king, and opponent pawn positions
        king = agent_player.king  # [r,c]
        pawns = agent_player.pawns  # [[r,c]]
        opp_king = opp_player.king  # [r,c]
        opp_pawns = opp_player.pawns  # [[r,c]]

        # Winning moves
        enemy_shrine_pos = [0, 2] if self.isPlayer1 else [4, 2]
        winning_moves = [move for move in all_moves if move.isKing and move.pos == enemy_shrine_pos
                         or move.pos == opp_king.pos]

        # Safe moves are moves which end up on a square not attackable by an opponents piece
        safe_moves = [move for move in all_moves if move.pos not in [opp_move.pos for opp_move in opp_moves]]

        # Safe retreats are safe moves where our pawn was under attack
        threatened_pawn_positions = [opp_move.pos for opp_move in opp_moves if
                                     opp_move.pos in [pawn.pos for pawn in pawns]]
        threatened_pawn_ids = [pawn.id for pawn in pawns if pawn.pos in threatened_pawn_positions]
        safe_retreats = [move for move in safe_moves if move.i in threatened_pawn_ids]

        # Safe captures are safe moves where a pawn is captured
        safe_captures = [move for move in safe_moves if move.pos in [opp_pawn.pos for opp_pawn in opp_pawns]]

        # 1) Agent tries to win
        if len(winning_moves) > 0:
            #print("winning_move")
            #print(winning_moves)
            return winning_moves[0]

        # 2) King is under attack
        # i) attempts to capture piece
        opp_pawn_ids = [opp_move.i for opp_move in opp_moves if opp_move.pos == king.pos]
        opp_pawn_pos = [opp_pawn.pos for opp_pawn in opp_pawns if opp_pawn.id in opp_pawn_ids]
        if len(opp_pawn_ids) == 1:  # if only 1 attacker only pawn captures
            saving_pawn_captures = [move for move in all_moves if move.pos in opp_pawn_pos and not move.isKing]
            #print("saving_pawn_capture")
            if len(saving_pawn_captures) > 0:
                return np.random.choice(saving_pawn_captures)
        elif len(opp_pawn_ids) > 1: # if >1 attacker only king can capture
            saving_king_captures = [move for move in safe_moves if move.pos in opp_pawn_pos and move.isKing]
            #print("saving_king_capture")
            if len(saving_king_captures) > 0:
                return np.random.choice(saving_king_captures)
        # ii) king retreats to a safe square
        if len(opp_pawn_ids) > 0:
            retreating_king_moves = [move for move in safe_moves if move.isKing]
            if len(retreating_king_moves) > 0:
                #print("retreating_king_move")
                return np.random.choice(retreating_king_moves)

        # 3) One of our pawns is under attack
        opp_piece_ids = [opp_move.i for opp_move in opp_moves if opp_move.pos in [pawn.pos for pawn in pawns]]
        opp_piece_pos = [opp_piece.pos for opp_piece in [*opp_pawns, opp_king] if opp_piece.id in opp_piece_ids]
        # i) attempts to capture piece
        captures = [move for move in all_moves if move.pos in opp_piece_pos]
        if len(captures) > 0:
            #print("capture_by_response")
            return np.random.choice(captures)
        # ii) attempts to retreat threatened piece
        if len(safe_retreats) > 0:
            #print("safe_retreat")
            return np.random.choice(safe_retreats)

        # 4) Captures an undefended enemy piece
        if len(safe_captures) > 0:
            #print("safe_capture")
            return np.random.choice(safe_captures)

        # 5) Chooses a random safe move
        if len(safe_moves) > 0:
            #print("random_safe_move")
            return np.random.choice(safe_moves)

        # 6) Chooses any other move
        else:
            #print("random_move")
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

