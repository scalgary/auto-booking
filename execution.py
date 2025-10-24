from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os

time_sleep=1
import sys

# Get arguments from command line or environment variables
if len(sys.argv) != 4:
    print("Usage: python mon_script.py <variable1> <variable2> <variable3>")
    #sys.exit(1)
import sys

# Valeurs par défaut
DEFAULT_DATE = "19-Aug-25"
DEFAULT_TIME = "4:30"
DEFAULT_LEVEL = "Intermediate"

# Récupérer arguments ou utiliser défauts
TARGET_DATE = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATE
TARGET_TIME = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TIME
COURSE_LEVEL = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_LEVEL

print(f"📅 Date: {TARGET_DATE}")
print(f"🕐 Time: {TARGET_TIME}")
print(f"🎾 Level: {COURSE_LEVEL}")


#load_dotenv()  # Charge le fichier .env when running in codespace

email = os.getenv('YOUR_SECRET_EMAIL')
password = os.getenv('YOUR_SECRET_PASSWORD')
logon_url = os.getenv("YOUR_SECRET_LOGON_URL")
planning_url = os.getenv('YOUR_SECRET_PLANNING_URL')
login_url = os.getenv('YOUR_SECRET_LOGIN_URL')
my_name = os.getenv('YOUR_SECRET_MY_NAME')

print("=== STATUS DES AUTRES SECRETS (MASQUÉS) ===")
print(f"EMAIL: {'✅ DÉFINI' if email else '❌ MISSING'}")
print(f"PASSWORD: {'✅ DÉFINI' if password else '❌ MISSING'}")
print(f"MY_NAME: {'✅ DÉFINI' if my_name else '❌ MISSING'}")
print()
if not all([email, password, logon_url, planning_url, login_url, my_name]):
    print("❌ ERREUR: UN OU PLUSIEURS SECRETS SONT MANQUANTS. VÉRIFIEZ VOS VARIABLES D'ENVIRONNEMENT.")
    print("=== STATUS DES AUTRES SECRETS (MASQUÉS) ===")
    for var in [email, password, logon_url, planning_url, login_url, my_name]:
            if not var:
                print(f"{var} ❌ MISSING'")
    sys.exit(1)
import time
#from PIL import Image
import io

def take_full_page_screenshot(driver, filename):
    # Obtenir la taille de la fenêtre
    window_size = driver.get_window_size()
    
    # Obtenir la hauteur totale de la page
    total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
    
    # Redimensionner pour capturer toute la page
    driver.set_window_size(window_size['width'], total_height)
    
    # Attendre que la page se charge complètement
    time.sleep(2)
    
    # Prendre la capture d'écran
    driver.save_screenshot(filename)
    
    # Remettre la taille originale
    driver.set_window_size(window_size['width'], window_size['height'])

from datetime import datetime, timedelta

def check_date(target_date):

    # Parse the date string
    your_date = datetime.strptime(target_date, "%d-%b-%y")

    # Get today's date
    today = datetime.now()

    # Check if your date is after today
    is_after_today = your_date > today

    # Calculate the difference in days
    difference = your_date - today
    days_difference = difference.days

    # Check if exactly 7 days difference
    next_week = days_difference == 6
    less_7_days = days_difference <=6
    possible = is_after_today & less_7_days


    print(f"Your date: {your_date.strftime('%Y-%m-%d')}")
    print(f"Today: {today.strftime('%Y-%m-%d')}")
    print(f"Is after today: {is_after_today}")
    print(f"Days difference: {days_difference}")
    return possible, next_week



def access_login(website_url, email_login, secret_password):
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
    return driver

def check_basket(driver,login_url):
    # Look up if basket is empty
    if driver.current_url == login_url:
        is_empty = driver.execute_script("return document.querySelector('span.basket-badge').textContent;") == "0"
        return is_empty
    else:
         print("not login")
    
def click_for_me(driver, target_date, my_name):
    moi_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{my_name}')]")
    # Chercher un bouton près de moi
    for i, moi_element in enumerate(moi_elements):

        # Chercher dans le conteneur parent
        parent = moi_element.find_element(By.XPATH, "./..")
        
        # Chercher des boutons de réservation
        moi_buttons = parent.find_elements(By.XPATH, ".//*[contains(text(), 'Book') or contains(text(), 'Réserver') or contains(text(), 'Select') or contains(text(), 'Choose')]")
        
        if moi_buttons:
            moi_button = moi_buttons[0]
            
            print(f"✅ Bouton trouvé près de Moi: '{moi_button.text.strip()}'")
            print(f"🖱️ Clic pour réserver pour Moi...")

            moi_button.click()
                        
            print("✅ Réservation Moi cliquée!")
            time.sleep(time_sleep)
                        
                        # Screenshot final
            driver.save_screenshot(f"7_before_basket_{target_date.replace('-', '_')}.png")
            print(f"📸 Screenshot final: reservation_moi_{target_date.replace('-', '_')}.png")
            return True
    return False
