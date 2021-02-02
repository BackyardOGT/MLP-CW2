from onitama.rl import MaskedCNNPolicy, OnitamaEnv, RandomAgent
from onitama.game import get_move
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
            assert (np.where(policy.proba_step([obs]))[1][0] == allowed), "Got: {} expected: {}".format(
                np.where(policy.proba_step([obs])), allowed)
            assert (policy.step([obs])[0] == allowed), "Got: {} expected: {}".format(policy.step([obs]), allowed)

    def test_with_env(self):
        env = OnitamaEnv()
        env.reset()
        dqn = DQN(MaskedCNNPolicy, env, learning_starts=10, exploration_initial_eps=0.0, exploration_final_eps=0.0)
        dqn.learn(total_timesteps=100)

    def test_with_env_learn(self):
        env = OnitamaEnv()
        env.reset()
        dqn = DQN(MaskedCNNPolicy, env, learning_starts=10, exploration_initial_eps=0.0, exploration_final_eps=0.0)
        dqn.learn(total_timesteps=100)

    def test_mask_with_env(self):
        env = OnitamaEnv()
        env.reset()
        valid_moves = env.game.get_valid_moves(env.game.player1)
        mask = env.get_mask()
        self.valid_mask(env, mask)

    def test_mask_with_env_step(self):
        env = OnitamaEnv()
        env.reset()
        valid_moves = env.game.get_valid_moves(env.game.player1)
        env.game.step(valid_moves[0])
        valid_moves = env.game.get_valid_moves(env.game.player1)
        mask = env.get_mask()
        self.valid_mask(env, mask)

    def valid_mask(self, env, mask):
        mask_pos = [(a, b, c) for (a, b, c) in zip(*np.where(mask))]
        valid_moves = env.game.get_valid_moves(env.game.player1)
        for mp in mask_pos:
            move = env.actionToMove(mp)
            assert move in valid_moves, "Move: {}\nValid moves: {}".format(move, valid_moves)

    def test_policy_ac_with_env(self):
        env = OnitamaEnv()
        dqn = DQN(MaskedCNNPolicy, env)
        obs = env.reset()
        ac, _ = dqn.predict(obs, deterministic=False)
        env.step(ac)

    def test_policy_ac_with_env_step(self):
        env = OnitamaEnv()
        self.dqn = DQN(MaskedCNNPolicy, env)
        dqn = self.dqn
        obs = env.reset()
        with dqn.sess:
            for _ in range(100):
                # mask ok?
                mask = obs[:, :, 9:]
                env_mask = env.get_mask()
                assert len(env.game.get_valid_moves(env.game.player1)) > 0, "No valid moves p1"
                assert not np.array_equal(env_mask, np.zeros_like(env_mask)), "Env mask is zeros"
                assert not np.array_equal(mask, np.zeros_like(mask)), "Obs mask is zeros"
                assert np.array_equal(mask,
                                      env_mask), "Wrong mask, differences\nObs mask {}\nEnv mask {}\nInds: {}".format(
                    mask[np.where(mask != env_mask)], env_mask[np.where(mask != env_mask)], np.where(mask != env_mask))
                ac = dqn.act([obs])
                ac_unravel = np.unravel_index(ac, (5, 5, 50))
                # should this have been masked?
                assert mask[ac_unravel], "This action should be masked"
                self.valid_mask(env, mask)

                obs, _, done, _ = env.step(ac)
                if done:
                    obs = env.reset()

    def test_policy_proba_with_env_step(self):
        env = OnitamaEnv()
        dqn = DQN(MaskedCNNPolicy, env, learning_starts=10)
        env.reset()
        valid_moves = env.game.get_valid_moves(env.game.player1)
        env.game.step(valid_moves[0])
        obs = env.get_obs()
        # mask ok?
        mask = obs[:, :, 9:]
        assert np.array_equal(mask, env.get_mask()), "Wrong mask"
        for ac_flat in np.where(dqn.action_probability(obs))[0]:
            ac = np.unravel_index(ac_flat, (5, 5, 50))
            # should this have been masked?
            assert mask[ac], "This action should be masked"
            move = env.actionToMove(ac)
            valid_moves = env.game.get_valid_moves(env.game.player1)
            # is it valid
            assert move in valid_moves, "Move: {}\nValid moves: {}".format(move, valid_moves)


if __name__ == "__main__":
    np.random.seed(111)
    tf.random.set_random_seed(111)
    unittest.main()
