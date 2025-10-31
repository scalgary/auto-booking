import logging
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from datetime import datetime, date, timedelta
import json
import logging
import os

from caldav import DAVClient
from dotenv import load_dotenv
import icalendar
import sys



# Configuration simple
CALDAV_USER = os.getenv("CALDAV_USER")
CALDAV_PASSWORD = os.getenv("CALDAV_PASSWORD")
CALDAV_URL = 'https://caldav.icloud.com'
CALENDAR_NAME = "Family"
SEARCH_TERMS = ['🏓', '🎾']

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

# Configuration simple
CALDAV_USER = os.getenv("CALDAV_USER")
CALDAV_PASSWORD = os.getenv("CALDAV_PASSWORD")
CALDAV_URL = 'https://caldav.icloud.com'
CALENDAR_NAME = "Family"
SEARCH_TERMS = ['🏓', '🎾']


# Configure logger
def setup_logger(debug_mode=False):
    level = logging.DEBUG if debug_mode else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)  # Print to console
        ]
    )
    return logging.getLogger(__name__)


# Initialize logger
DEBUG = False  # Set to False in production
logger = setup_logger(debug_mode=DEBUG)
time_sleep=5


# Vérification des secrets
logger.info("=== STATUS DES AUTRES SECRETS (MASQUÉS) ===")
logger.info(f"EMAIL: {'✅ DÉFINI' if email else '❌ MISSING'}")
logger.info(f"PASSWORD: {'✅ DÉFINI' if password else '❌ MISSING'}")
logger.info(f"MY_NAME: {'✅ DÉFINI' if my_name else '❌ MISSING'}")
logger.info(f"LOGON_URL: {'✅ DÉFINI' if logon_url else '❌ MISSING'}")
logger.info(f"PLANNING_URL: {'✅ DÉFINI' if planning_url else '❌ MISSING'}")
logger.info(f"LOGIN_URL: {'✅ DÉFINI' if login_url else '❌ MISSING'}")
logger.info(f"website_appointment: {'✅ DÉFINI' if website_appointment else '❌ MISSING'}")
logger.info(f"email_from: {'✅ DÉFINI' if email_from else '❌ MISSING'}")
logger.info(f"email_to: {'✅ DÉFINI' if email_to else '❌ MISSING'}")
logger.info(f"email_password: {'✅ DÉFINI' if email_password else '❌ MISSING'}")
logger.info(f"CALDAV_USER: {'✅ DÉFINI' if CALDAV_USER else '❌ MISSING'}")
logger.info(f"CALDAV_PASSWORD: {'✅ DÉFINI' if CALDAV_PASSWORD else '❌ MISSING'}")


# Vérification complète
secrets_dict = {
    "EMAIL": email,
    "PASSWORD": password,
    "MY_NAME": my_name,
    "LOGON_URL": logon_url,
    "PLANNING_URL": planning_url,
    "LOGIN_URL": login_url,
    "website_appointment": website_appointment,
    "email_to":email_to,
    "email_from":email_from,
    "email_password":email_password,
    "CALDAV_USER":CALDAV_USER,
    "CALDAV_PASSWORD":CALDAV_PASSWORD
}

missing_secrets = [name for name, value in secrets_dict.items() if not value]

if missing_secrets:
    logger.error("❌ ERREUR: UN OU PLUSIEURS SECRETS SONT MANQUANTS")
    logger.error("=== SECRETS MANQUANTS ===")
    for secret_name in missing_secrets:
        logger.error(f"{secret_name}: ❌ MISSING")
    logger.critical("ARRÊT DU PROGRAMME - VÉRIFIEZ VOS VARIABLES D'ENVIRONNEMENT")
    sys.exit(1)
else:
    logger.info("✅ TOUS LES SECRETS SONT DÉFINIS")
    logger.debug("Poursuite de l'exécution...")


