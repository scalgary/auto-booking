import logging
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
import sys



start = time.perf_counter()
# Configuration du logger
def setup_logger(debug_mode=False):
    """Configure le logger avec console + fichier"""
    
    # Nom du fichier log avec timestamp
    log_filename = f"booking_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configuration
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)
    
    # Supprimer les handlers existants
    logger.handlers.clear()
    
    # Format des messages
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Handler 1: Console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if debug_mode else logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler 2: Fichier
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # Tout dans le fichier
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logger.info(f"📝 Logs sauvegardés dans: {log_filename}")
    
    return logger


# Initialize logger
DEBUG = False  # Set to False in production
logger = setup_logger(debug_mode=DEBUG)
time_sleep=3
implicit_wait=0.5
web_wait_time=3
poll_frequency=0.1
##########

email = os.getenv('YOUR_SECRET_EMAIL')
password = os.getenv('YOUR_SECRET_PASSWORD')
logon_url = os.getenv("YOUR_SECRET_LOGON_URL")
planning_url = os.getenv('YOUR_SECRET_PLANNING_URL')
login_url = os.getenv('YOUR_SECRET_LOGIN_URL')
my_name = os.getenv('YOUR_SECRET_MY_NAME')
his_name = os.getenv('YOUR_SECRET_HIS_NAME')



# Vérification des secrets
logger.info("=== STATUS DES AUTRES SECRETS (MASQUÉS) ===")
logger.info(f"EMAIL: {'✅ DÉFINI' if email else '❌ MISSING'}")
logger.info(f"PASSWORD: {'✅ DÉFINI' if password else '❌ MISSING'}")
logger.info(f"MY_NAME: {'✅ DÉFINI' if my_name else '❌ MISSING'}")
logger.info(f"his_name: {'✅ DÉFINI' if his_name else '❌ MISSING'}")
logger.info(f"LOGON_URL: {'✅ DÉFINI' if logon_url else '❌ MISSING'}")
logger.info(f"PLANNING_URL: {'✅ DÉFINI' if planning_url else '❌ MISSING'}")
logger.info(f"LOGIN_URL: {'✅ DÉFINI' if login_url else '❌ MISSING'}")

