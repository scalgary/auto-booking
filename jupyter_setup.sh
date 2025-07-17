#!/bin/bash

# Script d'installation et configuration Jupyter pour GitHub Codespaces
echo "🚀 Installation de Jupyter Lab..."

# Fonction pour afficher les messages avec couleurs
print_status() {
    echo -e "\033[1;32m✅ $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m❌ $1\033[0m"
}

print_info() {
    echo -e "\033[1;34mℹ️  $1\033[0m"
}

print_info "Installation de Jupyter Lab et extensions..."
pip install jupyterlab notebook ipykernel selenium python-dotenv

if [ $? -eq 0 ]; then
    print_status "Jupyter installé"
else
    print_error "Erreur lors de l'installation"
    exit 1
fi

print_info "Configuration du kernel Python..."
python -m ipykernel install --user --name=python3 --display-name "Python 3"

print_info "Création du dossier notebooks..."
mkdir -p notebooks

print_info "Création d'un notebook de démonstration..."
cat > notebooks/demo_login.ipynb << 'EOF'
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Auto Login Bot - Demo\n",
    "\n",
    "Ce notebook montre comment utiliser notre bot de connexion automatique."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Installation des dépendances (si nécessaire)\n",
    "!pip install selenium python-dotenv"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Import des librairies\n",
    "from selenium import webdriver\n",
    "from selenium.webdriver.chrome.options import Options\n",
    "from selenium.webdriver.chrome.service import Service\n",
    "from selenium.webdriver.common.by import By\n",
    "import time\n",
    "import os\n",
    "from dotenv import load_dotenv\n",
    "\n",
    "print(\"✅ Librairies importées\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Configuration (modifiez selon vos besoins)\n",
    "EMAIL = \"votre_email@example.com\"\n",
    "PASSWORD = \"votre_password\"\n",
    "WEBSITE_URL = \"https://votre-site.com\"\n",
    "\n",
    "print(f\"📧 Email: {EMAIL}\")\n",
    "print(f\"🌐 Site: {WEBSITE_URL}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Configuration Chrome pour Codespaces\n",
    "def setup_chrome():\n",
    "    options = Options()\n",
    "    options.add_argument('--headless')\n",
    "    options.add_argument('--no-sandbox')\n",
    "    options.add_argument('--disable-dev-shm-usage')\n",
    "    options.add_argument('--disable-gpu')\n",
    "    \n",
    "    service = Service('/usr/local/bin/chromedriver')\n",
    "    driver = webdriver.Chrome(service=service, options=options)\n",
    "    return driver\n",
    "\n",
    "print(\"✅ Configuration Chrome prête\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Test de connexion\n",
    "print(\"🚀 Test de connexion...\")\n",
    "\n",
    "driver = setup_chrome()\n",
    "\n",
    "try:\n",
    "    # Aller sur le site\n",
    "    driver.get(WEBSITE_URL)\n",
    "    print(f\"📄 Titre: {driver.title}\")\n",
    "    print(f\"🔗 URL: {driver.current_url}\")\n",
    "    \n",
    "    # Ici vous pouvez ajouter votre logique de connexion\n",
    "    \n",
    "    print(\"✅ Test terminé\")\n",
    "    \n",
    "except Exception as e:\n",
    "    print(f\"❌ Erreur: {e}\")\n",
    "    \n",
    "finally:\n",
    "    driver.quit()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
EOF

print_status "Notebook de démonstration créé"

print_info "Génération du script de lancement..."
cat > start_jupyter.sh << 'EOF'
#!/bin/bash
echo "🚀 Lancement de Jupyter Lab..."
echo "🔗 Jupyter sera accessible via l'onglet PORTS de Codespaces"
echo "📝 Notebooks disponibles dans le dossier 'notebooks/'"
echo ""
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --notebook-dir=notebooks
EOF

chmod +x start_jupyter.sh

print_status "Script de lancement créé: ./start_jupyter.sh"

echo ""
print_status "🎉 Installation terminée!"
echo ""
print_info "Pour démarrer Jupyter Lab:"
echo "   ./start_jupyter.sh"
echo ""
print_info "Ou directement:"
echo "   jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root"
echo ""
print_info "📁 Vos notebooks seront dans le dossier 'notebooks/'"
print_info "🌐 Accès via l'onglet PORTS de Codespaces (port 8888)"