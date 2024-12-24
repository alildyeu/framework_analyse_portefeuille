import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from itertools import cycle


from src.risk import Risk
from src.factor import Factor
from src.fund import Fund
from src.bench import Benchmark
from src.factoranalysis import FactorialAnalysis
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
    
    region_fund = {'AQR Large Cap Multi-Style': "US",
                   'JPM America Equity': "US",
                   'Schroder Global Sustainable Growth': "Global"}

    fund_name = st.selectbox('Sélectionnez le fonds à analyser:', fonds_dict.keys())
    st.header(f'{fund_name}')
    fund = Fund(fund_name, region_fund[fund_name], fonds_dict)

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
    st.subheader(f'Historique des valeurs liquidatives')
    st.line_chart(fund.data.set_index('Date'))

    ### Statistiques
    fenetres = {
        "YTD" : "2024-01-01",
        "1 an" : fund.rdments.iloc[-252,0],
        "3 ans" : fund.rdments.iloc[-252*3,0],
        "5 ans" : fund.rdments.iloc[-252*5,0]
    }

    recap = pd.DataFrame(columns= fenetres.keys())
    performance = pd.DataFrame(columns= fenetres.keys())
    risques = pd.DataFrame(columns= fenetres.keys())

    for periode, start_date in fenetres.items():
        dataset = pd.merge(pd.merge(fund.rdments, rfr, how='inner', on='Date'), spx.rdments, how='inner', on='Date')
        dataset = filter(dataset, start_date, end_date:=dataset.iloc[-1,0])
        daily_returns_bench = dataset[f'{fund.name}']
        daily_returns_fund = dataset[f'{spx.name}']
        risk_free_rate = dataset['RF']

        perf = f"{fund.compute_cumul_returns(dataset[['Date',f'{fund.name}']]).iloc[-1]['Cumul Returns']:.2f}%"
        vol = f"{fund.compute_volatility(daily_returns_fund):.2f}%"
        downside_vol = f"{fund.compute_downside_volatility(daily_returns_fund):.2f}%"
        sharpe_ratio = f"{fund.compute_sharpe_ratio(daily_returns_fund,risk_free_rate):.2f}"
        sortino_ratio = f"{fund.compute_sortino_ratio(daily_returns_fund, risk_free_rate):.2f}"
        risk = Risk(fund, spx)
        beta = f"{risk.compute_beta(daily_returns_fund, daily_returns_bench):.2f}"
        alpha = f"{risk.compute_alpha(daily_returns_fund, daily_returns_bench, risk_free_rate):.2f}"
        rel_max_dd = f"{risk.compute_relative_max_drawdown(dataset[['Date',f'{fund.name}']], dataset[['Date',f'{spx.name}']]):.2f}"
        
        recap[periode] = [perf, vol, sharpe_ratio]
        performance[periode] = [perf, alpha, sharpe_ratio, sortino_ratio]
        risques[periode] = [vol, downside_vol, beta, rel_max_dd ]

    recap.index=['Performance','Volatility','Sharpe Ratio']
    performance.index=['Performance','Alpha','Sharpe Ratio','Sortino Ratio']
    risques.index = ['Volatility','Downside Volatility','Beta','Relative Maximum Drawdown']

    #### Récapitulatif performances
    st.subheader('Synthèse Performance')
    st.table(recap)

    #### Comparaison performances
    st.subheader('Comparaison Performance')
    fund_bis_names = st.multiselect('Sélectionnez les fonds à comparer:', [f for f in fonds_dict.keys() if f!=fund_name])
    window = st.selectbox("Sélectionnez la période d'analyse:", fenetres.keys())

    fund_bis_names.append(fund_name)
    performance_comparees = pd.DataFrame(columns= fund_bis_names)

    for fund_bis_name in fund_bis_names:
        fund_bis = Fund(fund_bis_name, region_fund[fund_bis_name],fonds_dict)
        dataset = pd.merge(fund_bis.rdments, rfr, how='inner', on='Date')
        time_window = {
        "YTD" : "2024-01-01",
        "1 an" : fund_bis.rdments.iloc[-252,0],
        "3 ans" : fund_bis.rdments.iloc[-252*3,0],
        "5 ans" : fund_bis.rdments.iloc[-252*5,0]}

        dataset = filter(dataset, start_date:=time_window[window], end_date:=dataset.iloc[-1,0])
        daily_returns_fund_bis = dataset[f'{fund_bis.name}']
        risk_free_rate = dataset['RF']
    
        perf = f"{fund_bis.compute_cumul_returns(dataset[['Date',f'{fund_bis.name}']]).iloc[-1]['Cumul Returns']:.2f}%"
        vol = f"{fund_bis.compute_volatility(daily_returns_fund_bis):.2f}%"
        sharpe_ratio = f"{fund_bis.compute_sharpe_ratio(daily_returns_fund_bis,risk_free_rate):.2f}"
        performance_comparees[fund_bis.name] = [perf, vol, sharpe_ratio]

    performance_comparees.index=['Performance','Volatilité','Sharpe Ratio']
    st.table(performance_comparees)
    st.info("ℹ️ Les performances comparées et synthétisées dans le tableau du dessus diffèrent légèrement : les fenêtres de calcul sont en effet harmonisées pour pouvoir comparer les fonds entre eux")

    #### Graphique rendements cumulés comparés au SP500 (base 100)
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

    #### Perfomance Metrics
    st.subheader('Perfomance Metrics')
    st.table(performance)
    perf_description = {
    "Performance": "Le rendement cumulatif montre la performance totale du fonds sur une période donnée.",
    "Volatility": "La volatilité mesure la variation des rendements du fonds, indiquant le niveau de risque.",
    "Sharpe Ratio": "Le ratio de Sharpe évalue le rendement ajusté au risque, calculant combien de rendement excédentaire vous obtenez par unité de volatilité.",
    "Alpha": "L'alpha mesure la performance du fonds par rapport à son benchmark, indiquant la valeur ajoutée par le gestionnaire de fonds.",
    "Sortino Ratio": "Le ratio de Sortino est similaire au ratio de Sharpe mais se concentre uniquement sur la volatilité négative, offrant une évaluation plus précise du risque de baisse.",
    }
    # Explications
    with st.expander("📖 Explications des métriques de performance"):
        for ratio, description in perf_description.items():
            if ratio in performance.index:
                st.markdown(f"*{ratio}*: {description}")

    #### Risque Metrics
    st.subheader('Risk Metrics')
    st.table(risques)
    # Explications
    risk_description = {
    "Downside Volatility": "La volatilité négative mesure uniquement les variations à la baisse des rendements, fournissant une évaluation du risque de perte.",
    "Beta": "Le bêta mesure la sensibilité du fonds par rapport aux mouvements du benchmark, indiquant le niveau de risque systématique.",
    "Relative Maximum Drawdown": "La baisse maximale relative compare la plus grande perte du fonds à celle du benchmark, évaluant la résilience face aux pertes."
    }
    with st.expander("📖 Explications des métriques de risque"):
        for ratio, description in risk_description.items():
            if ratio in risques.index:
                st.markdown(f"*{ratio}*: {description}")

