from onitama.rl import MaskedCNNPolicy, get_mask, OnitamaEnv, SimpleAgent, actionToMove
from onitama.rl.env import _get_obs
from stable_baselines.deepq import DQN

import numpy as np


class RLAgent:
    """
    Wraps policy to work with backend API calls
    """
    def __init__(self, thisPlayer=2):
        """
        Assumes player 2 as this is normal
        """
        self.thisPlayer = thisPlayer

        env = OnitamaEnv(SimpleAgent, verbose=False)
        self.policy = DQN(MaskedCNNPolicy, env)
        np.random.seed(1123)

    def get_action(self, state):
        obs = np.concatenate([_get_obs(state), get_mask(state, self.thisPlayer)], -1)
        ac, _ = self.policy.predict([obs])
        ac = np.squeeze(ac)
        # action is index into 5 x 5 x 50
        ac = np.unravel_index(ac, (5, 5, 50))
        move = actionToMove(ac, state, self.thisPlayer)
        return move
