import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

from src.fund import Fund

class FactorialAnalysis():
    def __init__(self, fund, factors_dict):
        self.fund: Fund = fund
        self.factors_dict: dict = factors_dict
        self.df = self.build_dataset()
        self.y = self.df[f'{self.fund.name}']
        self.x = self.df.filter(like=f'{self.fund.region}') #selectionne les facteurs de la region appropriée

    def build_dataset(self):
        all_factors = pd.DataFrame()
        for factor_name, factor in self.factors_dict.items():
            if all_factors.empty:
                all_factors = factor.value
            else:
                all_factors = pd.merge(all_factors, factor.value, on='Date', how='inner')
        
        full_dataset =  pd.merge(self.fund.rdments, all_factors, on='Date', how='inner').dropna()
        return full_dataset
    
    def ACP(self):
        x_train, x_test, y_train, y_test = self.divide_train_test()
        x_train, x_test = self.normalize_data(x_train, x_test)

        pca = PCA(n_components = 2)
        x_train = pca.fit_transform(x_train)
        x_test = pca.transform(x_test)
        
        explained_variance = pca.explained_variance_ratio_ #variance expliquée par chaque composante principale
        pca_loadings = pca.components_
        feature_names = self.x.columns

        regressor = LinearRegression()
        regressor.fit(x_train, y_train)

        return x_test, y_test, pca_loadings, feature_names, explained_variance
    
    def divide_train_test(self):
        return train_test_split(self.x, self.y, test_size=0.2, random_state=0)
    
    def normalize_data(self, train, test):
        sc = StandardScaler()
        train = sc.fit_transform(train)
        test = sc.transform(test)
        return train, test


