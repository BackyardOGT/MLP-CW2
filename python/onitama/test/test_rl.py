from onitama.rl import MaskedCNNPolicy, OnitamaEnv, RandomAgent
import tensorflow as tf
import gym
from stable_baselines.common import tf_util
import numpy as np

if __name__ == "__main__":
    env = OnitamaEnv(RandomAgent)
    observation_space = env.observation_space
    action_space = env.action_space
    n_env = 1
    n_steps = 100
    n_batch = 64

    graph = tf.Graph()
    with graph.as_default():
        sess = tf_util.make_session(1, graph)
        policy = MaskedCNNPolicy(sess, observation_space, action_space, n_env, n_steps, n_batch)
        obs = np.zeros(observation_space.shape)
        print("Obs", np.shape(obs))
        policy.step(obs)