# Vérification complète
secrets_dict = {
    "EMAIL": email,
    "PASSWORD": password,
    "MY_NAME": my_name,
    "LOGON_URL": logon_url,
    "PLANNING_URL": planning_url,
    "LOGIN_URL": login_url,
    "HIS_NAME" : his_name,
    "MY_NAME": my_name
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




class TennisBookingBot:
    """Bot de réservation de tennis/sport complet avec screenshots debug"""
    
    def __init__(self, target_date, target_time, course_level, player_name, time_sleep, web_wait_time, poll_frequency, debug_mode=False):
        # Paramètres de réservation
        self.target_date = target_date
        self.target_time = target_time
        self.course_level = course_level
        self.player_name = player_name
        self.time_sleep = time_sleep
        self.web_wait_time = web_wait_time
        self.poll_frequency = poll_frequency
        self.debug_mode = debug_mode
        self.screenshot_counter = 0
        self.implicit_wait=0.5
        
        # URLs et credentials depuis env
        self.email = os.getenv('YOUR_SECRET_EMAIL')
        self.password = os.getenv('YOUR_SECRET_PASSWORD')
        self.logon_url = os.getenv("YOUR_SECRET_LOGON_URL")
        self.planning_url = os.getenv('YOUR_SECRET_PLANNING_URL')
        self.login_url = os.getenv('YOUR_SECRET_LOGIN_URL')
        
        # Driver
        self.driver = None
        self.logged_in = False
        
        # Vérifier les secrets
        self._check_secrets()
        
        logger.info(f"🤖 Bot créé pour:")
        logger.info(f"📅 Date: {self.target_date}")
        logger.info(f"🕐 Time: {self.target_time}")
        logger.info(f"🎾 Level: {self.course_level}")
        logger.info(f"👤 Player: {self.player_name}")
        logger.info(f"🐛 Debug mode: {'✅ ON' if self.debug_mode else '❌ OFF'}")
    
    def _check_secrets(self):
        """Vérifier que tous les secrets sont présents"""
        secrets = {
            "EMAIL": self.email,
            "PASSWORD": self.password,
            "LOGON_URL": self.logon_url,
            "PLANNING_URL": self.planning_url,
            "LOGIN_URL": self.login_url
        }
        
        logger.info("=== STATUS DES SECRETS ===")
        missing = []
        for name, value in secrets.items():
            status = "✅ DÉFINI" if value else "❌ MISSING"
            logger.info(f"{name}: {status}")
            if not value:
                missing.append(name)
        
        if missing:
            logger.error(f"❌ ERREUR: {len(missing)} secrets manquants")
            sys.exit(1)
        logger.info("✅ Tous les secrets OK")
    
    def _debug_screenshot(self, step_name):
        """Prendre une screenshot en mode debug"""
        if self.debug_mode and self.driver:
            self.screenshot_counter += 1
            filename = f"debug_{self.screenshot_counter:02d}_{step_name}_{self.target_date.replace('-', '_')}.png"
            self.driver.save_screenshot(filename)
            logger.debug(f"📸 Screenshot: {filename}")
            return filename
        return None
    
    def _setup_driver(self):
        """Initialise le driver Chrome"""
        logger.info("🚀 Initialisation du driver...")
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_window_size(1400, 900)
        self.driver.set_page_load_timeout(100)  # 5 minutes au lieu du défaut
        self.driver.implicitly_wait( self.implicit_wait)  # Add this for element searches

        logger.info("✅ Driver configuré")
        self._debug_screenshot("driver_setup")
    
    def login(self):
        """Se connecter au site"""
        start_time = time.perf_counter()  # ← AJOUTER

        if not self.driver:
            self._setup_driver()
        
        logger.info("🔐 Connexion en cours...")
        self.driver.get(self.logon_url)

        # Option 3: Wait for specific element (BEST - also ensures page is loaded)
        WebDriverWait(self.driver, timeout = web_wait_time, poll_frequency = poll_frequency).until(EC.presence_of_element_located((By.ID, "Logon")))  # or any unique element)
        logger.info(f"⏱️ Page login chargée en {time.perf_counter() - start_time:.3f}s")  # ← AJOUTER
        logger.info(f"📄 Titre: {self.driver.title}")
        self._debug_screenshot("login_page_loaded")
        
        wait = WebDriverWait(self.driver, timeout = self.web_wait_time, poll_frequency = self.poll_frequency)
        try:
            # Email
            email_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='email']")))
            email_field.clear()
            email_field.send_keys(self.email)
            logger.info("📧 Email saisi")
            self._debug_screenshot("email_entered")
            
            # Password
            password_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password']")))
            password_field.clear()
            password_field.send_keys(self.password)
            logger.info("🔑 Password saisi")
            self._debug_screenshot("password_entered")
            
            # Login button
            login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Login']")))
            login_button.click()
            logger.info("✅ Bouton Login cliqué")
            self._debug_screenshot("login_button_clicked")
            
            # Attendre redirection
            wait.until(EC.url_changes(self.logon_url))
            self.logged_in = True
            logger.info(f"⏱️ Login total: {time.perf_counter() - start_time:.3f}s")  # ← AJOUTER
            self._debug_screenshot("login_success")
            return True
            
        except TimeoutException as e:
            logger.error(f"❌ Erreur login: {e}")
            self._debug_screenshot("login_error")
            return False
    
    def _check_date_validity(self):
        """Vérifier si la date est valide pour réservation"""
        if self.debug_mode:
            logger.warning("🐛 DEBUG MODE: Skip date validation")
            return True, True
        try:
            target_datetime = datetime.strptime(self.target_date, "%d-%b-%y")
            today = datetime.now()
            difference = target_datetime - today
            days_difference = difference.days
            
            is_future = target_datetime > today
            is_within_week = days_difference <= 6
            is_next_week = days_difference == 6
            
            logger.info(f"📅 Date cible: {target_datetime.strftime('%Y-%m-%d')}")
            logger.info(f"📅 Aujourd'hui: {today.strftime('%Y-%m-%d')}")
            logger.info(f"📊 Différence: {days_difference} jours")
            
            can_book = is_future and is_within_week
            if self.debug_mode:
                can_book=True
                is_next_week=True
            return can_book, is_next_week
            
        except ValueError:
            logger.error(f"❌ Format de date invalide: {self.target_date}")
            return False, False
    
    def _check_basket_empty(self):
        """Vérifier si le panier est vide"""
        self._debug_screenshot("before_basket_check")
        if self.driver.current_url == self.login_url:
            is_empty = self.driver.execute_script("return document.querySelector('span.basket-badge').textContent;") == "0"
            logger.info(f"🛒 Panier {'vide' if is_empty else 'non vide'}")
            self._debug_screenshot("basket_checked")
            return is_empty
        logger.warning("❌ Pas sur la page de login")
        self._debug_screenshot("not_on_login_page")
        return False
    
    def _navigate_to_planning(self, next_week=False):
        """Naviguer vers la page de planning"""
        start_time = time.perf_counter()  # ← AJOUTER

        logger.info("🗓️ Navigation vers planning...")
        # ❌ Attente aveugle (toujours 500ms même si chargé en 100ms)

        #self.driver.get(self.planning_url)
        #time.sleep(self.time_sleep)


        # ✅ Attente intelligente (100ms si rapide, 3s si lent)
        self.driver.get(self.planning_url)
        WebDriverWait(self.driver, timeout = self.time_sleep, poll_frequency=self.poll_frequency).until(
            EC.presence_of_element_located((By.XPATH, "//button[@data-class-time]"))
)
        self._debug_screenshot("planning_page_loaded")
        logger.info(f"⏱️ Planning semaine  chargé en {time.perf_counter() - start_time:.3f}s")  # ← AJOUTER

        if next_week:
            logger.info("⏭️ Navigation vers semaine suivante...")
            next_week_btn = self.driver.find_element(By.XPATH, "//input[@value='Next Week']")
            
            # Capturer un élément qui va changer
            old_buttons = self.driver.find_elements(By.XPATH, "//button[@data-class-time]")
            old_date = old_buttons[0].get_attribute('data-class-date') if old_buttons else None
            
            next_week_btn.click()
            
            # Attendre que les dates changent (au lieu de time.sleep aveugle)
            WebDriverWait(self.driver, timeout=self.web_wait_time, poll_frequency=self.poll_frequency).until(
                lambda d: (
                    d.find_elements(By.XPATH, "//button[@data-class-time]") and
                    d.find_elements(By.XPATH, "//button[@data-class-time]")[0].get_attribute('data-class-date') != old_date
                )
            )
            logger.info("✅ Planning semaine suivante chargé")
            self._debug_screenshot("next_week_clicked")
            
            logger.info(f"⏱️ Planning semaine suivante chargé en {time.perf_counter() - start_time:.3f}s")  # ← AJOUTER
            
            self._debug_screenshot("final_planning_view")
    
    def _find_available_slot(self):
        """Chercher un créneau disponible"""
        overall_start = time.perf_counter()  # ← AJOUTER

        logger.info("🔍 Recherche de créneaux...")
        self._debug_screenshot("before_slot_search")
        
        course_buttons = self.driver.find_elements(By.XPATH, "//button[@data-class-time]")
        logger.info(f"📋 {len(course_buttons)} boutons trouvés")
        
        for i, button in enumerate(course_buttons):
            # Extraire les données
            class_name = button.get_attribute('data-class-name') or ''
            class_date = button.get_attribute('data-class-date') or ''
            class_time = button.get_attribute('data-class-time') or ''
            class_spaces = button.get_attribute('data-class-spaces') or '0'
            
            # Vérifier correspondance
            date_match = self.target_date in class_date
            level_match = self.course_level in class_name
            time_match = self.target_time in class_time.split("-")[0] or self.target_time.strip() in class_time.split("-")[0]
            
            logger.debug(f"Bouton {i}: {class_name} | {class_date} | {class_time} | Espaces: {class_spaces}")
            logger.debug(f"  Date match: {date_match} | Level match: {level_match} | Time match: {time_match}")
            
            if date_match and time_match and level_match:
                spaces_available = int(class_spaces)
                logger.info(f"✅ CRÉNEAU TROUVÉ!")
                logger.info(f"  📛 Nom: {class_name}")
                logger.info(f"  📅 Date: {class_date}")
                logger.info(f"  🕐 Heure: {class_time}")
                logger.info(f"  👥 Places: {spaces_available}")
                
                self._debug_screenshot("slot_found")
                
                if spaces_available > 0:
                    return {
                        'button': button,
                        'available': True,
                        'spaces': spaces_available
                    }
                else:
                    logger.warning("❌ Créneau complet")
                    self._debug_screenshot("slot_full")
                    return {
                        'button': button,
                        'available': False,
                        'spaces': 0
                    }
        
        logger.warning("❌ Aucun créneau trouvé")
        self._debug_screenshot("no_slot_found")
        return None


                

    
    def _find_and_wait_for_bookable_slot(self, max_refresh=8):
        """Trouver le slot et attendre qu'il devienne bookable"""
        overall_start = time.perf_counter()  # ← AJOUTER

        logger.info("🔍 Recherche du slot correspondant...")
        
        for refresh_count in range(max_refresh):
            loop_start = time.perf_counter()  # ← AJOUTER
            self._debug_screenshot(f"search_attempt_{refresh_count + 1}")
            
            course_buttons = self.driver.find_elements(By.XPATH, "//button[@data-class-time]")
            logger.info(f"📋 {len(course_buttons)} slots trouvés (tentative {refresh_count + 1}/{max_refresh})")
            
            for button in course_buttons:
                # Extraire données
                class_name = button.get_attribute('data-class-name') or ''
                class_date = button.get_attribute('data-class-date') or ''
                class_time = button.get_attribute('data-class-time') or ''
                class_spaces = button.get_attribute('data-class-spaces') or '0'
                
                # Match du slot
                date_match = self.target_date in class_date
                level_match = self.course_level in class_name
                time_match = self.target_time in class_time.split("-")[0]
                
                if not (date_match and time_match and level_match):
                    continue
                    
                logger.info(f"✅ SLOT TROUVÉ: {class_name} | {class_date} | {class_time}")
                logger.info(f"⏱️ Slot trouvé en {time.perf_counter() - loop_start:.3f}s")  # ← AJOUTER

                parent = button.find_element(By.XPATH, "./..")
                poll_start = time.perf_counter()  # ← AJOUTER

                # POLLER sans refresh d'abord (3s max)
                wait = WebDriverWait(self.driver, timeout=self.web_wait_time, poll_frequency=self.poll_frequency)
                try:
                    wait.until(lambda d: len(parent.find_elements(
                        By.XPATH, ".//*[contains(text(), 'Book Now') or contains(text(), 'Book')]"
                    )) > 0)
                    
                    spaces = int(class_spaces)
                    logger.info(f"🎉 BOOKABLE! ({spaces} places)")
                    logger.info(f"⏱️ Polling réussi en {time.perf_counter() - poll_start:.3f}s")  # ← AJOUTER
                    logger.info(f"⏱️ Total recherche: {time.perf_counter() - overall_start:.3f}s")  # ← AJOUTER

                    self._debug_screenshot("slot_bookable")
                    return {'button': button, 'available': spaces > 0, 'spaces': spaces}
                    
                except TimeoutException:
                    logger.warning(f"⚠️ Unavailable après {self.web_wait_time}s polling")
                
                # REFRESH et retry
                if refresh_count < max_refresh - 1:
                    refresh_start = time.perf_counter()  # ← AJOUTER

                    logger.info(f"🔄 Refresh {refresh_count + 1}/{max_refresh}")
                    self.driver.refresh()
                    
                    # Attendre que les boutons se rechargent
                    WebDriverWait(self.driver, timeout=self.web_wait_time, poll_frequency=self.poll_frequency).until(
                        EC.presence_of_element_located((By.XPATH, "//button[@data-class-time]"))
                    )
                    logger.info(f"⏱️ Refresh en {time.perf_counter() - refresh_start:.3f}s")  # ← AJOUTER

                break
            
            else:
                # Slot pas trouvé du tout
                logger.warning("❌ Slot non trouvé")
                if refresh_count < max_refresh - 1:
                    self.driver.refresh()
                    WebDriverWait(self.driver, timeout=self.web_wait_time, poll_frequency=self.poll_frequency).until(
                        EC.presence_of_element_located((By.XPATH, "//button[@data-class-time]"))
                    )
        
        logger.error(f"❌ Échec après {max_refresh} tentatives")
        return None
                        

    def _click_book_slot(self, slot):
        """Cliquer pour réserver le créneau"""
        start_time = time.perf_counter()  # ← AJOUTER

        logger.info("📝 Réservation du créneau...")
        self._debug_screenshot("before_book_click")
        
        wait = WebDriverWait(self.driver, timeout=self.web_wait_time, poll_frequency=self.poll_frequency)
        
        parent = slot['button'].find_element(By.XPATH, "./..")
        book_buttons = parent.find_elements(
            By.XPATH, 
            ".//*[contains(text(), 'Book Now') or contains(text(), 'Book')]"
        )
        
        if not book_buttons:
            logger.error("❌ Bouton 'Book' non trouvé")
            logger.info(f"⏱️ Bouton 'Book' non trouvé {time.perf_counter() - start_time:.3f}s")  # ← AJOUTER

            self._debug_screenshot("book_button_not_found")
            return False
        
        try:
            logger.info("✅ Bouton 'Book' trouvé")
            logger.info(f"⏱️ Bouton 'Book' trouvé {time.perf_counter() - start_time:.3f}s")  # ← AJOUTER

            
            # Attendre que le bouton soit cliquable
            button = wait.until(EC.element_to_be_clickable(book_buttons[0]))
            current_url = self.driver.current_url
            button.click()
            
            # Attendre preuve du succès (page joueur OU checkout)
            wait.until(lambda d: 
                d.current_url != current_url or
                len(d.find_elements(By.XPATH, f"//*[contains(text(), '{self.player_name}')]")) > 0 or
                len(d.find_elements(By.XPATH, "//*[contains(text(), 'Select') or contains(text(), 'Choose')]")) > 0
            )
            
            logger.info("✅ Slot booké, page suivante chargée")
            logger.info(f"⏱️ Click book en {time.perf_counter() - start_time:.3f}s")  # ← AJOUTER

            self._debug_screenshot("book_button_clicked")
            return True
            
        except TimeoutException:
            logger.error("❌ Click échoué ou timeout")
            self._debug_screenshot("book_click_failed")
            return False
    
    def _select_player(self):
        """Sélectionner le joueur"""
        start_time = time.perf_counter()  # ← AJOUTER

        logger.info(f"👤 Sélection du joueur: {self.player_name}")
        self._debug_screenshot("before_player_selection")
        
        # Attendre que les joueurs soient chargés
        wait = WebDriverWait(self.driver, timeout=self.web_wait_time, poll_frequency=self.poll_frequency)
        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, f"//*[contains(text(), '{self.player_name}')]")
            ))
        except TimeoutException:
            logger.error(f"❌ {self.player_name} non trouvé")
            self._debug_screenshot("player_not_found")
            return False
        
        player_elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{self.player_name}')]")
        
        for player_element in player_elements:
            parent = player_element.find_element(By.XPATH, "./..")
            select_buttons = parent.find_elements(
                By.XPATH, 
                ".//*[contains(text(), 'Book') or contains(text(), 'Select') or contains(text(), 'Choose')]"
            )
            
            if select_buttons:
                logger.info(f"✅ Bouton trouvé pour {self.player_name}")
                
                # Attendre que le bouton soit cliquable
                button = wait.until(EC.element_to_be_clickable(select_buttons[0]))
                current_url = self.driver.current_url
                button.click()
                
                # Attendre changement d'URL ou élément "Checkout"
                try:
                    wait.until(lambda d: 
                        d.current_url != current_url or 
                        len(d.find_elements(By.XPATH, "//*[contains(text(), 'Checkout')]")) > 0
                    )
                    logger.info("✅ Joueur sélectionné")
                    logger.info(f"⏱️ Sélection joueur en {time.perf_counter() - start_time:.3f}s")  # ← AJOUTER

                    self._debug_screenshot("player_selected")
                    return True
                except TimeoutException:
                    logger.warning("⚠️ Click sans effet visible")
        
        logger.error(f"❌ Sélection impossible")
        self._debug_screenshot("player_selection_failed")
        return False
    
    def _confirm_booking(self):
        """Confirmer la réservation"""
        start_time = time.perf_counter()  # ← AJOUTER

        logger.info("✅ Confirmation de la réservation...")
        self._debug_screenshot("before_checkout")
        
        wait = WebDriverWait(self.driver, timeout=self.web_wait_time, poll_frequency=self.poll_frequency)
        
        try:
            # Attendre que Checkout apparaisse
            checkout_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(text(), 'Checkout')]")
            ))
            
            current_url = self.driver.current_url
            checkout_button.click()
            logger.info("🔄 Checkout cliqué, attente confirmation...")
            
            # Attendre signe de succès (URL change OU message confirmation)
            try:
                wait.until(lambda d: 
                    d.current_url != current_url or
                    len(d.find_elements(By.XPATH, "//*[contains(text(), 'confirmed') or contains(text(), 'Confirmed') or contains(text(), 'Success')]")) > 0
                )
                logger.info("🎉 RÉSERVATION CONFIRMÉE!")
                logger.info(f"⏱️ Confirmation en {time.perf_counter() - start_time:.3f}s")  # ← AJOUTER

                self._debug_screenshot("booking_confirmed")
                return True
                
            except TimeoutException:
                logger.warning("⚠️ Pas de confirmation visible, mais checkout cliqué")
                self._debug_screenshot("checkout_no_confirmation")
                return True  # Considérer comme succès si pas d'erreur
            
        except TimeoutException:
            logger.error("❌ Bouton Checkout non trouvé")
            self._debug_screenshot("checkout_not_found")
            return False
    
    def book(self):
        """Méthode principale de réservation"""
        booking_start = time.perf_counter()  # ← AJOUTER

        if not self.logged_in:
            logger.error("❌ Pas connecté. Appelez login() d'abord")
            return False
        
        logger.info("🎯 Début de la réservation...")
        self._debug_screenshot("booking_start")
        
        # 1. Vérifier la date
        can_book, next_week = self._check_date_validity()
        if not can_book:
            logger.error("❌ Date non valide pour réservation")
            self._debug_screenshot("invalid_date")
            return False
        
        # 2. Vérifier panier vide
        #if not self._check_basket_empty():
        #    logger.error("❌ Panier non vide")
        #    return False
        
        # 3. Aller au planning
        self._navigate_to_planning(next_week)
        
        # 4. Chercher créneau
        slot = self._find_and_wait_for_bookable_slot()
        if not slot:
            logger.error("❌ Aucun créneau disponible")
            return False
        
        if not slot['available']:
            logger.info("❌ Créneau complet")
            return True
        
        # 5. Réserver le créneau
        if not self._click_book_slot(slot):
            return False
        
        # 6. Sélectionner joueur
        if not self._select_player():
            return False
        
        # 7. Confirmer
        success = self._confirm_booking()
        if success:
            logger.info(f"⏱️ RÉSERVATION TOTALE: {time.perf_counter() - booking_start:.3f}s")  # ← AJOUTER
            self._debug_screenshot("final_success")
        else:
            self._debug_screenshot("final_failure")
        
        return success
    
    def quit(self):
        """Fermer le driver"""
        if self.driver:
            self._debug_screenshot("before_quit")
            self.driver.quit()
            logger.info("🔒 Driver fermé")

# Valeurs par défaut
DEFAULT_DATE = "27-Nov-25"
DEFAULT_TIME = "8:00"
DEFAULT_LEVEL = "Intermediate"
DEFAULT_NAME = os.getenv('YOUR_SECRET_HIS_NAME', 'Player')


# Arguments ou défauts
target_date = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATE
target_time = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TIME
course_level = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_LEVEL
player_name = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_NAME


    # Créer bot avec mode debug
bot = TennisBookingBot(
        target_date=target_date,
        target_time=target_time, 
        course_level=course_level,
        player_name=player_name,
        time_sleep=time_sleep,
        web_wait_time=web_wait_time,
        poll_frequency=poll_frequency,
        debug_mode=DEBUG
    )


try:
    if bot.login():
        success = bot.book()
        exit_code = 0 if success else 1
    else:
        exit_code = 1
finally:
    bot.quit()

elapsed = time.perf_counter() - start
print(f" Runtime: {elapsed:.6f} seconds")
sys.exit(exit_code)