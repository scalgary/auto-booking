from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

import sys





email = os.getenv('YOUR_SECRET_EMAIL')
password = os.getenv('YOUR_SECRET_PASSWORD')
logon_url = os.getenv("YOUR_SECRET_LOGON_URL")
planning_url = os.getenv('YOUR_SECRET_PLANNING_URL')
login_url = os.getenv('YOUR_SECRET_LOGIN_URL')
my_name = os.getenv('YOUR_SECRET_MY_NAME')

website_appointment =os.getenv("YOUR_SECRET_APPOINTMENT")
email_from = os.environ.get('EMAIL_FROM')
email_to = os.environ.get('EMAIL_TO')
email_password = os.environ.get('EMAIL_PASSWORD')
smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
smtp_port = int(os.environ.get('SMTP_PORT', '587'))


print("=== STATUS DES AUTRES SECRETS (MASQUÉS) ===")
print(f"EMAIL: {'✅ DÉFINI' if email else '❌ MISSING'}")
print(f"PASSWORD: {'✅ DÉFINI' if password else '❌ MISSING'}")
print(f"MY_NAME: {'✅ DÉFINI' if my_name else '❌ MISSING'}")
print(f"website_appointment: {'✅ DÉFINI' if website_appointment else '❌ MISSING'}")
print(f"logon_url: {'✅ DÉFINI' if logon_url else '❌ MISSING'}")

print()



def access_login(website_url, email_login, secret_password, website_appointment):
    """Script simple : saisir email + password et prendre screenshots"""

    print("🚀 Script simple - Email + Password + Screenshots")
    print("=" * 50)
    #print(f"🌐 Site: {website_url}")
    #print(f"📧 Email: {email}")
    print("🔑 Password: ****")
    print()

    # Configuration
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')

    # Driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

        # Si vous avez déjà un driver ouvert
    driver.set_window_size(1920, 1080)
    driver.maximize_window()

    # Ou définir une taille spécifique
    driver.set_window_size(1400, 900)

    # Rafraîchir la page pour que les changements prennent effet
    driver.refresh()

    # Étape 1: Aller sur le site
    print("🌐 Connexion au site...")
    driver.get(website_url)
    time.sleep(3)
    print(f"📄 Titre: {driver.title}")
    # Screenshot avant
    #driver.save_screenshot("1_avant_saisie.png")
    print("📸 Screenshot 1: 1_avant_saisie.png")
    email_field = driver.find_element(By.XPATH, "//input[@type='email']")
    ("✅ Champ email trouvé par type='email'")
    email_field
    if email_field:
            print("📝 Saisie de l'email...")
            email_field.clear()
            email_field.send_keys(email_login)
            #(f"✅ Email saisi: {email_login}")
            time.sleep(1)

    # Screenshot après email
    #driver.save_screenshot("2_apres_email.png")
    print("📸 Screenshot 2: 2_apres_email.png")
    # Étape 3: Trouver et remplir le champ password
    print("🔑 Recherche du champ Password...")

    password_field = None

    password_field = driver.find_element(By.XPATH, "//input[@type='password']")
    print("✅ Champ password trouvé par type='password'")


    if password_field:
        print("📝 Saisie du password...")
        password_field.clear()
        password_field.send_keys(secret_password)
        print("✅ Password saisi")
        time.sleep(1)

        # Screenshot après password
    #driver.save_screenshot("3_apres_password.png")
    print("📸 Screenshot 3: 3_apres_password.png")

    login_button = None
    login_button = driver.find_element(By.XPATH, "//input[@value='Login']")

    login_button.click()
    print("✅ Bouton cliqué!")

    # Étape 6: Attendre la redirection et vérifier
    print("⏳ Attente de la redirection...")
    time.sleep(5)

    # Screenshot après connexion
    #driver.save_screenshot("4_apres_clic.png")
    print("📸 Screenshot 4: 4_apres_clic.png")
    #print(driver.current_url)
    
    driver.get(website_appointment)
    time.sleep(5)

  # Screenshot après connexion
    #driver.save_screenshot("5_appoint.png")
    print("📸 Screenshot 5: 5_appot.png")
    #print(driver.current_url)
    return driver
def parse_date(date_str, year=2025):
    """Parse date string like 'Mon\n13\nOct' to datetime object"""
    parts = [p.strip() for p in date_str.split('\n') if p.strip()]
    
    if len(parts) < 3:
        return None
    
    month_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    
    try:
        month_num = month_map.get(parts[2], 1)
        return datetime(year, month_num, int(parts[1]))
    except (ValueError, TypeError):
        return None
