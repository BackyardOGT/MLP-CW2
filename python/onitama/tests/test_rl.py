from onitama.rl import MaskedCNNPolicy, OnitamaEnv, RandomAgent
import tensorflow as tf
import gym
from stable_baselines.common import tf_util
from stable_baselines.deepq import DQN
import numpy as np
import unittest


class RLTest(unittest.TestCase):
    def test_error(self):
        env = OnitamaEnv(RandomAgent)
        observation_space = env.observation_space
        action_space = env.action_space
        n_env = 1
        n_steps = 100
        graph = tf.Graph()
        with graph.as_default():
            sess = tf_util.make_session(1, graph)
            policy = MaskedCNNPolicy(sess, observation_space, action_space, n_env, n_steps, 1)
            tf_util.initialize(sess)
            obs = np.zeros(observation_space.shape)
            actions, qs, _ = policy.step([obs])

    def test_masked_outputs(self):
        env = OnitamaEnv(RandomAgent)
        observation_space = env.observation_space
        action_space = env.action_space
        n_env = 1
        n_steps = 100
        graph = tf.Graph()
        with graph.as_default():
            sess = tf_util.make_session(1, graph)
            policy = MaskedCNNPolicy(sess, observation_space, action_space, n_env, n_steps, 1)
            tf_util.initialize(sess)
            obs = np.ones((5, 5, 9))
            mask = np.ones(5 * 5 * 25 * 2) * -10e9
            allowed = 1
            mask[allowed] = 1
            mask = mask.reshape((5, 5, 50))
            obs = np.concatenate([obs, mask], -1)
            assert(np.where(policy.proba_step([obs]))[1][0] == allowed), "Got: {} expected: {}".format(np.where(policy.proba_step([obs])), allowed)
            assert(policy.step([obs])[0] == allowed), "Got: {} expected: {}".format(policy.step([obs]), allowed)

    def test_with_env(self):
        env = OnitamaEnv()
        dqn = DQN(MaskedCNNPolicy, env, learning_starts=10)
        dqn.learn(total_timesteps=100)


if __name__ == "__main__":
    unittest.main()