class SecureWebLogin:
    """Classe pour gérer le login sécurisé avec driver comme objet"""
    
    def __init__(self, website_url, email_login, secret_password):
        self.website_url = website_url
        self.email_login = email_login
        self.secret_password = secret_password
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self):
        """Initialise le driver Chrome"""
        logger.debug("Initialisation du driver Chrome...")
        # Configuration
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        
        # Driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Si vous avez déjà un driver ouvert
        #self.driver.set_window_size(1920, 1080)
        #self.driver.maximize_window()
        # Ou définir une taille spécifique

        logger.debug("Driver configuré avec succès")
    
    def login(self):
        """Script simple : saisir email + password et prendre screenshots"""
        logger.info("🚀 Script simple - Email + Password + Screenshots")
        logger.info(f"🌐 Site: {self.website_url}")

        self.driver.get(self.website_url)
        self.driver.set_window_size(1400, 900)
        logger.info(f"📄 Titre: {self.driver.title}")

        wait = WebDriverWait(self.driver, time_sleep)  # attend max 15s
        try:
            # 🕐 Attendre que le champ email soit présent ET visible
            email_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='email']")))
            logger.info("✅ Champ email visible, on peut continuer")

            # Remplir email
            email_field.clear()
            email_field.send_keys(self.email_login)
            logger.info("📧 Email saisi")

            # 🕐 Attendre le champ password
            password_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password']")))
            password_field.clear()
            password_field.send_keys(self.secret_password)
            logger.info("🔑 Password saisi")

            # 🕐 Attendre et cliquer sur le bouton Login
            login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Login']")))
            login_button.click()
            logger.info("✅ Bouton 'Login' cliqué")

            # 🕐 Attendre que la redirection soit terminée (ex: titre ou URL)
            wait.until(EC.url_changes(self.website_url))
            logger.info(f"🌍 Nouvelle URL : {self.driver.current_url}")

        except TimeoutException as e:
            logger.error(f"❌ Timeout pendant le login : {e}")
            raise

        return self.driver



    def go_url(self, url):
        logger.info(f"🔗 Navigation vers {url}")
        self.driver.get(url)

    
    def go_appointment(self, appointment_url=website_appointment):
        self.go_url(appointment_url)
        wait = WebDriverWait(self.driver, time_sleep)
        try:
            # 🕐 Attendre que la liste déroulante soit présente
            select_element = wait.until(EC.presence_of_element_located((By.ID, "Users")))
            select = Select(select_element)
            select.select_by_visible_text("Serge Lebon (Family Lebon, Sandrine)")

            # 🕐 Attendre que le bouton Search soit cliquable
            search_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//input[@type='submit' and @value='Search']")
            ))
            search_button.click()
            logger.debug("🔍 Bouton 'Search' cliqué")

        except TimeoutException:
            logger.error("❌ Timeout: la page appointment n’a pas chargé correctement")
            raise

        return self.driver
    
    def save_appointments_json(self):
        self.go_appointment()
        wait = WebDriverWait(self.driver, time_sleep)

        try:
            # 🕐 Attendre que le tableau soit visible
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "tbody tr.align-middle")))
            rows = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr.align-middle")
        except TimeoutException:
            logger.error("❌ Aucun rendez-vous trouvé (timeout)")
            rows = []

        appointments = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                appointments.append({
                    "date": cells[0].text,
                    "time": cells[1].text,
                    "name": cells[4].text,
                })

        with open('appointments.json', 'w', encoding='utf-8') as f:
            json.dump(appointments, f, indent=2)

        logger.info(f"✓ {len(appointments)} appointments saved!")


    def get_driver(self):
        """Retourne le driver pour utilisation externe"""
        return self.driver

    def quit(self):
        """Ferme le driver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 Driver fermé")
    
    

# Usage:
# secure_login = SecureWebLogin("https://site.com", "email@test.com", "password123")
# secure_login.login()
# 
# Utiliser le driver dans d'autres fonctions:
# driver = secure_login.driver


def load_appointments(filename='appointments.json'):
    """Load appointments from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            appointments = json.load(f)
            logger.info(f"✓ Loaded {len(appointments)} appointments")
            logger.info(f"\n📅 Appointments to send:")
            for idx, apt in enumerate(appointments, 1):
                date = apt['date'].replace('\n', ' ')
                time = apt['time'].replace('\n', ' ')
                name = apt['name'].replace('\n', ' ')


                logger.info(f"  {idx}. {date} - {time} - {name}")
    

            return appointments
    except FileNotFoundError:
        logger.error(f"❌ File {filename} not found")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON: {e}")
        return []

