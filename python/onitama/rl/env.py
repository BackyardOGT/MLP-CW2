from onitama.game import VsBot, State, get_move
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
    def __init__(self, agent_type=RandomAgent, player=1):
        super(OnitamaEnv, self).__init__()
        self.game = VsBot(agent_type())
        self.observation_space = gym.spaces.Box(np.zeros((5, 5, 59)), np.ones((5, 5, 59)))
        self.action_space =  gym.spaces.Discrete(5 * 5 * 25 * 2)
        self.thisPlayer = player

    def step(self, ac):
        # action is index into 5 x 5 x 50
        move = self.actionToMove(np.unravel_index(ac, (5, 5, 50)))
        self.game.step(move)
        return self.get_obs(), self.get_reward(), self.game.winner > 0, {}

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
        # TODO: test
        mask = np.zeros((5, 5, 50))
        player = self.game.player1 if self.thisPlayer == 1 else self.game.player2
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
        piece_pos = ac_chosen[:2]  # pr of picking a piece at this location
        isKing, i = self.get_piece(piece_pos)
        cardBoard = ac_chosen[2]
        if cardBoard >= 25:
            cardId = 1
            cardBoard -= 25
        else:
            cardId = 0
        pos_i = cardBoard // 5
        pos_j = cardBoard % 5
        move = get_move([pos_i, pos_j], isKing, cardId, i)
        return move

    def moveToMask(self, move, player):
        """
        :return: (a, b, c) tuple the indices of the action for mask = 1
        """
        # TODO: test this equals actionToMove
        # 5 x 5 grid is pr(pickup piece here)
        piecePos = player.king.get() if move.isKing else player.pawns[move.i].get()
        # the next is 5 x 5 spaces x 2 cards
        # card id is 0 or 1
        placePos = move.pos[0] * 5 + move.pos[1] + 25 * move.cardId
        # TODO: reverse of actionToMove
        ind = move.cardId
        return (piecePos[0], piecePos[1], placePos)

