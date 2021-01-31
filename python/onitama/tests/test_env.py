from onitama.rl import OnitamaEnv
from onitama.game import *
import numpy as np
import unittest

class RewardTests(unittest.TestCase):

	def testMoveForwardsPlayer2(self):
		#Test move_forwards
    	##Move player 2 pawn (id=0) forward 2 squares
    	##Reward should = 0.2 (2 moves * 0.1)
    	env = OnitamaEnv(player=2)

    	moveJson = {"pos":[2,0],
    			"name":"pawn",
    			"i":0,
    			"id":0}

    	move = Move(moveJson)
    	env.game.player2.step(move,None)
   		self.assertEqual(env.get_reward,0.2)
		



if __name__ == "__main__":
    env = OnitamaEnv()
    obs = env.reset()
    print(np.shape(obs))

    unittest.main()