def get_tomorrow_appointments(appointments, precision=1):
    """Find appointments for tomorrow"""
    tomorrow = (datetime.now() + timedelta(days=precision)).date()
    
    tomorrow_appointments = []
    for apt in appointments:
        apt_datetime = parse_date(apt['date'])
        if apt_datetime and apt_datetime.date() == tomorrow:
            tomorrow_appointments.append(apt)
    
    return tomorrow_appointments
def send_email(appointments):
    """Send email reminder"""
    email_from = os.environ.get('EMAIL_FROM')
    email_to = os.environ.get('EMAIL_TO')
    email_password = os.environ.get('EMAIL_PASSWORD')
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    
    if not all([email_from, email_to, email_password]):
        print("❌ Email configuration missing")
        return False
    
    subject = f"🎾 Gym Appointment Reminder - {len(appointments)} appointment(s) tomorrow"
    
    body = "Hello!\n\n"
    body += f"You have {len(appointments)} appointment(s) scheduled for tomorrow:\n\n"
    
    for idx, apt in enumerate(appointments, 1):
        date_clean = apt['date'].replace('\n', ' ')
        time_clean = apt['time'].replace('\n', ' ')
        body += f"{idx}. {date_clean} at {time_clean}\n"
    
    body += "\n📍 Location: Calgary JCC\n"
    body += "\nDon't forget your pickleball gear! 🏓"
    
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_from, email_password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email sent to {email_to}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

driver= access_login(logon_url, email, password, website_appointment)

# Attendez d'être sur la page, puis exécutez:
rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr.align-middle")

appointments = []
for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    if len(cells) >= 2:
        appointments.append({
            "date": cells[0].text,
            "time": cells[1].text
        })

# Sauvegarder
with open('appointments.json', 'w', encoding='utf-8') as f:
    json.dump(appointments, f, indent=2)

print(f"✓ {len(appointments)} appointments saved!")
#print(json.dumps(appointments, indent=2))

driver.quit()
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def load_appointments(filename='appointments.json'):
    """Load appointments from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            appointments = json.load(f)
            print(f"✓ Loaded {len(appointments)} appointments")
            return appointments
    except FileNotFoundError:
        print(f"❌ File {filename} not found")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return []


def send_all_appointments_email(appointments):
    """Send email with ALL appointments"""
    email_from = os.environ.get('EMAIL_FROM')
    email_to = os.environ.get('EMAIL_TO')
    email_password = os.environ.get('EMAIL_PASSWORD')
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    
    if not all([email_from, email_to, email_password]):
        print("❌ Email configuration missing")
        return False
    
    # Email subject

    subject = f"🏓 Your Pickleball Appointments - {len(appointments)} total"
    
    # Email body
    body = "Hello!\n\n"
    body += f"Here are all your scheduled pickleball appointments ({len(appointments)} total):\n\n"
    
    for idx, apt in enumerate(appointments, 1):
        date_clean = apt['date'].replace('\n', ' ')
        time_clean = apt['time'].replace('\n', ' ')
        body += f"{idx}. {date_clean} at {time_clean}\n"
    
    body += "\n📍 Location: Calgary JCC\n"
    body += "\nSee you on the court! 🏓\n"
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    try:
        print(f"📧 Connecting to {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        print(f"🔐 Logging in...")
        server.login(email_from, email_password)
        print(f"📤 Sending email...")
        server.send_message(msg)
        server.quit()
        print(f"✅ Email sent to {email_to}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False



def main():

    if not appointments:
        print("ℹ️ No appointments found")
        return
    
    #tomorrow_appointments = get_tomorrow_appointments(appointments,1)
    
    #if tomorrow_appointments:
        #print(f"🎯 Found {len(tomorrow_appointments)} appointment(s) for tomorrow")
        #send_email(tomorrow_appointments)
    #else:
        #print("ℹ️ No appointments for tomorrow")
    print(f"\n📅 Appointments to send:")
    for idx, apt in enumerate(appointments, 1):
        date = apt['date'].replace('\n', ' ')
        time = apt['time'].replace('\n', ' ')
        print(f"  {idx}. {date} - {time}")
    
    # Send email
    print()
    if send_all_appointments_email(appointments):
        print("\n✅ Email sent successfully!")
    else:
        print("\n❌ Failed to send email")



main()




