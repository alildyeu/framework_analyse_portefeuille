class Benchmark():
    def __init__(self, name, price):
        self.name = name
        self.price = price
        self.rdments = self.compute_daily_returns()

    def compute_daily_returns(self):
        rdment = self.price.copy()
        rdment['Returns'] = rdment['Price'].pct_change() * 100
        return rdment[['Date','Returns']]
    
    def compute_cumul_returns(self, daily_returns):
        cumul_returns = daily_returns.copy()
        cumul_returns['Cumul Returns'] = (daily_returns['Returns'] / 100).cumsum() * 100
        cumul_returns['Cumul Returns'] = cumul_returns['Cumul Returns'].apply(lambda x: f"{x:.2f}%")
        return cumul_returns[['Date','Cumul Returns']]