def look_for_slots(driver, target_date, target_level, target_time):
    print("🔍 Recherche de boutons avec données de cours...")

    # Chercher tous les boutons avec data-class-time (structure de votre site)
    course_buttons = driver.find_elements(By.XPATH, "//button[@data-class-time]")

    print(f"📋 {len(course_buttons)} bouton(s) de cours trouvé(s)")

    found_slots = None

    for i, button in enumerate(course_buttons):
        
            # Extraire les données du bouton
            class_name = button.get_attribute('data-class-name') or ''
            class_date = button.get_attribute('data-class-date') or ''
            class_time = button.get_attribute('data-class-time') or ''
            class_spaces = button.get_attribute('data-class-spaces') or '0'
            class_location = button.get_attribute('data-class-location') or ''
            class_venue = button.get_attribute('data-class-venue') or ''
            
            #print(f"\n  Cours {i+1}:")
            #print(f"    Nom: {class_name}")
            #print(f"    Date: {class_date}")
            #print(f"    Heure: {class_time}")
            #print(f"    Places: {class_spaces}")
            
            # Vérifier si c'est le bon jour ET contient 6:30 PM
            date_match = target_date in class_date
            level_match = target_level in class_name
            time_match = target_time in class_time.split("-")[0] or target_time.lstrip() in class_time.split("-")[0]
            
            if date_match:
                 pass
                #print(f"    Heure: {class_time}")
                #print(f"    Nom: {class_name}")
                #print(f"    Date: {class_date}")
                #print(f"    Heure: {class_time}")
                #print(f"    Places: {class_spaces}")
            
            if date_match and time_match and level_match:
                print(f"    ✅ CORRESPONDANCE TROUVÉE!")
                spaces_available = int(class_spaces)
                print(spaces_available)
                #driver.save_screenshot("7_find_date_planning.png")
                slot_info = {
                            'button': button,
                            'class_name': class_name,
                            'class_date': class_date,
                            'class_time': class_time,
                            'class_spaces': spaces_available,
                            'class_location': class_location,
                            'class_venue': class_venue,
                            'available': spaces_available > 0
                        }
                        
                found_slots = slot_info
                        
                if spaces_available > 0:
                    print(f"    ✅ DISPONIBLE - {spaces_available} place(s)")
                    
                else:
                    print(f"    ❌ COMPLET - 0 place")
                break
    if found_slots == None:
        print(f"    ❌ NO CORRESPONDANCE TROUVÉE!")
    return found_slots
            

def click_confirm_basket(driver):
    basket = driver.find_elements(By.XPATH, "//*[contains(text(), 'Checkout')]")
    if basket:
        basket[0].click()
        time.sleep(time_sleep)
        driver.save_screenshot(f"8_after_basket_{TARGET_DATE.replace('-', '_')}.png")
        return True
    return False
                
def click_on_slot(driver, slot_available):
    info_button = slot_available['button']
    parent = info_button.find_element(By.XPATH, "./..")
    book_buttons = parent.find_elements(By.XPATH, ".//*[contains(text(), 'Book Now') or contains(text(), 'Book')]")
    if book_buttons:
        print(f"✅ Bouton 'Book Now' trouvé dans le même conteneur")
        book_buttons[0].click()
        time.sleep(time_sleep)
        #driver.save_screenshot("6_click_on_slot.png")
        return True
    return False


driver = access_login(logon_url, email, password) # navigate after login
possible_to_book, next_week_booking = check_date(TARGET_DATE)

success = False
if possible_to_book:
    if check_basket(driver, login_url): #check empty basket
        driver.get(planning_url) #go to planning after login
       
        if next_week_booking:
            next_week_btn = driver.find_element(By.XPATH, "//input[@value='Next Week']")
            next_week_btn.click()
        time.sleep(time_sleep)  # Attendre le chargement
        # Screenshot
        #driver.save_screenshot("5_planning_page.png")
        print("📸 Screenshot: planning_page.png")
        slot_available = look_for_slots(driver, TARGET_DATE, COURSE_LEVEL, TARGET_TIME)
        if slot_available:
            if click_on_slot(driver, slot_available):
                if click_for_me(driver, TARGET_DATE, my_name):
                    click_confirm_basket(driver)
                    success = True

driver.quit()

if success:
    sys.exit(0)  # Success
else:
    sys.exit(1)