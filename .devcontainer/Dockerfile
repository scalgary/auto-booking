FROM mcr.microsoft.com/devcontainers/python:3.11

# Installer les dépendances système
RUN apt-get update -qq && \
    apt-get install -y wget gnupg unzip && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | \
    gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update -qq && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

    # copier fichier requirement
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt 
# Installer les packages Python nécessaires
#RUN pip install --no-cache-dir selenium webdriver-manager python-dotenv pillow

# (Optionnel) Tester l'installation
RUN python3 -c "from selenium import webdriver; from webdriver_manager.chrome import ChromeDriverManager; from selenium.webdriver.chrome.service import Service; from selenium.webdriver.chrome.options import Options; options = Options(); options.add_argument('--headless'); options.add_argument('--no-sandbox'); options.add_argument('--disable-dev-shm-usage'); service = Service(ChromeDriverManager().install()); driver = webdriver.Chrome(service=service, options=options); driver.get('https://www.google.com'); print('✅ Test réussi! Titre:', driver.title); driver.quit()"