from onitama.game import VsBot, State
from onitama.rl import RandomAgent
import gym
import numpy as np


def get_board_state(player_dict):
    pawns = np.zeros((5, 5))
    king = np.zeros((5, 5))
    for (i, j) in player_dict["pawns"]:
        pawns[i][j] = 1
    k, l = player_dict["king"]
    king[k][l] = 1
    return pawns, king


class OnitamaEnv(gym.Env):
    """
    Observations:
        (5 x 5 x 6) cards - 2 current and 1 next for each player
        (5 x 5 x 4) board - kings and pawns for each player
    Actions:
        (5 x 5 x 25) board spaces x number of moves - each filter is the probability of picking a piece
        from this board location, filter dimesnions are 25 (5 x 5) possible moves to move to. S
        oftmax over this and zero out invalid moves.
    """
    def __init__(self, agent_type=RandomAgent):
        super(OnitamaEnv, self).__init__()
        self.game = VsBot(agent_type())

    def step(self, ac):
        pass

    def reset(self):
        self.game.reset()
        return self.get_obs()

    def render(self, mode='human'):
        pass

    def get_obs(self):
        # see game class for API
        game_state = State(self.game.get())
        obs = []
        # cards
        for card in game_state.player1_dict["cards"]:
            obs.append(card)
        for card in game_state.player2_dict["cards"]:
            obs.append(card)
        obs.append(game_state.spare_card)
        # board
        pawns_p1, king_p1 = get_board_state(game_state.player1_dict)
        obs.append([pawns_p1, king_p1])
        pawns_p2, king_p2 = get_board_state(game_state.player2_dict)
        obs.append([pawns_p2, king_p2])
        return np.hstack(obs)