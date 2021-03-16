from onitama.rl import DQNMaskedCNNPolicy, SimpleAgent, RandomAgent
from stable_baselines import DQN, PPO2
from stable_baselines.common.evaluation import evaluate_policy
import numpy as np
import argparse
import onitama
import gym

class EvalCB:
    def __init__(self):
        self.reset()

    def reset(self):
        self.n_wins = 0
        self.n_eps = 0

    def callback(self, locals, globals):
        info = locals["_info"] if not type(locals["_info"]) == list else locals["_info"][0]
        if "winner" in info:
            if info["winner"] == 1:
                self.n_wins += 1
        if locals["done"]:
            self.n_eps += 1

    def print(self):
        print("Won {} / {}".format(self.n_wins, self.n_eps))
        self.reset()


def evaluate_rl(policy, env, n_eps=100):
    eval_cb = EvalCB()
    episode_rewards, episode_lengths = evaluate_policy(policy, env,
                                                       callback=eval_cb.callback,
                                                       return_episode_rewards=True,
                                                       n_eval_episodes=n_eps)
    print("Mean reward: {}".format(np.mean(episode_rewards)))
    print("Std reward: {}".format(np.std(episode_rewards)))
    print("Min reward: {}".format(np.min(episode_rewards)))
    print("Max reward: {}".format(np.max(episode_rewards)))
    print("Mean episode length: {}".format(np.mean(episode_lengths)))
    print("Std episode length: {}".format(np.std(episode_lengths)))
    print("Min episode length: {}".format(np.min(episode_lengths)))
    print("Max episode length: {}".format(np.max(episode_lengths)))
    eval_cb.print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', default=12314, type=int)
    parser.add_argument('--algorithm', default="DQN", type=str)
    parser.add_argument('--model_path', default="logs/best_model.zip", type=str)
    args = parser.parse_args()

    env = gym.make("Onitama-v0", seed=args.seed, agent_type=RandomAgent, verbose=False)
    if args.algorithm == "PPO":
        policy = PPO2.load(args.model_path)
    else:
        policy = DQN.load(args.model_path)

    evaluate_rl(policy, env)