from onitama.rl import OnitamaEnv
from onitama.game import get_move
import numpy as np
import unittest


class EnvTest(unittest.TestCase):
    def test_error(self):
        env = OnitamaEnv()
        obs = env.reset()

    def test_move_to_mask(self):
        env = OnitamaEnv()
        ac = np.zeros((5, 5, 50))
        # ac has to be a piece
        # note all pieces in orig positions, for p1 it's [4, *], king at [4, 2]
        ac[4, 2, 29] = 1
        move = env.actionToMove([i[0] for i in np.where(ac)])
        mask = env.moveToMask(move, env.game.player1)
        assert np.all([a[0] == m for a, m in zip(np.where(ac), mask)]), "Ac : {}\nMask : {}".format(np.where(ac), mask)

    def test_move_to_mask_pawn(self):
        env = OnitamaEnv()
        ac = np.zeros((5, 5, 50))
        # ac has to be a piece
        # note all pieces in orig positions, for p1 it's [4, *], king at [4, 2]
        ac[4, 1, 29] = 1
        move = env.actionToMove([i[0] for i in np.where(ac)])
        mask = env.moveToMask(move, env.game.player1)
        assert np.all([a[0] == m for a, m in zip(np.where(ac), mask)]), "Ac : {}\nMask : {}".format(np.where(ac), mask)

    def test_mask_to_move(self):
        env = OnitamaEnv()
        # note all pieces in orig positions, for p1 it's [4, *], king at [4, 2]
        move = get_move([1, 1], True, 0, -1)
        mask = env.moveToMask(move, env.game.player1)
        ac = np.zeros((5, 5, 50))
        ac[mask] = 1
        move2 = env.actionToMove([i[0] for i in np.where(ac)])
        assert move.pos == move2.pos, "pos Orig : {}\nNew : {}".format(move, move2)
        assert move.isKing == move2.isKing, "isKing Orig : {}\nNew : {}".format(move, move2)
        assert move.i == move2.i, "i Orig : {}\nNew : {}".format(move, move2)
        assert move.cardId == move2.cardId, "CardID Orig : {}\nNew : {}".format(move, move2)

    def test_mask_to_move_pawn(self):
        env = OnitamaEnv()
        move = get_move([1, 1], False, 0, 1)
        mask = env.moveToMask(move, env.game.player1)
        ac = np.zeros((5, 5, 50))
        ac[mask] = 1
        move2 = env.actionToMove([i[0] for i in np.where(ac)])
        assert move.pos == move2.pos, "pos Orig : {}\nNew : {}".format(move, move2)
        assert move.isKing == move2.isKing, "isKing Orig : {}\nNew : {}".format(move, move2)
        assert move.i == move2.i, "i Orig : {}\nNew : {}".format(move, move2)
        assert move.cardId == move2.cardId, "CardID Orig : {}\nNew : {}".format(move, move2)

    def test_valid_moves(self):
        env = OnitamaEnv()
        env.reset()
        valid_moves = env.game.get_valid_moves(env.game.player1)
        env.game.step(valid_moves[0])
        for move in env.game.get_valid_moves(env.game.player1):
            assert env.game.check_valid_move(move), "Found incorrect valid move {}".format(move)


if __name__ == "__main__":
    unittest.main()
