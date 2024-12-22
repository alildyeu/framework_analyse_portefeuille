import pandas as pd
import streamlit as st
import plotly.express as px
import os
import numpy as np
from src.datafile import DataFile
from src.factor import Factor
from src.fund import Fund
from src.bench import Benchmark
from src.utils import fund_loading_details, load_rfr, filter, find_unique_end_date


def main():
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
    fund = Fund(fund_name, fonds_dict)

    ### 2. Import des Facteurs de performance d'AQR
    aqr_factors_list = ["MKT","SMB","HML FF","HML Devil","UMD"]
    factors = {}
    for factor in aqr_factors_list:
        factors[factor] = Factor(name = factor)

    ### 3. Import du Risk-Free Rate
    rfr = load_rfr("RF")

    ### 4. Import du benchmark S&P500
    spx = Benchmark("SPX")

    ## Section 2 : Performance & Risques --------------------------------------------------------------------------

    ### Graphique des VL
    st.subheader(f'Historique des Valeurs liquidatives')
    st.line_chart(fund.data.set_index('Date'))

    ### Graphique rendements cumulés comparés au SP500 (base 100)
    st.subheader(f'Rendements cumulés')

    start_date = fund.rdments.iloc[0,0] # date a laquelle premiere donnee est dispo
    end_date = find_unique_end_date([fund.rdments, spx.rdments]) # s'assure que toutes les données s'étalent sur la même periode
    daily_returns_fund = filter(fund.rdments, start_date, end_date)
    daily_returns_bench = filter(spx.rdments, start_date, end_date)

    cumul_returns = pd.merge(
        fund.compute_cumul_returns(daily_returns_fund),
        spx.compute_cumul_returns(daily_returns_bench),
        on='Date', how='inner'
        ).rename(columns={'Cumul Returns_x': f'{fund_name}', 'Cumul Returns_y': f'{spx.name}'}
    )
    fig = px.line(cumul_returns, x='Date', y=[f'{fund_name}', f'{spx.name}'])
    st.plotly_chart(fig)

    ### Statistiques
    fenetres = {
        "YTD" : "2024-01-01",
        "1 an" : fund.rdments.iloc[-252,0],
        "3 ans" : fund.rdments.iloc[-252*3,0],
        "5 ans" : fund.rdments.iloc[-252*5,0]
    }

    performance = pd.DataFrame(columns= fenetres.keys())
    sortino = pd.DataFrame(columns= fenetres.keys())
    alpha_beta = pd.DataFrame(columns= fenetres.keys())

    for periode, start_date in fenetres.items():
        dataset = pd.merge(pd.merge(fund.rdments, rfr, how='inner', on='Date'), spx.rdments, how='inner', on='Date')
        dataset = filter(dataset, start_date, end_date:=dataset.iloc[-1,0])
        daily_returns_bench = dataset[f'{fund.name}']
        daily_returns_fund = dataset[f'{spx.name}']
        risk_free_rate = dataset['RF']

    perf = f"{fund.compute_cumul_returns(dataset[['Date',f'{fund.name}']]).iloc[-1]['Cumul Returns']:.2f}%"
    vol = f"{fund.compute_volatility(daily_returns_fund):.2f}%"
    sharpe_ratio = f"{fund.compute_sharpe_ratio(daily_returns_fund,risk_free_rate):.2f}"
    performance[periode] = [perf, vol, sharpe_ratio]

    downside_vol = f"{fund.compute_downside_volatility(daily_returns_fund):.2f}%"
    sortino_ratio = f"{fund.compute_sortino_ratio(daily_returns_fund, risk_free_rate):.2f}"
    sortino[periode] = [downside_vol, sortino_ratio]

    beta = fund.compute_beta(daily_returns_fund, daily_returns_bench, risk_free_rate)
    alpha = fund.compute_alpha(daily_returns_fund, daily_returns_bench, risk_free_rate)
    alpha_beta[periode] = [beta, alpha]

    performance.index=['Performance','Volatility','Sharpe Ratio']
    sortino.index=['Downside Volatility','Sortino Ratio']
    alpha_beta.index = ['Alpha','Beta']

    #### Récapitulatif performances
    st.subheader('Récapitulatif Performance')
    st.table(performance)

    #### Sortino Ratio
    st.subheader('Sortino Ratio')
    st.table(sortino)

    #### Risque
    st.subheader('Market Performance')
    st.table(alpha_beta)

    #### Comparaison performances
    st.subheader('Comparaison Performance')
    fund_bis_names = st.multiselect('Sélectionnez les fonds à comparer:', [f for f in fonds_dict.keys() if f!=fund_name])
    window = st.selectbox("Sélectionnez la période d'analyse:", fenetres.keys())

    fund_bis_names.append(fund_name)
    performance_comparees = pd.DataFrame(columns= fund_bis_names)

    for fund_bis_name in fund_bis_names:
        fund_bis = Fund(fund_bis_name, fonds_dict)
        dataset = pd.merge(fund_bis.rdments, rfr, how='inner', on='Date')
        dataset = filter(dataset, start_date:=fenetres[window], end_date:=dataset.iloc[-1,0])
        daily_returns_fund_bis = dataset[f'{fund_bis.name}']
        risk_free_rate = dataset['RF']
    
    perf = f"{fund_bis.compute_cumul_returns(dataset[['Date',f'{fund_bis.name}']]).iloc[-1]['Cumul Returns']:.2f}%"
    vol = f"{fund_bis.compute_volatility(daily_returns_fund_bis):.2f}%"
    sharpe_ratio = f"{fund_bis.compute_sharpe_ratio(daily_returns_fund_bis,risk_free_rate):.2f}"
    performance_comparees[fund_bis.name] = [perf, vol, sharpe_ratio]

    performance_comparees.index=['Performance','Volatilité','Sharpe Ratio']
    st.table(performance_comparees)

if __name__ == '__main__':
    main()


## Section 3 : Analyse Factorielle  -----------------------------------------------------------


