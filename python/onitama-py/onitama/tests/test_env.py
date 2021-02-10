from onitama.rl import OnitamaEnv, actionToMove, moveToMask
from onitama.game import Move, get_move
import numpy as np
import unittest


class EnvTest(unittest.TestCase):
    seed = 123124

    def testMoveForwardsPlayer2(self):
        # Test move_forwards
        ##Move player 2 pawn (id=0) forward 2 squares
        ##Reward should = 0.2 (2 moves * 0.1)
        env = OnitamaEnv(self.seed, player=2)

        moveJson = {"pos": [2, 0],
                    "name": "pawn",
                    "i": 0,
                    "id": 0}

        move = Move(moveJson)

        env.game.player2.step(move, None)
        self.assertEqual(env.get_reward(), 0.02)

    def testPlayer2TakePawn(self):
        # Test Player1 taking Player2s pawn at location [0,0]
        # NOTE: This test will only pass if the move is NOT checked to be a valid move
        env = OnitamaEnv(self.seed, player=1)
        moveJson = {"pos": [0, 0],
                    "name": "pawn",
                    "i": 0,
                    "id": 0}
        move = Move(moveJson)

        env.game.step(move)
        
        self.assertEqual(env.get_reward(), 0.1+4*0.01)

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
        valid_moves = env.game.get_valid_moves(env.game.player1)
        env.game.step(valid_moves[0])
        env.game.stepBot()
        for move in env.game.get_valid_moves(env.game.player1):
            assert env.game.check_valid_move(move), "Found incorrect valid move {}".format(move)


if __name__ == "__main__":
    np.random.seed(111)
    unittest.main()
