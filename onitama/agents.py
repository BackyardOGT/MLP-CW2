import numpy as np


class RandomAgent:
    def __init__(self):
        np.random.seed(1123)

    def get_action(self, state):
        ac = np.random.choice(state.get_valid_moves(state.player2))
        return ac