def send_all_appointments_email(appointments):
    """Send email with ALL appointments"""
    email_from = os.environ.get('EMAIL_FROM')
    email_to = os.environ.get('EMAIL_TO')
    email_password = os.environ.get('EMAIL_PASSWORD')
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    
    if not all([email_from, email_to, email_password]):
        logger.error("❌ Email configuration missing")
        return False
    if appointments is None:
        logger.info("no appointments")
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
        logger.info(f"📧 Connecting to {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        logger.info(f"🔐 Logging in...")
        server.login(email_from, email_password)
        logger.info(f"📤 Sending email...")
        server.send_message(msg)
        server.quit()
        logger.info(f"✅ Email sent to {email_to}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")
        return False






class PickleballCalendarManager:
    def __init__(self, calendar_name=CALENDAR_NAME):
        if not CALDAV_USER or not CALDAV_PASSWORD:
            raise ValueError("CALDAV_USER et CALDAV_PASSWORD requis dans .env")
        
        self.calendar_name = calendar_name
        self.calendar = self._connect_calendar()
    
    def _connect_calendar(self):
        client = DAVClient(
            url=CALDAV_URL,
            username=CALDAV_USER,
            password=CALDAV_PASSWORD
        )
        return client.principal().calendar(name=self.calendar_name)
    
    def find_events(self, start_date=None, days_ahead=7, search_terms=SEARCH_TERMS):
        """Trouve les événements avec les emojis recherchés"""
        if start_date is None:
            start_date = datetime.now() + timedelta(days=1)
        
        end_date = start_date + timedelta(days=days_ahead)
        
        try:
            events = self.calendar.search(start=start_date, end=end_date)
            found_events = []
            
            for event in events:
                cal = icalendar.Calendar.from_ical(event.data)
                for component in cal.walk():
                    if component.name == "VEVENT":
                        summary = str(component.get('SUMMARY', ''))
                        if any(emoji in summary for emoji in search_terms):
                            found_events.append({
                                'summary': summary,
                                'start': component.get('dtstart').dt,
                                'end': component.get('dtend').dt,
                                'uid': str(component.get('uid'))
                            })
            
            logger.info(f"🔍 Trouvé {len(found_events)} événements")
            return found_events
        except Exception as e:
            logger.error(f"❌ Erreur recherche: {e}")
            return []
    
    def delete_events(self, events):
        """Supprime une liste d'événements"""
        deleted = 0
        for event in events:
            try:
                cal_event = self.calendar.event_by_uid(event['uid'])
                cal_event.delete()
                deleted += 1
            except Exception as e:
                logger.warning(f"⚠️ Impossible de supprimer {event['uid']}: {e}")
        
        logger.info(f"🗑️ Supprimé {deleted}/{len(events)} événements")
    
    def create_events(self, events):
        """Crée une liste d'événements"""
        created = 0
        for event in events:
            try:
                cal = icalendar.Calendar()
                ical_event = icalendar.Event()
                
                ical_event.add('summary', event['summary'])
                ical_event.add('dtstart', event['start'])
                ical_event.add('dtend', event['end'])
                ical_event.add('uid', f"pickleball-{event['start'].strftime('%Y%m%d-%H%M')}")
                
                cal.add_component(ical_event)
                self.calendar.save_event(cal.to_ical())
                created += 1
                
            except Exception as e:
                logger.error(f"❌ Échec création: {e}")
        
        logger.info(f"➕ Créé {created}/{len(events)} événements")
    
    def parse_appointments_json(self, filepath="appointments.json"):
        # Mapping des mois
        MONTH_MAP = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        """Parse le JSON et retourne les événements futurs"""
        try:
            with open(filepath, 'r') as f:
                appointments = json.load(f)
        except FileNotFoundError:
            logger.error(f"❌ Fichier non trouvé: {filepath}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON invalide: {e}")
            return []
        
        today = date.today()
        current_year = today.year
        current_month = today.month
        events = []
        
        for apt in appointments:
            try:
                # Parser la date
                date_parts = apt['date'].split('\n')
                day = int(date_parts[1])
                month = MONTH_MAP[date_parts[2]]
                name = apt['name']
                
                # Année: actuelle si mois >= actuel, sinon suivante
                year = current_year if month >= current_month else current_year + 1
                
                # Parser les heures
                time_parts = apt['time'].replace('\n', ' ').split(' - ')
                start = datetime.strptime(
                    f"{year}-{month:02d}-{day:02d} {time_parts[0].strip()}", 
                    "%Y-%m-%d %I:%M %p"
                )
                end = datetime.strptime(
                    f"{year}-{month:02d}-{day:02d} {time_parts[1].strip()}", 
                    "%Y-%m-%d %I:%M %p"
                )
                
                # Garder seulement les futurs
                if start.date() > today:
                    events.append({
                        'start': start,
                        'end': end,
                        'summary': f'🏓 Registration {name}'
                    })
                    
            except Exception as e:
                logger.warning(f"⚠️ Erreur parsing: {e}")
        
        events.sort(key=lambda x: x['start'])
        logger.info(f"📅 Parsé {len(events)} événements futurs")
        
        return events
    
    def sync_pickleball_events(self):
        """Synchronisation complète"""
        logger.info("🔄 Début synchronisation")
        logger.info("=" * 50)
        
        # Nettoyer les anciens
        old_events = self.find_events(days_ahead=60)
        if old_events:
            self.delete_events(old_events)
        
        # Créer les nouveaux
        new_events = self.parse_appointments_json()
        if new_events:
            logger.info(f"📅 Création de {len(new_events)} événements:")
            for event in new_events:  # Montrer les 3 premiers
                logger.info(f"  • {event['start'].strftime('%b %d %H:%M')}")
            
            self.create_events(new_events)
        else:
            logger.warning("⚠️ Aucun événement futur dans le JSON")
        
        logger.info("=" * 50)
        logger.info("✅ Synchronisation terminée!")

def update_calendar():
    try:
        manager = PickleballCalendarManager()
        manager.sync_pickleball_events()
    
    except ValueError as e:
        logger.error(f"❌ Erreur config: {e}")
        logger.info("Vérifiez CALDAV_USER et CALDAV_PASSWORD dans .env")
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        raise

secure_login = SecureWebLogin(logon_url, email, password)
secure_login.login()  # ✅ D'abord se connecter
secure_login.save_appointments_json()
secure_login.quit()
send_all_appointments_email(load_appointments())
update_calendar()