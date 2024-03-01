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
    
    def _get_rwd(self, W, pos_status):
        if pos_status == "close":
            reward = W * 1000
        elif pos_status == "stoploss":
            reward = W * -1000
        elif pos_status == "exit":
            reward = W * -500
        else:
            reward = 0
        
        # print(reward)
        return reward

    def _take_action(self, cash, action):
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
        position = 0
        pos_status = "unopen" # "open", "close", "stoploss", "exit"
        for i, row in trading_df.iterrows():
            # print(i)
            if position==0 and abs(row['zscore']) > trading_boundary and i<len(trading_df)-1:
                # print("open")
                sa, sb = row['close0'], row['close1']
                pos_status = "open"
                if row['zscore'] > 0:
                    # Long leg0 short leg1
                    holding = [1/row['close0']*(1-self.tc), -1/row['close1']*(1-self.tc)]
                    position = -1
                elif row['zscore'] < 0:
                    # Short leg0 long leg1
                    holding = [-1/row['close0']*(1-self.tc), 1/row['close1']*(1-self.tc)]
                    position = 1
                # print(holding, sa, sb)
            elif position!=0 and abs(row['zscore']) > stoploss_boundary:
                # print("stoploss")
                sat, sbt = row['close0'], row['close1']
                cash -= holding[0]*row['close0']*(1-self.tc) + holding[1]*row['close1']*(1-self.tc)
                position = 0
                pos_status = "stoploss"
                break
            elif position!=0 and row['zscore']*trading_df.iloc[i-1]["zscore"] < 0:
                # print("close")
                sat, sbt = row['close0'], row['close1']
                cash -= holding[0]*row['close0']*(1-self.tc) + holding[1]*row['close1']*(1-self.tc)
                position = 0
                pos_status = "close"
                break
            elif i==len(trading_df)-1:
                # print("exit")   
                sat, sbt = row['close0'], row['close1']
                if pos_status == "open":
                    cash -= holding[0]*row['close0'] + holding[1]*row['close1']
                    pos_status = "exit"

        # print("end trading window")        
        # print(pos_status)
        W = abs(holding[0]*(sat-sa)/sa + holding[1]*(sat-sb)/sb) if pos_status!="unopen" else 0
        return cash, W, pos_status

    def reset(self, seed=None):
        self.trade_step = 0
        self.observation = self._get_obs()
        self.networth = 1
        return self.observation, {}

    def step(self, action):
        self.action = action
        self.signal = self.observation
        self.observation = self._get_obs()
        self.networth, W, pos_status = self._take_action(self.networth, action)
        self.trade_step += 1
        terminated = self.trade_step >= int(len(self.df)/self.tw)
        truncated = False

        return self.observation, self._get_rwd(W, pos_status), terminated, truncated, {}

    def render(self):
        # print(f"signal: {self.signal}, action: {self.action}, reward:{round(self.reward, 3)}, networth: {round(self.networth, 4)}")
        print(f"networth: {round(self.networth, 4)}")