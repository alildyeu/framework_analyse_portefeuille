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

    def compute_covariance(self, fund_excess_returns, benchmark_excess_returns):
        return np.cov(fund_excess_returns[1:], benchmark_excess_returns[1:])[0, 1]
    