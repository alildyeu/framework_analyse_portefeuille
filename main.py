import pandas as pd
import warnings
import streamlit as st
import plotly.express as px
import os

from src.datafile import DataFile
from src.fund import Fund
from src.factor import Factor
from src.bench import Benchmark

# Framework d'Analyse de Fonds ---------------------------------------------------------------------------
st.title('Analyse de Fonds')

## Section 1 : Import & Traitement des Données -----------------------------------------------------------

### 1. Import des fonds et leur VL, selon l'entrée de l'utilisateur
warnings.filterwarnings('ignore')

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

fund_name = st.selectbox('Sélectionnez le fonds à analyser:', fonds_dict.keys())
st.header(f'{fund_name}')

if os.path.exists(fund_path:= f'data/loaded/funds/{fund_name}.xlsx'):
    fund = Fund(name = fund_name, vl = pd.read_excel(fund_path), region = fonds_dict[fund_name][1])
else:  
    import_fund = DataFile(**fonds_dict[fund_name][0])
    fund = Fund(name = fund_name, vl = import_fund.data, region = fonds_dict[fund_name][1])
    import_fund.data.to_excel(fund_path, index = False)

### 2. Import des Facteurs de performance d'AQR

factors_list = ["MKT","SMB","HML FF","HML Devil","UMD"]
factors = {}

for factor in factors_list:
    if os.path.exists(factor_path:= f'data/loaded/factors/{factor}.xlsx'):
        factors[factor] = Factor(name = factor, value = pd.read_excel(factor_path))
    else:
        import_factor = DataFile(
            id= factor,
            filepath= "data/aqr factors",
            filename= "Betting Against Beta Equity Factors Daily",
            sheet= True,
            file_format= "xlsx",
            select_col= [0,25,26], # régions US et Monde
            name_col= ["Date",f"{factor} US",f"{factor} Global"],
            first_date= "01/03/1927"
            )
        factors[factor] = Factor(name = factor, value = import_factor.data)
        import_factor.data.to_excel(factor_path, index = False)

### 3. Import du Risk-Free Rate
if os.path.exists(rf_path:= f'data/loaded/factors/RF.xlsx'):
    rfr = pd.read_excel(rf_path)
else :
    import_rf = DataFile(
            id= "RF",
            filepath= "data/aqr factors",
            filename= "Betting Against Beta Equity Factors Daily",
            sheet= True,
            file_format= "xlsx",
            select_col= [0,1],
            name_col= ["Date","RF"],
            first_date= "01/03/1927"
            )
    rfr = import_rf.data
    import_rf.data.to_excel(rf_path, index = False)

### 4. Import du benchmark S&P500

if os.path.exists(bench_path:= f'data/loaded/bench/SP500.xlsx'):
    spx = Benchmark(name = "SPX", price = pd.read_excel(bench_path))
else :
    import_spx = DataFile(
    id="SPX",
    filepath="data/bench",
    filename= "S&P 500 tracker",
    sheet = False,
    file_format= "csv",
    select_col = [0,1], # prix de clôture
    name_col = ['Date','Price'],
    first_date= "10/08/2024",
            )
    spx = Benchmark(name = "SPX", price = import_spx.data)
    import_spx.data.to_excel(bench_path, index = False)

# %% 
## Section 2 : Performance & Risques -----------------------------------------------------------

def filter(data, start_date, end_date):
    return data[(data['Date'] >= start_date) & (data['Date'] <= end_date)]

# Graphique des VL
st.subheader(f'Historique des Valeurs liquidatives')
st.line_chart(fund.vl.set_index('Date'))

# Graphique rendements cumulés comparés au SP500 (base 100)
st.subheader(f'Rendements cumulés')
start_date = max(fund.rdments.iloc[0,0], spx.rdments.iloc[0,0])
end_date = max(fund.rdments.iloc[-1,0], spx.rdments.iloc[-1,0])

cumul_returns = pd.merge(
    fund.compute_cumul_returns(filter(fund.rdments, start_date, end_date)), 
    spx.compute_cumul_returns(filter(spx.rdments, start_date, end_date)), 
    on='Date', how='inner'
    ).rename(columns={'Cumul Returns_x': f'{fund_name}', 'Cumul Returns_y': 'SP500'}
)
fig = px.line(cumul_returns, x='Date', y=[f'{fund_name}', 'SP500'])
st.plotly_chart(fig)

# Récapitulatif Performance
st.subheader('Récapitulatif Performance')

