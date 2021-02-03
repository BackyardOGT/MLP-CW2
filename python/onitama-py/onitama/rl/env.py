from onitama.game import PvBot, State, get_move
from onitama.rl import RandomAgent
import gym
import numpy as np


def get_board_state(player_dict):
    pawns = np.zeros((5, 5, 1))
    king = np.zeros((5, 5, 1))
    for i, j in player_dict["pawns"]:
        pawns[i][j] = 1
    k, l = player_dict["king"]
    king[k][l] = 1
    return pawns, king


class OnitamaEnv(gym.Env):
    """
    Defaults to player 1
    See README for obs and ac space definitions
    """
    def __init__(self, agent_type=RandomAgent, player=1, verbose=True):
        super(OnitamaEnv, self).__init__()
        self.game = PvBot(agent_type(), verbose=verbose)
        self.observation_space = gym.spaces.Box(np.zeros((5, 5, 59)), np.ones((5, 5, 59)))
        self.action_space =  gym.spaces.Discrete(5 * 5 * 25 * 2)
        self.thisPlayer = player

    def step(self, ac):
        ac = np.squeeze(ac)
        # action is index into 5 x 5 x 50
        ac = np.unravel_index(ac, (5, 5, 50))
        move = self.actionToMove(ac)
        self.game.step(move)
        self.game.stepBot()
        info = {} if self.game.winner == 0 else {"winner": self.game.winner}
        return self.get_obs(), self.get_reward(), self.game.winner > 0, info

    def reset(self):
        self.game.reset()
        return self.get_obs()

    def render(self, mode='human'):
        pass

    def get_obs(self):
        """
        Observation and mask for valid actions
        :return:
        """
        return np.concatenate([self._get_obs(), self.get_mask()], -1)

    def _get_obs(self):
        """
        Returns (5, 5, 9) see above for observation format
        """
        # see game class for API
        game_state = State(self.game.get())
        obs = []
        # cards
        obs.append(np.stack(game_state.player1_dict["cards"], -1))
        obs.append(np.stack(game_state.player2_dict["cards"], -1))
        obs.append(np.expand_dims(game_state.spare_card, -1))
        # board
        pawns_p1, king_p1 = get_board_state(game_state.player1_dict)
        obs.append(pawns_p1)
        obs.append(king_p1)
        pawns_p2, king_p2 = get_board_state(game_state.player2_dict)
        obs.append(pawns_p2)
        obs.append(king_p2)
        return np.concatenate(obs, -1)

    def get_mask(self):
        """
        (5 x 5 x 50) (same shape as agent output)
        Returns the mask over valid moves
        Binary tensor.
        """
        mask = np.zeros((5, 5, 50))
        player = self.game.player1 if self.thisPlayer == 1 else self.game.player2
        assert len(self.game.get_valid_moves(player)) > 0, "No valid moves for masking"
        for move in self.game.get_valid_moves(player):
            ac = self.moveToMask(move, player)
            mask[ac] = 1
        return mask

    def get_piece(self, piece_pos):
        """
        :return: isKing, i
        """
        if self.thisPlayer == 1:
            return self._get_piece(piece_pos, self.game.player1)
        else:
            return self._get_piece(piece_pos, self.game.player2)

    def _get_piece(self, piece_pos, player):
        if np.array_equal(piece_pos, player.king.get()):
            return True, -1
        for i, pawn in enumerate(player.pawns):
            if np.array_equal(piece_pos, pawn.get()):
                return False, i

    def get_reward(self):
        # TODO
        # can get game state by eg.
        # self.game.player1
        move_forwards = 0
        reward_win = 0

        state = State(self.game.get())
        reward_win = state.winner == self.thisPlayer

        player = self.game.player1  if self.thisPlayer == 1 else self.game.player2 

        #Get number of rows moved
        rows_moved = player.last_move.pos[0] - player.last_pos[0]

        row_orientation = 1 if self.thisPlayer == 2 else -1

        move_forwards = max(0,rows_moved * row_orientation)

        reward_weights = {
            "move_forwards": 0.1,
            "win": 1.0,
        }
        reward_dict = {
            "move_forwards": move_forwards,
            "win": reward_win
        }
        reward = 0
        for k, r in reward_dict.items():
            reward += r * reward_weights[k]
        return reward

    def actionToMove(self, ac_chosen):
        """
        :param ac_chosen: reshaped action (piece pos i, piece pos j, board x card data)
        :return: Move() object
        """
        ac_ravel = np.ravel_multi_index(ac_chosen, (5, 5, 50))
        (piece_pos_i, piece_pos_j, pos_i, pos_j, card_id) = np.unravel_index(ac_ravel, (5, 5, 5, 5, 2))
        piece = self.get_piece([piece_pos_i, piece_pos_j])
        if not piece:
            return None
        isKing, i = piece
        move = get_move([pos_i, pos_j], isKing, card_id, i)
        return move

    def moveToMask(self, move, player):
        """
        :return: (a, b, c) tuple the indices of the action for mask = 1
        """
        # 5 x 5 grid is pr(pickup piece here)
        piecePos = player.king.get() if move.isKing else player.pawns[move.i].get()
        # the next is 5 x 5 spaces x 2 cards
        # card id is 0 or 1
        placePos = np.ravel_multi_index((move.pos[0], move.pos[1], move.cardId), (5, 5, 2))
        move_ravel = np.ravel_multi_index((piecePos[0], piecePos[1], move.pos[0], move.pos[1], move.cardId), (5, 5, 5, 5, 2))
        mask = np.unravel_index(move_ravel, (5, 5, 50))
        return mask

