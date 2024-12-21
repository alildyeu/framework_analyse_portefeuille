import numpy as np

class Fund():
    def __init__(self, name, vl, region):
        """
        Initialize the Fund object.

        Parameters:
        - name (str): Name of the fund.
        - data (pd.DataFrame): DataFrame containing 'Date' and 'VL' columns.
        """
        self.name = name
        self.vl = vl
        self.region = region
        self.rdments = self.compute_daily_returns()

    def compute_daily_returns(self):
        rdment = self.vl.copy()
        rdment['Returns'] = rdment['VL'].pct_change() * 100
        return rdment[['Date','Returns']]
    
    def compute_cumul_returns(self, daily_returns):
        cumul_returns = daily_returns.copy()
        cumul_returns['Cumul Returns'] = (daily_returns['Returns'] / 100).cumsum() * 100
        cumul_returns['Cumul Returns'] = cumul_returns['Cumul Returns'].apply(lambda x: f"{x:.2f}%")
        return cumul_returns[['Date','Cumul Returns']]
    
    def compute_volatility(self, returns):
        return returns.std() * np.sqrt(252)
    
    def compute_downside_volatility(self, returns):
        negative_returns = returns[returns < 0]
        return negative_returns.std() * np.sqrt(252)
    
    def compute_excess_returns(self, r, rfr):
        print(len(r), len(rfr))
        return  r - rfr
    
    def compute_sharpe_ratio(self, returns, risk_free_rate):
        excess_returns = self.compute_excess_returns(returns, risk_free_rate)
        vol = self.compute_volatility(returns)
        return (excess_returns.mean() / vol) * np.sqrt(252)
    
    def compute_sortino_ratio(self, returns, risk_free_rate):
        excess_returns = self.compute_excess_returns(returns, risk_free_rate)
        downside_vol = self.compute_downside_volatility(returns)
        return (excess_returns.mean() / downside_vol) * np.sqrt(252)
    
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

