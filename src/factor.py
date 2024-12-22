import os
import pandas as pd

from src.datafile import DataFile

class Factor():
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
            import_factor.data.loc[:, import_factor.data.columns != "Date"] *= 100
            self.value = import_factor.data
            import_factor.data.to_excel(factor_path, index = False)
