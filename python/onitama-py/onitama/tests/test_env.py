from onitama.rl import OnitamaEnv, actionToMove, moveToMask
from onitama.game import Move, get_move
import numpy as np
import unittest


class EnvTest(unittest.TestCase):
    seed = 123124

    # def testMoveForwardsPlayer2(self):
    #     # Test move_forwards
    #     ##Move player 2 pawn (id=0) forward 2 squares
    #     ##Reward should = 0.2 (2 moves * 0.1)
    #     env = OnitamaEnv(self.seed, player=2)
    #
    #     moveJson = {"pos": [2, 0],
    #                 "name": "pawn",
    #                 "i": 0,
    #                 "id": 0}
    #
    #     move = Move(moveJson)
    #
    #     env.game.player2.step(move, None)
    #     self.assertEqual(env.get_reward(), 0.02)
    #
    # def testPlayer2TakePawn(self):
    #     # Test Player1 taking Player2s pawn at location [0,0]
    #     # NOTE: This test will only pass if the move is NOT checked to be a valid move
    #     env = OnitamaEnv(self.seed, player=1)
    #     moveJson = {"pos": [0, 0],
    #                 "name": "pawn",
    #                 "i": 0,
    #                 "id": 0}
    #     move = Move(moveJson)
    #
    #     env.game.step(move)
    #
    #     self.assertEqual(env.get_reward(), 0.1+4*0.01)

    def test_error(self):
        env = OnitamaEnv(self.seed)
        obs = env.reset()

    def test_move_to_mask(self):
        env = OnitamaEnv(self.seed)
        ac = np.zeros((5, 5, 50))
        # ac has to be a piece
        # note all pieces in orig positions, for p1 it's [4, *], king at [4, 2]
        ac[4, 2, 29] = 1
        move = actionToMove([i[0] for i in np.where(ac)], env.game, env.thisPlayer, env.mask_shape)
        mask = moveToMask(move, env.game.player1)
        assert np.all([a[0] == m for a, m in zip(np.where(ac), mask)]), "Ac : {}\nMask : {}".format(np.where(ac), mask)

    def test_move_to_mask_pawn(self):
        env = OnitamaEnv(self.seed)
        ac = np.zeros((5, 5, 50))
        # ac has to be a piece
        # note all pieces in orig positions, for p1 it's [4, *], king at [4, 2]
        ac[4, 1, 29] = 1
        move = actionToMove([i[0] for i in np.where(ac)], env.game, env.thisPlayer, env.mask_shape)
        mask = moveToMask(move, env.game.player1)
        assert np.all([a[0] == m for a, m in zip(np.where(ac), mask)]), "Ac : {}\nMask : {}".format(np.where(ac), mask)

    def test_mask_to_move(self):
        env = OnitamaEnv(self.seed)
        # note all pieces in orig positions, for p1 it's [4, *], king at [4, 2]
        move = get_move([1, 1], True, 0, -1)
        mask = moveToMask(move, env.game.player1)
        ac = np.zeros((5, 5, 50))
        ac[mask] = 1
        move2 = actionToMove([i[0] for i in np.where(ac)], env.game, env.thisPlayer, env.mask_shape)
        assert move.pos == move2.pos, "pos Orig : {}\nNew : {}".format(move, move2)
        assert move.isKing == move2.isKing, "isKing Orig : {}\nNew : {}".format(move, move2)
        assert move.i == move2.i, "i Orig : {}\nNew : {}".format(move, move2)
        assert move.cardId == move2.cardId, "CardID Orig : {}\nNew : {}".format(move, move2)

    def test_mask_to_move_pawn(self):
        env = OnitamaEnv(self.seed)
        move = get_move([1, 1], False, 0, 1)
        mask = moveToMask(move, env.game.player1)
        ac = np.zeros((5, 5, 50))
        ac[mask] = 1
        move2 = actionToMove([i[0] for i in np.where(ac)], env.game, env.thisPlayer, env.mask_shape)
        assert move.pos == move2.pos, "pos Orig : {}\nNew : {}".format(move, move2)
        assert move.isKing == move2.isKing, "isKing Orig : {}\nNew : {}".format(move, move2)
        assert move.i == move2.i, "i Orig : {}\nNew : {}".format(move, move2)
        assert move.cardId == move2.cardId, "CardID Orig : {}\nNew : {}".format(move, move2)

    def test_valid_moves(self):
        env = OnitamaEnv(self.seed)
        env.reset()
        valid_moves = env.game.get_valid_moves(env.game.player1, True)
        env.game.step(valid_moves[0])
        env.game.stepBot()
        for move in env.game.get_valid_moves(env.game.player1, True):
            assert env.game.check_valid_move(move), "Found incorrect valid move {}".format(move)


    def test_env_random_agent(self):
        """
        Would expect 50 / 50 of random unmasked actions compared to random agent
        """
        env = OnitamaEnv(self.seed)
        n_episodes = 10
        wins = 0
        for ep in range(n_episodes):
            obs = env.reset()
            mask = obs[:, :, 9:]
            done = False
            while not done:
                valid_acs = [np.ravel_multi_index(ac, (5, 5, 50)) for ac in zip(*np.where(mask))]
                action = env.action_space.sample()
                while not action in valid_acs:
                    action = env.action_space.sample()
                obs, reward, done, info = env.step(action)
                mask = obs[:, :, 9:]
                if done:
                    if info["winner"] == 1:
                        wins += 1
        print("Won {} of {}".format(wins, n_episodes))


if __name__ == "__main__":
    np.random.seed(111)
    unittest.main()
