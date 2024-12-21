from src.datafile import DataFile
from src.asset import FinancialAsset

class Benchmark(FinancialAsset):
    def __init__(self, name):
        super().__init__(name)
        self.load_data(
            f'data/loaded/bench/{name}.xlsx',
            lambda: DataFile(
                id=name,
                filepath="data/bench",
                filename="S&P 500 tracker",
                sheet=False,
                file_format="csv",
                select_col=[0, 1],
                name_col=['Date', 'Price'],
                first_date="10/08/2024",
            ).data
        )
        self.compute_daily_returns('Price')