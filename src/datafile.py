import pandas as pd

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
        self.data = self.load_data()

    def load_data(self):
        """Cette méthode charge le fichier sélectionné dans un dataframe. Pour ce faire, elle fait appel à trois autres méthodes : import_data(), filter_columns() et clean_data().Elle retourne donc un dataframe, enregistré dans self.data."""
        
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
        data_filtered = data_filtered.sort_values('Date').reset_index(drop=True)
        return data_filtered