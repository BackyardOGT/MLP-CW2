from onitama.rl import OnitamaEnv, OnitamaSelfPlayEnv, DQNMaskedCNNPolicy, ACMaskedCNNPolicy, SimpleAgent, RandomAgent
from onitama.rl.eval import EvalCB
from stable_baselines import DQN
from stable_baselines import PPO2
from stable_baselines.common.callbacks import CheckpointCallback, EvalCallback, CallbackList
import argparse


def train_rl(seed, policy):
    eval_env = OnitamaEnv(seed, SimpleAgent, verbose=False)

    checkpoint_callback = CheckpointCallback(save_freq=1e4, save_path='./logs/',
                                             name_prefix='rl_model', verbose=2)
    eval_policy_cb = EvalCB()
    eval_callback = EvalCallback(eval_env, best_model_save_path='./logs/',
                             log_path='./logs/', eval_freq=int(1e3),
                             deterministic=True, render=False,
                                 evaluate_policy_callback=eval_policy_cb)
    callback = CallbackList([checkpoint_callback, eval_callback])
    policy.learn(int(1e6), callback=callback)


def getPolicy(algorithm, seed):
    env = OnitamaSelfPlayEnv(seed, verbose=False)

    if algorithm == "PPO":
        policy = PPO2(ACMaskedCNNPolicy,
                     env,
                     seed=seed,
                     verbose=1,
                     )

    else:
        policy = DQN(DQNMaskedCNNPolicy,
                     env,
                     seed=seed,
                     prioritized_replay=True,
                     buffer_size=5000,
                     verbose=1,
                     )
    env.setSelfPlayModel(policy)
    return policy


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', default=12314, type=int)
    parser.add_argument('--algorithm', default="PPO", type=str)
    args = parser.parse_args()

    policy = getPolicy(args.algorithm, args.seed)

    train_rl(args.seed, policy)
