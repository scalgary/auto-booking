# main.py

from module.fichierA import Animal
from module.fichierB import Dog

def main():
    # Exemple avec Animal
    chat = Animal("Chaton")
    print(chat.parler())  # Chaton fait un bruit.

    # Exemple avec Dog
    rex = Dog("Rex")
    print(rex.parler())   # Rex aboie !

if __name__ == "__main__":
    main()