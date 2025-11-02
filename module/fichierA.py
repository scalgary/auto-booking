# module/fichierA.py

class Animal:
    def __init__(self, nom):
        self.nom = nom

    def parler(self):
        return f"{self.nom} fait un bruit."