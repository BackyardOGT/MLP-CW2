import os
from datetime import datetime
from onitama.rl import DQNMaskedCNNPolicy, ACMaskedCNNPolicy, SimpleAgent, RandomAgent
from onitama.rl.callbacks import EvalCB
from stable_baselines import DQN, PPO2
from stable_baselines.common.evaluation import evaluate_policy
from stable_baselines.common.callbacks import CheckpointCallback, EvalCallback, CallbackList
from stable_baselines.bench.monitor import Monitor
import numpy as np
import argparse
import onitama
import gym


def train_rl(seed, isDQN, isRandom):
    agent_type = RandomAgent if isRandom else SimpleAgent
    env = gym.make("Onitama-v0", seed=seed, agent_type=agent_type, verbose=False)
    eval_env = gym.make("Onitama-v0", seed=seed, agent_type=agent_type, verbose=False)
    if isDQN:
        basedir = "./logs/dqn-tb/"
        env, logdir = setup_monitor(basedir, env)
        policy = DQN(DQNMaskedCNNPolicy,
                     env,
                     seed=seed,
                     prioritized_replay=True,
                     verbose=1,
                     tensorboard_log=logdir
                     )

    else:
        basedir = "./logs/ppo-tb/"
        env, logdir = setup_monitor(basedir, env)
        policy = PPO2(ACMaskedCNNPolicy,
                      env,
                      seed=seed,
                      verbose=1,
                      tensorboard_log=logdir
                      )

    checkpoint_callback = CheckpointCallback(save_freq=5e3, save_path=logdir,
                                             name_prefix='rl_model', verbose=2)
    eval_policy_cb = EvalCB(logdir)
    eval_callback = EvalCallback(eval_env, best_model_save_path=logdir,
                                 log_path=logdir, eval_freq=500, n_eval_episodes=20,
                                 deterministic=True, render=False,
                                 evaluate_policy_callback=eval_policy_cb)
    callback = CallbackList([checkpoint_callback, eval_callback])
    policy.learn(int(1e6), callback=callback, log_interval=100 if isDQN else 10)



def setup_monitor(basedir, env):
    logdir = basedir + datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    if not os.path.exists(basedir): os.mkdir(basedir)
    if not os.path.exists(logdir): os.mkdir(logdir)
    env = Monitor(env, logdir + "/logs")
    return env, logdir


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', default=12314, type=int)
    parser.add_argument('--DQN', action="store_true", help="Use DQN")
    parser.add_argument('--random', action="store_true", help="Use random agent")
    args = parser.parse_args()

    train_rl(args.seed, args.DQN, args.random)
