import statsmodels.api as sm
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from src.asset import Fund

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