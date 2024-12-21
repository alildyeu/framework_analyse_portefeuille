import numpy as np

from src.datafile import DataFile
from src.asset import FinancialAsset

class Fund(FinancialAsset):
    def __init__(self, name, all_funds):
        super().__init__(name)
        self.load_data(
            f'data/loaded/funds/{name}.xlsx',
            lambda: DataFile(**all_funds[name]).data
        )
        self.compute_daily_returns('VL')

    def compute_volatility(self, returns):
        return returns.std() * np.sqrt(252)

    def compute_downside_volatility(self, returns):
        negative_returns = returns[returns < 0]
        return negative_returns.std() * np.sqrt(252)

    def compute_excess_returns(self, returns, risk_free_rate):
        return returns - risk_free_rate

    def compute_sharpe_ratio(self, returns, risk_free_rate):
        excess_returns = self.compute_excess_returns(returns, risk_free_rate)
        return (excess_returns.mean() / self.compute_volatility(returns)) * np.sqrt(252)

    def compute_sortino_ratio(self, returns, risk_free_rate):
        excess_returns = self.compute_excess_returns(returns, risk_free_rate)
        return (excess_returns.mean() / self.compute_downside_volatility(returns)) * np.sqrt(252)
    
    def compute_beta(self, returns, benchmark_returns, risk_free_rate):
        fund_excess_returns = self.compute_excess_returns(returns, risk_free_rate)
        benchmark_excess_returns = self.compute_excess_returns(benchmark_returns, risk_free_rate)
        covariance = self.compute_covariance(fund_excess_returns, benchmark_excess_returns)
        return covariance / np.var(benchmark_excess_returns[1:])
    
    def compute_alpha(self, returns, benchmark_returns, risk_free_rate):
        beta = self.compute_beta(returns, benchmark_returns, risk_free_rate)
        fund_annualized_return = self.compute_annualized_returns(returns)
        benchmark_annualized_return = self.compute_annualized_returns(benchmark_returns)
        return fund_annualized_return - (risk_free_rate.mean() + beta * (benchmark_annualized_return - risk_free_rate.mean()))

    def compute_covariance(self, fund_excess_returns, benchmark_excess_returns):
        return np.cov(fund_excess_returns[1:], benchmark_excess_returns[1:])[0, 1]
    
    def compute_annualized_returns(self, returns):
        return (1 + returns.mean()) ** 252 - 1