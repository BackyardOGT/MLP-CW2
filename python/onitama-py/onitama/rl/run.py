from onitama.rl import OnitamaEnv, MaskedCNNPolicy, SimpleAgent
from stable_baselines.deepq import DQN
from stable_baselines.common.evaluation import evaluate_policy
import numpy as np


class EvalCB:
    def __init__(self):
        self.n_wins = 0
        self.n_eps = 0

    def eval_cb(self, locals, globals):
        if "winner" in locals["_info"]:
            if locals["_info"] == 1:
                self.n_wins += 1
        if locals["done"]:
            self.n_eps += 1

    def print(self):
        print("Won {} / {}".format(self.n_wins, self.n_eps))

def evaluate_rl():
    eval_cb = EvalCB()
    episode_rewards, episode_lengths = evaluate_policy(policy, env, callback=eval_cb.eval_cb, return_episode_rewards=True)
    print("Mean reward: {}".format(np.mean(episode_rewards)))
    print("Std reward: {}".format(np.std(episode_rewards)))
    print("Min reward: {}".format(np.min(episode_rewards)))
    print("Max reward: {}".format(np.max(episode_rewards)))
    print("Mean episode length: {}".format(np.mean(episode_lengths)))
    print("Std episode length: {}".format(np.std(episode_lengths)))
    print("Min episode length: {}".format(np.min(episode_rewards)))
    print("Max episode length: {}".format(np.max(episode_rewards)))
    eval_cb.print()

if __name__ == "__main__":
    env = OnitamaEnv(SimpleAgent, verbose=False)
    policy = DQN(MaskedCNNPolicy, env)
    evaluate_rl()