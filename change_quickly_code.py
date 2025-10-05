# -*- coding: utf-8 -*-
input_file = ".github/workflows/sunday_registration.yml"
output_file = ".github/workflows/registration.yml"


# Lire le contenu du fichier YAML
with open(input_file, "r", encoding="utf-8") as f:
    contenu = f.read()

# Remplacer Sunday et sunday
contenu_modifie = contenu.replace("Sunday", "Monday").replace("sunday", "monday")

# Sauvegarder le nouveau contenu dans un autre fichier
with open(output_file, "w", encoding="utf-8") as f:
    f.write(contenu_modifie)

print(f"✅ Fichier modifié sauvegardé sous le nom : {output_file}")