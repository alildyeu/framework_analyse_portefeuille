# %% 
import sys
print(sys.path)
import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import warnings
import streamlit as st
from functools import reduce
import plotly.express as px

from src.datafile import DataFile
from src.fund import Fund, FactorialAnalysis

# %% 
# Framework d'Analyse de Portefeuille
st.title('Analyse de Fonds')

# %% 
## Section 1 : Import & Traitement des Données -----------------------------------------------------------

### 1. Import des fonds et leur VL, selon l'entrée de l'utilisateur
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

fonds_dict = {'AQR Large Cap Multi-Style': [aqr_dict,"US"],
               'JPM America Equity': [jpm_dict,"US"], 
               'Schroder Global Sustainable Growth': [schroder_dict,"Global"]}

# Selection du fonds sur streamlit
fund_name = st.selectbox('Sélectionnez le fonds à analyser:', fonds_dict.keys())
st.header(f'{fund_name}')

# Import des vl du fonds correspondant
warnings.filterwarnings('ignore')
fund_vl = DataFile(**fonds_dict[fund_name][0]).data
fund_region = fonds_dict[fund_name][1]

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
        select_col= [0,25,26] if factor!="RF" else [0,1], # régions US et Monde
        name_col= ["Date",f"{factor} US",f"{factor} Global"] if factor!="RF" else ["Date","Risk Free Rate"],
        first_date= "01/03/1927"
        )

dataframes_factors = [f.data for f in factors.values() if f.id!="RF"]

# On consolide les dataframe de chaque facteur de performance en un mega dataframe
aqr_factors = reduce(
    lambda left, right: pd.merge(left, right, on="Date", how="inner"),
    dataframes_factors
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

sp500_price.data['SP500 Daily Returns'] = sp500_price.data['SPX Price'].pct_change() * 100

# %% 
## Section 2 : Performance & Risques -----------------------------------------------------------

fund = Fund(fund_name, fund_vl)

# Streamlit
# Graphique des VL
st.subheader(f'Historique des Valeurs liquidatives')
st.line_chart(fund_vl.set_index('Date')['VL'])

# Graphique rendements comparés au SP500
st.subheader(f'Historique des rendements')
daily = pd.merge(fund.daily_returns, sp500_price.data[['Date','SP500 Daily Returns']], on='Date', how='inner') 

# Calcul en base 100
daily[f'{fund_name}'] = (1 + daily['Daily Returns'] / 100).cumprod() * 100
daily['SP500'] = (1 + daily['SP500 Daily Returns'] / 100).cumprod() * 100
fig = px.line(daily, x='Date', y=[f'{fund_name}', 'SP500'])
st.plotly_chart(fig)

st.subheader(f'YTD = {fund.ytd:.2f}%')

st.subheader(f'Volatilité = {fund.vol:.2f}%')

# %% 
## Section 3 : Analyse Factorielle  -----------------------------------------------------------

st.subheader(f'Résultats Régression')
factorial_analysis = FactorialAnalysis(fund_name, fund_vl, fund_region, aqr_factors)
factorial_analysis.regression