## Section 3 : Analyse Factorielle  -----------------------------------------------------------
    st.subheader('Principal Component Analysis')
    factorial_analysis = FactorialAnalysis(fund, factors)
    x_test, y_test, pca_loadings, feature_names, explained_variance = factorial_analysis.ACP()

    pca_df = pd.DataFrame(x_test, columns=['PC1', 'PC2'])
    pca_df['Target Daily Returns'] = pd.Series(y_test).reset_index(drop=True)
    
    fig_acp = px.scatter(pca_df, x='PC1', y='PC2', color='Target Daily Returns')
    
    fig_acp.update_layout(
        xaxis_title = f"PC1: {explained_variance[0]*100:.2f}% variance",
        yaxis_title = f"PC2: {explained_variance[1]*100:.2f}% variance",
        legend=dict(orientation='h', x=0.5,  xanchor='center',y=-0.2  )
    )
    
    scaling_factor = 3 # pour agrandir un peu les vecteurs sur le plot
    colors = cycle(px.colors.qualitative.Plotly)  
    for i, feature in enumerate(feature_names): # visualisation vecteurs des facteurs
        color = next(colors) 
        fig_acp.add_trace(go.Scatter(x=[0, pca_loadings[0, i]* scaling_factor], 
                                     y=[0, pca_loadings[1, i]* scaling_factor],
                                    mode='lines',
                                    name=feature,
                                    line=dict(color=color, width=3),
                                    text=[feature]))

    st.plotly_chart(fig_acp)

    # Explications de l'Analyse Factorielle (ACP) 
    with st.expander("📖 Explications de l'Analyse Factorielle (ACP)"):
        st.markdown("""
            ### *Qu'est-ce que l'ACP ?*
            L'Analyse en Composantes Principales (ACP) est une méthode statistique utilisée pour réduire la dimensionnalité des données tout en conservant l'essentiel de l'information. Elle permet d'identifier les combinaisons linéaires des facteurs de performance qui expliquent le mieux la variance des rendements des fonds.

            ### *Interprétation des Résultats*
            - *Variance Expliquée* : Chaque composante principale (PC1, PC2, etc.) explique une portion de la variance totale des données. Par exemple, *PC1* pourrait expliquer 60% de la variance, tandis que *PC2* en explique 25%.
            - *Charges des Composantes* : Les charges indiquent l'importance de chaque facteur dans une composante. Des charges élevées (positives ou négatives) signifient que le facteur a une influence significative sur la composante.
            - *Visualisation des Fonds* : Dans le graphique ACP, chaque point représente un fonds projeté dans l'espace des deux premières composantes principales. Cela permet de visualiser les similarités et différences entre les fonds en fonction des facteurs de performance.

            ### *Comment utiliser ces informations ?*
            - *Identifier les Facteurs Clés* : Comprenez quels facteurs influencent le plus les rendements des fonds.
            - *Comparer les Fonds* : Visualisez comment différents fonds se positionnent par rapport aux facteurs principaux, facilitant ainsi la comparaison et la prise de décision.
            - *Optimisation de Portefeuille* : Utilisez les informations de l'ACP pour diversifier ou optimiser votre portefeuille en fonction des facteurs de risque et de performance identifiés.
        """) 

if __name__ == '__main__':
    main()