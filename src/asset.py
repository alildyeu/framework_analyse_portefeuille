import os
import pandas as pd

class FinancialAsset:
    def __init__(self, name):
        self.name = name
        self.data = None
        self.rdments = None

    def load_data(self, path, import_func):
        """
        Charge les données de l'actif financier à partir d'un fichier Excel ou en utilisant une fonction d'importation si le fichier excel n'est pas déjà crée.

        Args:
            path (str): Chemin vers le fichier Excel contenant les données.
            import_func (function): Fonction pour importer les données si le fichier n'existe pas.
        """

        if os.path.exists(path):
            self.data = pd.read_excel(path)
        else:
            self.data = import_func()
            self.data.to_excel(path, index=False)
    
    def compute_daily_returns(self, column_name):
        """
        Calcule les rendements quotidiens basés sur une colonne spécifique des données.

        Args:
            column_name (str): Nom de la colonne à partir de laquelle calculer les rendements (par exemple, 'Price' ou 'VL').
        """
        rdment = self.data.copy()
        rdment[f'{self.name}'] = rdment[column_name].pct_change() * 100
        self.rdments = rdment[['Date', f'{self.name}']]

    def compute_cumul_returns(self, returns: pd.DataFrame)-> pd.DataFrame:
        """
        Calcule les rendements cumulés à partir des rendements quotidiens.
        
        Args:
            returns (pd.DataFrame): DataFrame contenant les rendements quotidiens avec une colonne nommée après l'actif.
        
        Returns:
            pd.DataFrame: DataFrame avec les rendements cumulés.
        """
        cumul_returns = returns.copy()
        cumul_returns['Cumul Returns'] = ((cumul_returns[f'{self.name}'] / 100 + 1).cumprod() - 1) * 100
        return cumul_returns[['Date', 'Cumul Returns']]

    def compute_excess_returns(self, returns, risk_free_rate):
        return returns - risk_free_rate
    
    def compute_annualized_returns(self, returns):
        return (1 + returns.mean()) ** 252 - 1