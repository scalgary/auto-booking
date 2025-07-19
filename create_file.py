#!/usr/bin/env python3

# Script qui crée un fichier
def create_file():
    content = """Fichier créé par Python !
Date de création: maintenant
Contenu: Hello from Python script!"""
    
    with open('output.txt', 'w') as f:
        f.write(content)
    
    print("Fichier 'output.txt' créé avec succès !")

if __name__ == "__main__":
    create_file()