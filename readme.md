# Reinforcement Learning Pair Trading

This is a replica of Kim's work on the Reinforcement Pair Trading. The fundamental strategy is to pair trading between trading boundary and Stop-loss boundry. Position shall be opened upon trading bondary and closed at the convergence. An opened position will be forcifully closed for stop-loss boundary or exited beyond trading window.

![Strategy](https://static.hindawi.com/articles/complexity/volume-2019/3582516/figures/3582516.fig.001.jpg)

> Kim, T., & Kim, H. Y. (2019). Optimizing the pairs-trading strategy using deep reinforcement learning with trading and stop-loss boundaries. Complexity, 2019, e3582516. https://doi.org/10.1155/2019/3582516

## Signal

The movement of the spreads are calculate from TLS (Total Least Square) between the pair price with OLS (Ordinary Least Square) as a comparison.

![TLS and OLS](https://miro.medium.com/v2/resize:fit:854/1*illoIj5LRD3NrQ69iV30kw.png)

## Window Size
Kim experimented a series of combination between Formation Window and Trading Window. The most profitable combination is Formation Window 30, Trading Window 15.

| Formation Window | Trading Window |
| -- | -- |
| 30 | 15 |
| 60 | 30 |
| 90 | 45 |
| 120 | 60 |
| 150 | 75 |
| 180 | 90 |

## Action Space
|    | A0 | A1 | A2 | A3 | A4 | A5 |
| -- | -- | -- | -- | -- | -- | -- |
| Trading Boundary | $\pm$ 0.5 | $\pm$ 1.0 | $\pm$ 1.5 | $\pm$ 2.0 | $\pm$2.5 | $\pm$ 3.0 |
| Stop-loss Boundary | $\pm$ 0.5 | $\pm$ 1.0 | $\pm$ 1.5 | $\pm$ 2.0 | $\pm$ 2.5 | $\pm$ 3.0 |

## Observation

Not mentioned, speculate as signal and zoning

## Reward Shaping
The reward is calculated upon a basic unit $W_t$. If portfolio closed when trading signal converge, then 1000 $W_t$, if stop-loss, big punishment for 1000 $W_t$. If the position does not meet the chance to close during the trading window, punishment for 500 $W_t$.

$$
W_t=\left|v_{A, t} \times \frac{S_{A, t^{\prime}}-S_{A, t}}{S_{A, t}}+v_{B, t} \times \frac{S_{B, t^{\prime}}-S_{B, t}}{S_{B, t}}\right| t<t^{\prime}
$$

$S$ stands for the spread, $V$ stands for position volume.

$$
R_t= \begin{cases}1000 \times W_t & \text { if portfolio closed } \\ -1000 \times W_t & \text { if portfolio reaches stop-loss threshold } \\ -500 \times W_t & \text { if portfolio exited }\end{cases}
$$