start_dates = {
    "YTD" : "2024-01-01",
    "1 an" : fund.rdments.iloc[-252,0],
    "3 ans" : fund.rdments.iloc[-252*3,0],
    "5 ans" : fund.rdments.iloc[-252*5,0]
}

performance = pd.DataFrame(columns= start_dates.keys())
sortino = pd.DataFrame(columns= start_dates.keys())
alpha = pd.DataFrame(columns= ["Alpha","Beta"])

for periode in start_dates.keys():
    data_periode = filter(fund.rdments, start_dates[periode], fund.rdments.iloc[-1,0])
    rfr_periode = filter(rfr, start_dates[periode], fund.rdments.iloc[-1,0])

    # Merge data_periode and rfr_periode on Date to align them
    merged_data = pd.merge(
        data_periode[['Date', 'Returns']],
        rfr_periode[['Date', 'RF']],
        on='Date',
        how='inner'
    )

    # Ensure no NaN values exist after merging
    if merged_data.isnull().values.any():
        st.warning(f"Missing values detected for the period: {periode}. Please check your data.")
        continue

    # Extract aligned Returns and RF
    aligned_returns = merged_data['Returns']
    aligned_rf = merged_data['RF']

    perf = fund.compute_cumul_returns(data_periode).iloc[-1]["Cumul Returns"]
    vol = f"{fund.compute_volatility(aligned_returns):.2f}%"
    sharpe_ratio = f"{fund.compute_sharpe_ratio(aligned_returns,aligned_rf):.2f}"
    performance[periode] = [perf, vol, sharpe_ratio]

    downside_vol = f"{fund.compute_downside_volatility(aligned_returns):.2f}%"
    sortino_ratio = f"{fund.compute_sortino_ratio(aligned_returns, aligned_rf):.2f}"
    sortino[periode] = [downside_vol, sortino_ratio]

performance.index=['Performance','Volatility','Sharpe Ratio']
sortino.index=['Downside Volatility','Sortino Ratio']
st.table(performance)

# Comparaison performances
st.subheader('Comparaison Performance')
funds_comp_name = st.multiselect('Sélectionnez les fonds à comparer:', [f for f in fonds_dict.keys() if f!=fund_name])
window = st.selectbox("Sélectionnez la période d'analyse:", start_dates.keys())

funds_comp_name.append(fund_name)
performance_comparees = pd.DataFrame(columns= funds_comp_name)

for fund_comp_name in funds_comp_name:
    if os.path.exists(fund_comp_path:= f'data/loaded/funds/{fund_comp_name}.xlsx'):
        fund_comp = Fund(name = fund_comp_name, vl = pd.read_excel(fund_comp_path), region = fonds_dict[fund_comp_name][1])
    else:  
        import_fund_comp = DataFile(**fonds_dict[fund_comp_name][0])
        fund_comp = Fund(name = fund_comp_name, vl = import_fund_comp.data, region = fonds_dict[fund_name][1])
        import_fund_comp.data.to_excel(funds_comp_name, index = False)
    
    data_window = filter(fund_comp.rdments, start_dates[window], fund_comp.rdments.iloc[-1,0])
    rfr_window = filter(rfr, start_dates[window], fund_comp.rdments.iloc[-1,0])
    
    # Merge data_periode and rfr_periode on Date to align them
    merged_window = pd.merge(
        data_periode[['Date', 'Returns']],
        rfr_periode[['Date', 'RF']],
        on='Date',
        how='inner'
    )

    # Ensure no NaN values exist after merging
    if merged_window.isnull().values.any():
        st.warning(f"Missing values detected for the period: {periode}. Please check your data.")
        continue

    # Extract aligned Returns and RF
    aligned_r = merged_window['Returns']
    aligned_rfr = merged_window['RF']
    
    perf = fund_comp.compute_cumul_returns(data_window).iloc[-1]["Cumul Returns"]
    vol = f"{fund_comp.compute_volatility(aligned_r):.2f}%"
    sharpe_ratio = f"{fund_comp.compute_sharpe_ratio(aligned_r, aligned_rfr):.2f}"
    performance_comparees[fund_comp_name] = [perf, vol, sharpe_ratio]

performance_comparees.index=['Performance','Volatilité','Sharpe Ratio']
st.table(performance_comparees)

# Other Metrics
st.subheader('Other Metrics')
st.table(sortino)

# %% 
## Section 3 : Analyse Factorielle  -----------------------------------------------------------


