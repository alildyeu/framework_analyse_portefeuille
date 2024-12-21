import pandas as pd
import streamlit as st
import plotly.express as px
import os

from src.datafile import DataFile
from src.factor import Factor
from src.asset import Fund, Benchmark
from src.utils import fund_loading_details, load_rfr, filter

# Framework d'Analyse de Fonds ---------------------------------------------------------------------------
st.title('Analyse de Fonds')

## Section 1 : Import & Traitement des Données -----------------------------------------------------------

### 1. Import des fonds et leur VL, selon l'entrée de l'utilisateur
aqr_dict, jpm_dict, schroder_dict = fund_loading_details()
fonds_dict = {'AQR Large Cap Multi-Style': aqr_dict,
               'JPM America Equity': jpm_dict, 
               'Schroder Global Sustainable Growth': schroder_dict}

fund_name = st.selectbox('Sélectionnez le fonds à analyser:', fonds_dict.keys())
st.header(f'{fund_name}')
fund = Fund(fonds_dict, fund_name)

### 2. Import des Facteurs de performance d'AQR
aqr_factors_list = ["MKT","SMB","HML FF","HML Devil","UMD"]
factors = {}
for factor in aqr_factors_list:
    factors[factor] = Factor(name = factor)

### 3. Import du Risk-Free Rate
rfr = load_rfr("RF")

### 4. Import du benchmark S&P500
spx = Benchmark("SPX")

## Section 2 : Performance & Risques -----------------------------------------------------------

### Graphique des VL
st.subheader(f'Historique des Valeurs liquidatives')
st.line_chart(fund.vl.set_index('Date'))

### Graphique rendements cumulés comparés au SP500 (base 100)
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


