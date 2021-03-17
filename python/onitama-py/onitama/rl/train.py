from onitama.rl import DQNMaskedCNNPolicy, ACMaskedCNNPolicy, SimpleAgent, RandomAgent
from onitama.rl.callbacks import EvalCB
from stable_baselines import DQN, PPO2
from stable_baselines.common.evaluation import evaluate_policy
from stable_baselines.common.callbacks import CheckpointCallback, EvalCallback, CallbackList
import numpy as np
import argparse
import onitama
import gym

def train_rl(seed, algorithm):
    agent_type = RandomAgent
    env = gym.make("Onitama-v0", seed=seed, agent_type=agent_type, verbose=False)
    eval_env = gym.make("Onitama-v0", seed=seed, agent_type=agent_type, verbose=False)
    if algorithm == "PPO":
        logdir = "./logs/ppo-tb/"
        policy = PPO2(ACMaskedCNNPolicy,
                      env,
                      seed=seed,
                      verbose=1,
                      tensorboard_log=logdir
                      )

    else:
        logdir = "./logs/dqn-tb/"
        policy = DQN(DQNMaskedCNNPolicy,
                     env,
                     seed=seed,
                     prioritized_replay=True,
                     verbose=1,
                     tensorboard_log=logdir
                     )

    checkpoint_callback = CheckpointCallback(save_freq=5e3, save_path='./logs/',
                                             name_prefix='rl_model', verbose=2)
    eval_policy_cb = EvalCB(logdir)
    eval_callback = EvalCallback(eval_env, best_model_save_path='./logs/',
                             log_path='./logs/', eval_freq=500, n_eval_episodes=20,
                             deterministic=True, render=False,
                                 evaluate_policy_callback=eval_policy_cb)
    callback = CallbackList([checkpoint_callback, eval_callback])
    policy.learn(int(1e6), callback=callback)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', default=3141, type=int)
    parser.add_argument('--algorithm', default="DQN", type=str)
    args = parser.parse_args()

    train_rl(args.seed, args.algorithm)
