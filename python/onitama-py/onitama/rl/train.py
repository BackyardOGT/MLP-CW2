from onitama.rl import OnitamaEnv, MaskedCNNPolicy, SimpleAgent
from stable_baselines.deepq import DQN
from stable_baselines.common.evaluation import evaluate_policy
from stable_baselines.common.callbacks import CheckpointCallback, EvalCallback, CallbackList
import numpy as np
import argparse


def train_rl():
    env = OnitamaEnv(SimpleAgent, verbose=False)
    policy = DQN(MaskedCNNPolicy, env)

    checkpoint_callback = CheckpointCallback(save_freq=1e4, save_path='./logs/',
                                             name_prefix='rl_model')
    eval_callback = EvalCallback(env, best_model_save_path='./logs/',
                             log_path='./logs/', eval_freq=500,
                             deterministic=True, render=False)
    callback = CallbackList([checkpoint_callback, eval_callback])

    policy.learn(1e6, callback=checkpoint_callback)


if __name__ == "__main__":
    train_rl()