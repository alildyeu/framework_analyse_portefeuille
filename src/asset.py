import os
import pandas as pd

class FinancialAsset:
    def __init__(self, name):
        self.name = name
        self.data = None
        self.rdments = None

    def load_data(self, path, import_func):
        if os.path.exists(path):
            self.data = pd.read_excel(path)
        else:
            self.data = import_func()
            self.data.to_excel(path, index=False)
    
    def compute_daily_returns(self, column_name):
        rdment = self.data.copy()
        rdment[f'{self.name}'] = rdment[column_name].pct_change() * 100
        self.rdments = rdment[['Date', f'{self.name}']]

    def compute_cumul_returns(self, returns):
        cumul_returns = returns.copy()
        cumul_returns['Cumul Returns'] = ((cumul_returns[f'{self.name}'] / 100 + 1).cumprod() - 1) * 100
        return cumul_returns[['Date', 'Cumul Returns']]
