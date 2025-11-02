# module/fichierB.py

from moduletest.fichierA import Animal

class Dog(Animal):
    def parler(self):
        return f"{self.nom} aboie !"


# Exemple d'utilisation
if __name__ == "__main__":
    rex = Dog("Rex")
    print(rex.parler())  # affichera: "Rex aboie !"