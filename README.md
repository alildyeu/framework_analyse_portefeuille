# Framework analysis portfolio

## Setup

``` bash
pip install -r requirements.txt
```

## How to run

In a terminal type

``` bash
streamlit run main.py
```

## 1. Fiches d'identités des fonds étudiés

### JPM America Equity C (Acc)
- ISIN : LU0129459060
- Société de gestion : JPM AM
- Actifs : Actions
- Market Cap : Large Cap
- Géographie : US
- Devise : US$ 

### Schroder International Selection Fund Global Sustainable Growth C Acc
- ISIN : LU0557290854
- Société de gestion : Schroder
- Actifs : Actions
- Market Cap : Large & Mid cap
- Géographie : Monde
- Devise : US$ 

### AQR Large Cap Multi-Style Fund
- ISIN : US00203H4956
- Société de gestion : AQR Funds
- Actif : Actions
- Market Cap : Large cap
- Géographie : US
- Devise : US$ 

## 2. Sélection des données

### a. Fonds : choix de parts
Pour le fonds AQR Large Cap Multi-Style, trois parts sont présentes dans le fichiers :  
- La **part I** : pour les investisseurs institutionnels. Pour ce fonds et cette part, le minimum d'investissement est à 5 millions $.
- La **part N** : pour les investisseurs institutionnels et privés. Pour ce fonds et cette part, le minimum d'investissement est à 2500$.
- La **part R6** : pour les plans de retraites. Pour ce fonds et cette part, le minimum d'investissement est à 50 millions $.

Source : [AQR](https://funds.aqr.com/funds/equities/aqr-large-cap-multi-style-fund/qcenx#about)

- Les fonds JPM et Schroder étudiés présentant la **part C**, nous nous sommes concentrées sur la **part N**, qui nous semble plus **similaire** et donc plus pertinente dans nos exercices comparatifs. 

### b. Facteurs de performance : choix de fréquence et de régions

Les facteurs de performances recensés par AQR sont accessible avec les caractéristiques suivantes:
- Sur une fréquence quotidienne et mensuelle.
- Sur un ensemble de pays et régions.

Afin d'avoir des données alignées avec celles des fonds étudiés, nous nous sommes concentrées sur les **données journalières** et sur les régions **US et Monde**.