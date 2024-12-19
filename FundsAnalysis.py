# %%
import pandas as pd
import warnings
from functools import reduce
import streamlit as st

# %% 
# Framework d'Analyse de Portefeuille
st.title('Analyse de Fonds')
# %% 
## Section 1 : Import & Traitement des Données -----------------------------------------------------------

class DataFile:
    def __init__(self, id: str, filepath: str, filename: str, sheet: bool, file_format: str, select_col: list, name_col: list, first_date : str):
        self.id = id
        self.filepath = filepath
        self.filename = filename
        self.sheet = sheet
        self.file_format = file_format
        self.select_col = select_col
        self.name_col = name_col
        self.first_date = first_date
        self.df = self.load_data()

    def load_data(self):
        """Cette méthode charge le fichier sélectionné dans un dataframe. Pour ce faire, elle fait appel à trois autres méthodes : import_data(), filter_columns() et clean_data().Elle retourne donc un dataframe, enregistré dans self.df."""
        
        data = self.import_data()
        data_filtered = self.filter_columns(data)
        final_data = self.clean_data(data_filtered)
        return final_data

    def import_data(self):
        """Cette méthode se charge d'importer les données depuis les fichiers. Elle tient compte du format du fichier (excel ou csv, plusieurs feuilles ou pas) renseigné en input. Elle renvoit donc un dataframe."""
        
        dict_format = {"xlsx":"excel",
                       "csv":"csv"}   
        if self.file_format in dict_format.keys():
            if self.sheet: # si le excel contient plusieurs feuilles (self.sheet = True), selectionne la bonne.
                data = getattr(pd,f"read_{dict_format[self.file_format]}")(f"{self.filepath}/{self.filename}.{self.file_format}",sheet_name = self.id)
            else:
                data = getattr(pd,f"read_{dict_format[self.file_format]}")(f"{self.filepath}/{self.filename}.{self.file_format}")            
            return data
        else:
            raise ValueError("Unsupported file type. Use 'xlsx' or 'csv'.")
    
    def filter_columns(self, data):
        """Cette méthode filtre les colonnes qui nous interessent dans le cadre du projet (dates, VL pour les fonds, données US et Monde pour les facteurs AQR ...) et renvoie le dataframe filtré. """
        
        data = data[[data.columns[idx] for idx in self.select_col]] 
        data.columns = self.name_col # on renomme les colonnes avec les noms renseignés en input
        return data
    
    def clean_data(self, data_filtered):
        """Cette méthode s'assure de la propreté des données en enlevant les informations non nécessaire au projet et s'assurant du bon format des données."""
        
        while data_filtered.iloc[0,0] != self.first_date: # tant que la première cellule du dataframe ne correspond pas à la première date de la série
            data_filtered = data_filtered.iloc[1:] # on supprime la première ligne
        
        data_filtered.Date = pd.to_datetime(data_filtered.Date, infer_datetime_format=True) # format datetime pour les dates
        filter_float = data_filtered.columns.difference(['Date'])
        data_filtered[filter_float] = data_filtered[filter_float].replace(",",".",regex=True).astype(float) # format float pour le reste

        data_filtered = data_filtered.dropna(axis="index") # on supprime les lignes sans données
        return data_filtered

# %%
### 1. Import des fonds et leur VL, selon l'entrée de l'utilisateur

aqr_dict = {
    "id":"US00203H4956",
    "filepath":"data/funds",
    "filename": "AQR Large Cap Multi-Style Fund Daily Price History",
    "sheet": False,
    "file_format": "csv",
    "select_col": [2,6],
    "name_col": ['Date','US00203H4956'],
    "first_date": "26/03/2013 00:00",
            }

jpm_dict = {
    "id":"LU0129459060",
    "filepath":"data/funds",
    "filename":"JPMorgan Funds - America Equity Fund",
    "sheet":False,
    "file_format": "xlsx",
    "select_col": [0,1],
    "name_col": ['Date','LU0129459060'],
    "first_date": "30.08.2019",
            }

schroder_dict = {
    "id":"LU0557290854",
    "filepath":"data/funds",
    "filename": "Schroder International Selection Fund Global Sustainable Growth C Accumulation USD",
    "sheet": False,
    "file_format": "csv",
    "select_col": [4,5],
    "name_col": ['Date','LU0557290854'],
    "first_date": "09.10.2024",
            }

fonds_dict = {'AQR Large Cap Multi-Style': aqr_dict,
               'JPM America Equity': jpm_dict, 
               'Schroder Global Sustainable Growth': schroder_dict}

# selection du fonds sur streamlit
fonds = st.selectbox('Sélectionnez le fonds à analyser:', fonds_dict.keys())
st.header(f'{fonds}')

# chargement des vl du fonds
warnings.filterwarnings('ignore')
fund_vl = DataFile(**fonds_dict[fonds]).df

# affichage gaphique des VL sur streamlit
st.subheader(f'Valeurs liquidatives du fonds')
st.line_chart(fund_vl.set_index('Date'))

# %% 
### 2. Import des Facteurs de performance d'AQR

factors_list = ["MKT","SMB","HML FF","HML Devil","UMD","RF"]
factors = {}

for factor in factors_list:
    factors[factor] = DataFile(
        id= factor,
        filepath= "data/aqr factors",
        filename= "Betting Against Beta Equity Factors Daily",
        sheet= True,
        file_format= "xlsx",
        select_col= [0,25,26,27] if factor!="RF" else [0,1],
        name_col= ["Date",f"{factor} USA",f"{factor} Global",f"{factor} Global Ex USA"] if factor!="RF" else ["Date","Risk Free Rate"],
        first_date= "01/03/1927"
        )

dataframes = [f.df for f in factors.values()]

# On consolide les dataframe de chaque facteur de performance en un mega dataframe
aqr_factors = reduce(
    lambda left, right: pd.merge(left, right, on="Date", how="inner"),
    dataframes
)

# %% 
### 3. Import du benchmark S&P500

sp500_price = DataFile(
    id="SPX",
    filepath="data",
    filename= "S&P 500 tracker",
    sheet = False,
    file_format= "csv",
    select_col = [0,1], # prix de clôture
    name_col = ['Date','SPX Price'],
    first_date= "10/08/2024",
            )


