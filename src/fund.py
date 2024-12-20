import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


class Fund():
    def __init__(self, name, data):
        """
        Initialize the Fund object.

        Parameters:
        - name (str): Name of the fund.
        - data (pd.DataFrame): DataFrame containing 'Date' and 'VL' columns.
        """
        self.name = name
        self.data = data
        self.daily_returns = self.compute_daily_returns()
        self.ytd = self.compute_ytd()
        self.vol = self.compute_volatility()

    def compute_daily_returns(self):
        self.data['Daily Returns'] = self.data['VL'].pct_change() * 100
        return self.data[['Date','Daily Returns']]
    
    def compute_ytd(self):
        start_vl = self.data.loc[self.data['Date'] >= "2024-01-01", 'VL'].iloc[0] # vl au premier jour ouvré de 2024
        end_vl = self.data['VL'].iloc[-1] # vl a la date la plus récente
        return (end_vl - start_vl)/start_vl * 100
    
    def compute_volatility(self):
        return self.data['Daily Returns'].std() * np.sqrt(252)

    def compute_sharpe_ratio(self):
        """Compute the Sharpe Ratio."""
        excess_returns = self.daily_returns - self.risk_free_rate
        return (excess_returns.mean() / self.volatility) * np.sqrt(252)

    def compute_downside_volatility(self):
        """Compute the downside volatility."""
        negative_returns = self.daily_returns[self.daily_returns < 0]
        return negative_returns.std() * np.sqrt(252)

    def compute_sortino_ratio(self):
        """Compute the Sortino Ratio."""
        excess_returns = self.daily_returns - self.risk_free_rate
        downside_vol = self.compute_downside_volatility()
        return (excess_returns.mean() / downside_vol) * np.sqrt(252)

    def compute_alpha(self, benchmark_returns):
        """Compute the alpha of the fund compared to a benchmark."""
        fund_excess_returns = self.daily_returns - self.risk_free_rate
        benchmark_excess_returns = benchmark_returns - self.risk_free_rate
        covariance = np.cov(fund_excess_returns[1:], benchmark_excess_returns[1:])[0, 1]
        beta = covariance / np.var(benchmark_excess_returns[1:])
        fund_annualized_return = (1 + self.daily_returns.mean()) ** 252 - 1
        benchmark_annualized_return = (1 + benchmark_returns.mean()) ** 252 - 1
        return fund_annualized_return - (self.risk_free_rate.mean() + beta * (benchmark_annualized_return - self.risk_free_rate.mean()))

    def compute_beta(self, benchmark_returns):
        """Compute the beta of the fund compared to a benchmark."""
        fund_excess_returns = self.daily_returns - self.risk_free_rate
        benchmark_excess_returns = benchmark_returns - self.risk_free_rate
        covariance = np.cov(fund_excess_returns[1:], benchmark_excess_returns[1:])[0, 1]
        return covariance / np.var(benchmark_excess_returns[1:])

    def compute_max_drawdown(self):
        """Compute the maximum drawdown."""
        cumulative_returns = (1 + self.daily_returns).cumprod()
        rolling_max = cumulative_returns.cummax()
        drawdown = cumulative_returns / rolling_max - 1
        return drawdown.min()

    def compute_relative_max_drawdown(self, benchmark_returns):
        """Compute the maximum relative drawdown compared to a benchmark."""
        fund_cumulative_returns = (1 + self.daily_returns).cumprod()
        benchmark_cumulative_returns = (1 + benchmark_returns).cumprod()
        relative_drawdown = fund_cumulative_returns / benchmark_cumulative_returns - 1
        return relative_drawdown.min()

    def compute_excess_return(self, benchmark_returns):
        """Compute total and annualized excess return compared to a benchmark."""
        fund_annualized_return = (1 + self.daily_returns.mean()) ** 252 - 1
        benchmark_annualized_return = (1 + benchmark_returns.mean()) ** 252 - 1
        total_excess_return = fund_annualized_return - benchmark_annualized_return
        return total_excess_return, total_excess_return / 252


    def compute_tracking_error(self, benchmark_returns):
        """Compute the tracking error."""
        return np.std(self.daily_returns - benchmark_returns) * np.sqrt(252)

class FactorialAnalysis(Fund):
    def __init__(self, name, data, region, factors):
        super().__init__(name, data)
        self.region = region
        self.factors = factors
        self.df = self.integrate_factors()
        self.regression = self.compute_regression()

    def integrate_factors(self):
        """
        Integrate factor data (e.g., AQR factors) into the fund data based on dates.
        Parameters:
        - factors (pd.DataFrame): DataFrame containing factor data with 'Date' as a column.
        """
        return pd.merge(self.data, self.factors, on='Date', how='inner')
    
    def compute_regression(self):
        """
        Perform regression to calculate metrics like Alpha, Beta, and Tracking Error.
        """

        # Perform regression (example with statsmodels or numpy)
        X = self.df[[f'MKT {self.region}', f'SMB {self.region}', f'HML FF {self.region}']]
        y = self.df['Daily Returns']
        X = sm.add_constant(X)  # Add constant for intercept
        model = sm.OLS(y, X).fit()

        return model.summary()

