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

    def compute_sharpe_ratio(self, returns, risk_free_rate):
        excess_returns = self.compute_excess_returns(returns, risk_free_rate)
        return (excess_returns.mean() / self.compute_volatility(returns)) * np.sqrt(252)

    def compute_sortino_ratio(self, returns, risk_free_rate):
        excess_returns = self.compute_excess_returns(returns, risk_free_rate)
        return (excess_returns.mean() / self.compute_downside_volatility(returns)) * np.sqrt(252)


