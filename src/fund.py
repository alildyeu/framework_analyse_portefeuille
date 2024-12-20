import pandas as pd
import numpy as np
import statsmodels.api as sm

class Fund():
    def __init__(self, name, data, region):
        """
        Initialize the Fund object.

        Parameters:
        - name (str): Name of the fund.
        - data (pd.DataFrame): DataFrame containing 'Date' and 'VL' columns.
        """
        self.name = name
        self.data = data
        self.region = region
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
        pass

class FactorialAnalysis(Fund):
    def __init__(self, name, data, region, factors):
        super().__init__(name, data, region)
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
