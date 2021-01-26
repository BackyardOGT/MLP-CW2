from onitama.rl import OnitamaEnv

if __name__ == "__main__":
    env = OnitamaEnv()
    obs = env.reset()
    print(obs)