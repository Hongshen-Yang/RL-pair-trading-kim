import gymnasium as gym
import numpy as np
import pandas as pd

class RL_Kim_TradeEnv(gym.Env):
    def __init__(self, df, tc=0.002, cash=1.0):

        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, dtype=np.float64)
        self.action_space = gym.spaces.Discrete(6) # {0: "short leg0 long leg1", 1: "close positions", 2: "long leg0 short leg1"}

        self.cash, self.networth = cash, cash
        self.df = df
        self.holdings = [0, 0]

    def _get_obs(self):
        obs = np.array([0])
        return obs
    
    def _get_reward(self, prev_networth):
        reward = 0
        return reward

    def _take_action(self):
        pass

    def reset(self, seed=None):
        self.position = 1
        self.trade_step = 15
        self.observation = self._get_obs()
        return self.observation, {}

    def step(self, action):
        self.action = action
        self.signal = self.observation
        prev_networth = self.networth
        self._take_action()
        self.trade_step += 1
        self.observation = self._get_obs()
        terminated = self.trade_step >= len(self.df)
        truncated = False
        self.reward = self._get_reward(prev_networth)

        return self.observation, self.reward, terminated, truncated, {}

    def render(self):
        print(f"signal: {self.signal}, action: {self.action}, reward:{round(self.reward, 3)}, networth: {round(self.networth, 4)}")

    def close(self):
        print("Finished")
        print(f"networth: {self.networth}")