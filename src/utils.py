import os
import pandas as pd
import warnings # Module pour gérer les avertissements

from src.datafile import DataFile # Importation de la classe DataFile depuis le module src.datafile

warnings.filterwarnings('ignore')

# Details fichiers par fonds analysés ------------------------------------------------------------
def fund_loading_details():
    """
        Définit les détails des fichiers pour les fonds analysés.

        Retourne:
            tuple: Contient trois dictionnaires (aqr_dict, jpm_dict, schroder_dict) avec les
                   informations nécessaires pour charger les données de chaque fonds.
        """

    aqr_dict = {
    "id":"US00203H4956",
    "filepath":"data/funds",
    "filename": "AQR Large Cap Multi-Style Fund Daily Price History",
    "sheet": False,
    "file_format": "csv",
    "select_col": [2,6],
    "name_col": ['Date','VL'],
    "first_date": "26/03/2013 00:00",
            }

    jpm_dict = {
        "id":"LU0129459060",
        "filepath":"data/funds",
        "filename":"JPMorgan Funds - America Equity Fund",
        "sheet":False,
        "file_format": "xlsx",
        "select_col": [0,1],
        "name_col": ['Date','VL'],
        "first_date": "30.08.2019",
                }

    schroder_dict = {
        "id":"LU0557290854",
        "filepath":"data/funds",
        "filename": "Schroder International Selection Fund Global Sustainable Growth C Accumulation USD",
        "sheet": False,
        "file_format": "csv",
        "select_col": [4,5],
        "name_col": ['Date','VL'],
        "first_date": "09.10.2024",
                }
    
    return aqr_dict, jpm_dict, schroder_dict
#---------------------------------------------------------------------------------------------------------
def load_rfr(name):
    """
        Charge les données du taux sans risque (Risk-Free Rate).

        Args:
            name (str): Nom du taux sans risque à charger (par exemple, 'RF').

        Retourne:
            pd.DataFrame: DataFrame contenant les données du taux sans risque.
        """
    if os.path.exists(rf_path:= f'data/loaded/factors/{name}.xlsx'):
        rfr = pd.read_excel(rf_path)
    else :
        import_rf = DataFile(
                id= name,
                filepath= "data/aqr factors",
                filename= "Betting Against Beta Equity Factors Daily",
                sheet= True,
                file_format= "xlsx",
                select_col= [0,1],
                name_col= ["Date",f"{name}"],
                first_date= "01/03/1927"
                )
        rfr = import_rf.data
        import_rf.data.to_excel(rf_path, index = False)
    return rfr
#--------------------------------------------------------------------------------------------------------
def find_unique_end_date(dataframes):
    """
    Trouve la date de fin unique la plus récente parmi plusieurs DataFrames.

    Args:
        dataframes (list of pd.DataFrame): Liste des DataFrames à examiner.

    Retourne:
        str: Date de fin unique minimale parmi toutes les dates de fin des DataFrames.
    """
    end_dates = []
    for df in dataframes:
        end_dates.append(df.iloc[-1,0])
    end_date = min(end_dates)
    return end_date
#--------------------------------------------------------------------------------------------------------
def filter(data, start_date, end_date):
    """
        Filtre les données entre une date de début et une date de fin spécifiées.

        Args:
            data (pd.DataFrame): DataFrame à filtrer contenant une colonne 'Date'.
            start_date (str): Date de début pour le filtrage (format 'YYYY-MM-DD' ou similaire).
            end_date (str): Date de fin pour le filtrage (format 'YYYY-MM-DD' ou similaire).

        Retourne:
            pd.DataFrame: DataFrame filtré contenant uniquement les lignes entre start_date et end_date inclus.
        """
    return data[(data['Date'] >= start_date) & (data['Date'] <= end_date)]
#--------------------------------------------------------------------------------------------------------
