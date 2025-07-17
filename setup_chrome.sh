#!/bin/bash

# Script d'installation Chrome + webdriver-manager pour GitHub Codespaces
# Version simple et fiable

echo "🚀 Setup Chrome avec webdriver-manager..."

# Fonctions d'affichage
print_status() {
    echo -e "\033[1;32m✅ $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m❌ $1\033[0m"
}

print_info() {
    echo -e "\033[1;34mℹ️  $1\033[0m"
}

# Mise à jour du système
print_info "Mise à jour des packages..."
sudo apt-get update -qq

# Installation des dépendances
print_info "Installation des dépendances..."
sudo apt-get install -y wget gnupg unzip

# Ajout de la clé et du repository Google Chrome
print_info "Configuration du repository Google Chrome..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | \
sudo gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | \
sudo tee /etc/apt/sources.list.d/google.list > /dev/null

# Mise à jour avec le nouveau repository
print_info "Mise à jour avec Google repository..."
sudo apt-get update -qq

# Installation de Google Chrome
print_info "Installation de Google Chrome..."
sudo apt-get install -y google-chrome-stable

if [ $? -eq 0 ]; then
    print_status "Google Chrome installé"
    google-chrome --version
else
    print_error "Erreur lors de l'installation de Chrome"
    exit 1
fi

# Installation des packages Python
print_info "Installation des packages Python..."
pip install selenium webdriver-manager python-dotenv

if [ $? -eq 0 ]; then
    print_status "Packages Python installés"
else
    print_error "Erreur lors de l'installation des packages Python"
    exit 1
fi

# Test de l'installation
print_info "Test de l'installation..."
python3 -c "
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

try:
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://www.google.com')
    title = driver.title
    driver.quit()
    print(f'✅ Test réussi! Titre: {title}')
except Exception as e:
    print(f'❌ Erreur test: {e}')
"

echo ""
print_status "🎉 Installation terminée!"
echo ""
print_info "Versions installées:"
google-chrome --version
python3 -c "import selenium; print(f'Selenium: {selenium.__version__}')"
python3 -c "import webdriver_manager; print(f'webdriver-manager: {webdriver_manager.__version__}')"

echo ""
print_info "✨ Avantages de webdriver-manager:"
echo "   - Télécharge automatiquement la bonne version de ChromeDriver"
echo "   - Plus de problème de compatibilité Chrome/ChromeDriver"
echo "   - Gestion automatique des mises à jour"

echo ""
print_info "🚀 Prêt pour le développement!"
echo "   Vous pouvez maintenant créer votre script Python"
