from src.bench import Benchmark
from src.fund import Fund
import numpy as np
from scipy.stats import linregress

class Risk():
    def __init__(self, fund, bench):
        self.fund: Fund = fund
        self.bench: Benchmark = bench

    def compute_beta(self, returns, benchmark_returns):
        slope, _, _, _, _ = linregress(benchmark_returns, returns)
        return slope
    
    def compute_alpha(self, returns, benchmark_returns, risk_free_rate):
        excess_fund_returns = returns - risk_free_rate
        excess_benchmark_returns = benchmark_returns - risk_free_rate
        beta = self.compute_beta(returns, benchmark_returns)
        return np.mean(excess_fund_returns) - beta * np.mean(excess_benchmark_returns)

    def compute_relative_max_drawdown(self, returns, benchmark_returns):
        fund_cumulative_returns = self.fund.compute_cumul_returns(returns)['Cumul Returns']
        benchmark_cumulative_returns = self.bench.compute_cumul_returns(benchmark_returns)['Cumul Returns']
        relative_drawdown = fund_cumulative_returns / benchmark_cumulative_returns - 1
        return relative_drawdown.min()

    