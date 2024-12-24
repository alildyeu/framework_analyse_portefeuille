from src.datafile import DataFile
from src.asset import FinancialAsset

class Benchmark(FinancialAsset):
    """
    Classe Benchmark qui hérite de FinancialAsset.
    
    Cette classe représente un benchmark financier (par exemple, le S&P 500) et gère le chargement et le traitement de ses données.
    Elle permet de charger les données historiques du benchmark, de calculer les rendements quotidiens et de fournir une base de comparaison pour l'analyse des performances des fonds.
    
    Attributs hérités de FinancialAsset :
        - name (str) : Le nom du benchmark.
        - data (pd.DataFrame) : Les données historiques du benchmark.
        - daily_returns (pd.Series) : Les rendements quotidiens calculés à partir des données historiques.
    """
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