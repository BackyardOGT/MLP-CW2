from onitama.rl import OnitamaEnv
import numpy as np


if __name__ == "__main__":
    env = OnitamaEnv()
    obs = env.reset()
    print(np.shape(obs))