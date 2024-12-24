import os # Module pour interagir avec le système d'exploitation
import pandas as pd # Bibliotheque pour la manipulation des données
from src.datafile import DataFile # Importation de la classe DataFile depuis le module src.datafile

class Factor():
    """
    Classe Factor pour gérer les facteurs de performance financiers.

    Cette classe représente un facteur de performance (par exemple, MKT, SMB, etc.) et gère le chargement et le traitement de ses données.
    Elle permet de charger les données historiques du facteur, de les séparer par région (US et Global), et de les préparer pour l'analyse factorielle.

    Attributs :
        - name (str) : Le nom du facteur de performance.
        - value (pd.DataFrame) : Les données historiques du facteur.
        - us (pd.DataFrame) : Les données du facteur pour la région US.
        - monde (pd.DataFrame) : Les données du facteur pour la région Global.
    """

    def __init__(self, name):
        self.name = name
        self.load_value()
        self.us = self.value[['Date',f'{name} US']]
        self.monde = self.value[['Date',f'{name} Global']]

    def load_value(self):
        if os.path.exists(factor_path:= f'data/loaded/factors/{self.name}.xlsx'):
            self.value = pd.read_excel(factor_path)
        else:
            import_factor = DataFile(
                id= self.name,
                filepath= "data/aqr factors",
                filename= "Betting Against Beta Equity Factors Daily",
                sheet= True,
                file_format= "xlsx",
                select_col= [0,25,26], # régions US et Monde
                name_col= ["Date",f"{self.name} US",f"{self.name} Global"],
                first_date= "01/03/1927"
                )
            import_factor.data.loc[:, import_factor.data.columns != "Date"] *= 100 # Multiplier les colonnes autres que 'Date' par 100 pour convertir les rendements en pourcentage
            self.value = import_factor.data # Sauvegarder les données importées dans un fichier Excel pour les utilisations futures
            import_factor.data.to_excel(factor_path, index = False)
