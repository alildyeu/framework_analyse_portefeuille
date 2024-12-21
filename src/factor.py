class Factor():
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.us = self.value[['Date',f'{name} US']]
        self.monde = self.value[['Date',f'{name} Global']]