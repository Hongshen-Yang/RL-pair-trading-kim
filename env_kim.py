import gymnasium as gym
import numpy as np
import pandas as pd

class RL_Kim_TradeEnv(gym.Env):
    def __init__(self, df, tc=0.002, cash=1.0, tw=15):
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, dtype=np.float64)
        self.action_space = gym.spaces.Discrete(6) # {0: "short leg0 long leg1", 1: "close positions", 2: "long leg0 short leg1"}

        self.df = df

        self.tc = tc
        self.tw = tw
        self.cash, self.networth = cash, cash
        self.trade_step = 0

        self.networth = 1

    def _get_obs(self):
        obs = np.array([self.df.iloc[self.trade_step*self.tw]['zscore']])
        return obs
    
    def _get_rwd(self):
        self.reward = 0
        return self.reward

    def _take_action(self, action):
        if action == 0:
            trading_boundary = 0.5
            stoploss_boundary = 2.5
        elif action == 1:
            trading_boundary = 1.0
            stoploss_boundary = 3.0 
        elif action == 2:
            trading_boundary = 1.5
            stoploss_boundary = 3.5
        elif action == 3:
            trading_boundary = 2.0
            stoploss_boundary = 4.0
        elif action == 4:
            trading_boundary = 2.5
            stoploss_boundary = 4.5
        elif action == 5:
            trading_boundary = 3.0
            stoploss_boundary = 5.0
        
        trading_df = self.df.iloc[self.trade_step*self.tw:self.trade_step*self.tw+self.tw].reset_index()

        holding = [0, 0]
        cash = 0
        position = 0
        for i, row in trading_df.iterrows():
            if position==0 and abs(row['zscore']) > trading_boundary:
                # print("opened pos")
                if row['zscore'] > 0:
                    # Long leg0 short leg1
                    holding = [1/row['close0']*(1-self.tc), -1/row['close1']*(1-self.tc)]
                    position = -1
                elif row['zscore'] < 0:
                    # Short leg0 long leg1
                    holding = [-1/row['close0']*(1-self.tc), 1/row['close1']*(1-self.tc)]
                    position = 1
                position = 1
            elif position!=0 and abs(row['zscore']) > stoploss_boundary:
                # print("stop pos")
                print(holding)
                cash = holding[0]*row['close0']*(1-self.tc) + holding[1]*row['close1']*(1-self.tc)
                position = 0
                break
            elif position!=0 and row['zscore']*trading_df.iloc[i-1]["zscore"] < 0:
                # print("closed pos")
                print(holding)
                cash = holding[0]*row['close0']*(1-self.tc) + holding[1]*row['close1']*(1-self.tc)
                position = 0
                break
            if position==0 and i==len(trading_df)-1:
                # print("exit pos")   
                cash = holding[0]*row['close0'] + holding[1]*row['close1']
        
        return cash

    def reset(self, seed=None):
        self.trade_step = 0
        self.observation = self._get_obs()
        self.networth = 1
        return self.observation, {}

    def step(self, action):
        self.action = action
        self.signal = self.observation
        self.observation = self._get_obs()
        self.networth = self._take_action(action)
        self.trade_step += 1
        terminated = self.trade_step >= int(len(self.df)/self.tw)
        truncated = False

        return self.observation, self._get_rwd(), terminated, truncated, {}

    def render(self):
        # print(f"signal: {self.signal}, action: {self.action}, reward:{round(self.reward, 3)}, networth: {round(self.networth, 4)}")
        print(f"networth: {round(self.networth, 4)}")

    def close(self):
        print("Finished")
        print(f"networth: {self.networth}")