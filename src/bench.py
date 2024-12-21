import os
import pandas as pd

from src.datafile import DataFile

class Benchmark():
    def __init__(self, name):
        self.name = name
        self.price = self.load_prices()
        self.rdments = self.compute_daily_returns()

    def load_prices(self, benchmark_name):
        if os.path.exists(bench_path:= f'data/loaded/bench/{benchmark_name}.xlsx'):
            self.price = pd.read_excel(bench_path)
        else :
            import_spx = DataFile(
            id= benchmark_name,
            filepath="data/bench",
            filename= "S&P 500 tracker",
            sheet = False,
            file_format= "csv",
            select_col = [0,1], # prix de clôture
            name_col = ['Date','Price'],
            first_date= "10/08/2024",
                    )
            self.price = import_spx.data
            import_spx.data.to_excel(bench_path, index = False)
            
    def compute_daily_returns(self):
        rdment = self.price.copy()
        rdment['Returns'] = rdment['Price'].pct_change() * 100
        return rdment[['Date','Returns']]
    
    def compute_cumul_returns(self, daily_returns):
        cumul_returns = daily_returns.copy()
        cumul_returns['Cumul Returns'] = (daily_returns['Returns'] / 100).cumsum() * 100
        cumul_returns['Cumul Returns'] = cumul_returns['Cumul Returns'].apply(lambda x: f"{x:.2f}%")
        return cumul_returns[['Date','Cumul Returns']]