import os
import pandas as pd
import warnings

from src.datafile import DataFile

warnings.filterwarnings('ignore')

# Details fichiers par fonds analysés ------------------------------------------------------------
def fund_loading_details():
    
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
def filter(data, start_date, end_date):
    return data[(data['Date'] >= start_date) & (data['Date'] <= end_date)]