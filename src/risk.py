from src.bench import Benchmark
from src.fund import Fund
import numpy as np

class Risk():
    def __init__(self, fund, bench):
        self.fund: Fund = fund
        self.bench: Benchmark = bench

    def compute_beta(self, returns, benchmark_returns, risk_free_rate):
        fund_excess_returns = self.fund.compute_excess_returns(returns, risk_free_rate)
        benchmark_excess_returns = self.bench.compute_excess_returns(benchmark_returns, risk_free_rate)
        covariance = self.compute_covariance(fund_excess_returns, benchmark_excess_returns)
        return covariance / np.var(benchmark_excess_returns[1:])
    
    def compute_alpha(self, returns, benchmark_returns, risk_free_rate):
        beta = self.compute_beta(returns, benchmark_returns, risk_free_rate)
        fund_annualized_return = self.fund.compute_annualized_returns(returns)
        benchmark_annualized_return = self.bench.compute_annualized_returns(benchmark_returns)
        return fund_annualized_return - (risk_free_rate.mean() + beta * (benchmark_annualized_return - risk_free_rate.mean()))

    def compute_covariance(self, fund_excess_returns, benchmark_excess_returns):
        return np.cov(fund_excess_returns[1:], benchmark_excess_returns[1:])[0, 1]
    