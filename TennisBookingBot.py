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
from selenium.common.exceptions import StaleElementReferenceException

from datetime import datetime
import sys



class TennisBookingBot:
    """Bot de réservation de tennis/sport complet avec screenshots debug"""
    
    def __init__(self, target_date, target_time, course_level, player_name, time_sleep, web_wait_time, poll_frequency,
                  hold_only=False, hold_duration = 600,
                 debug_mode = False):
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
        self.hold_only = hold_only
        self.hold_duration = hold_duration
        
        # URLs et credentials depuis env
        self.email = os.getenv('YOUR_SECRET_EMAIL')
        self.password = os.getenv('YOUR_SECRET_PASSWORD')
        self.logon_url = os.getenv("YOUR_SECRET_LOGON_URL")
        self.planning_url = os.getenv('YOUR_SECRET_PLANNING_URL')
        self.login_url = os.getenv('YOUR_SECRET_LOGIN_URL')
        
        # Driver
        self.driver = None
        self.logged_in = False
        
        self.logger = logging.getLogger(__name__)  # ✅ remplace self._setup_logger()

        # Vérifier les secrets
        self._check_secrets()
        self.logger.info(f"🤖 Bot créé pour:")
        self.logger.info(f"📅 Date: {self.target_date}")
        self.logger.info(f"🕐 Time: {self.target_time}")
        self.logger.info(f"🎾 Level: {self.course_level}")
        self.logger.info(f"👤 Player: {self.player_name}")
        self.logger.info(f"🐛 Debug mode: {'✅ ON' if self.debug_mode else '❌ OFF'}")
        self.logger.info(f"⏸️ Hold only: {'✅ ON' if self.hold_only else '❌ OFF'}")
        self.logger.info(f"⏱️ Hold duration: {self.hold_duration}s")


    def _check_secrets(self):
        """Vérifier que tous les secrets sont présents"""
        secrets = {
            "EMAIL": self.email,
            "PASSWORD": self.password,
            "LOGON_URL": self.logon_url,
            "PLANNING_URL": self.planning_url,
            "LOGIN_URL": self.login_url
        }
        
        self.logger.info("=== STATUS DES SECRETS ===")
        missing = []
        for name, value in secrets.items():
            status = "✅ DÉFINI" if value else "❌ MISSING"
            self.logger.info(f"{name}: {status}")
            if not value:
                missing.append(name)
        
        if missing:
            self.logger.error(f"❌ ERREUR: {len(missing)} secrets manquants")
            sys.exit(1)
        self.logger.info("✅ Tous les secrets OK")
    
    def _debug_screenshot(self, step_name):
        """Prendre une screenshot en mode debug"""
        if self.debug_mode and self.driver:
            self.screenshot_counter += 1
            filename = f"debug_{self.screenshot_counter:02d}_{step_name}_{self.target_date.replace('-', '_')}.png"
            self.driver.save_screenshot(filename)
            self.logger.debug(f"📸 Screenshot: {filename}")
            return filename
        return None
    
    def _setup_driver(self):
        """Initialise le driver Chrome"""
        self.logger.info("🚀 Initialisation du driver...")
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')   # ADD
        options.add_argument('--disable-gpu')              # ADD
        options.add_argument('--disable-extensions')       # ADD
        options.add_argument('--shm-size=2g')              # ADD
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_window_size(1400, 900)
        self.driver.set_page_load_timeout(100)  # 5 minutes au lieu du défaut
        self.driver.implicitly_wait( self.implicit_wait)  # Add this for element searches

        self.logger.info("✅ Driver configuré")
        self._debug_screenshot("driver_setup")
    
    def login(self):
        """Se connecter au site"""
        start_time = time.perf_counter()  # ← AJOUTER

        if not self.driver:
            self._setup_driver()
        
        self.logger.info("🔐 Connexion en cours...")
        self.driver.get(self.logon_url)

        # Option 3: Wait for specific element (BEST - also ensures page is loaded)
        WebDriverWait(self.driver, timeout = self.web_wait_time, poll_frequency = self.poll_frequency).until(EC.presence_of_element_located((By.ID, "Logon")))  # or any unique element)
        self.logger.info(f"⏱️ Page login chargée en {time.perf_counter() - start_time:.3f}s")  # ← AJOUTER
        self.logger.info(f"📄 Titre: {self.driver.title}")
        self._debug_screenshot("login_page_loaded")
        
        wait = WebDriverWait(self.driver, timeout = self.web_wait_time, poll_frequency = self.poll_frequency)
        try:
            # Email
            email_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='email']")))
            email_field.clear()
            email_field.send_keys(self.email)
            self.logger.info("📧 Email saisi")
            self._debug_screenshot("email_entered")
            
            # Password
            password_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password']")))
            password_field.clear()
            password_field.send_keys(self.password)
            self.logger.info("🔑 Password saisi")
            self._debug_screenshot("password_entered")
            
            # Login button
            login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Login']")))
            login_button.click()
            self.logger.info("✅ Bouton Login cliqué")
            self._debug_screenshot("login_button_clicked")
            
            # Attendre redirection
            wait.until(EC.url_changes(self.logon_url))
            self.logged_in = True
            self.logger.info(f"⏱️ Login total: {time.perf_counter() - start_time:.3f}s")  # ← AJOUTER
            self._debug_screenshot("login_success")
            return True
            
        except TimeoutException as e:
            self.logger.error(f"❌ Erreur login: {e}")
            self._debug_screenshot("login_error")
            return False
    
    def _check_date_validity(self):
        """Vérifier si la date est valide pour réservation"""
        if self.debug_mode:
            self.logger.warning("🐛 DEBUG MODE: Skip date validation")
            return True, True
        try:
            target_datetime = datetime.strptime(self.target_date, "%d-%b-%y")
            today = datetime.now()
            difference = target_datetime - today
            days_difference = difference.days
            
            is_future = target_datetime > today
            is_within_week = days_difference <= 6
            is_next_week = days_difference == 6
            
            self.logger.info(f"📅 Date cible: {target_datetime.strftime('%Y-%m-%d')}")
            self.logger.info(f"📅 Aujourd'hui: {today.strftime('%Y-%m-%d')}")
            self.logger.info(f"📊 Différence: {days_difference} jours")
            
            can_book = is_future and is_within_week
            if self.debug_mode:
                can_book=True
                is_next_week=True
            return can_book, is_next_week
            
        except ValueError:
            self.logger.error(f"❌ Format de date invalide: {self.target_date}")
            return False, False
    
    def _check_basket_empty(self):
        """Vérifier si le panier est vide"""
        self._debug_screenshot("before_basket_check")
        if self.driver.current_url == self.login_url:
            is_empty = self.driver.execute_script("return document.querySelector('span.basket-badge').textContent;") == "0"
            self.logger.info(f"🛒 Panier {'vide' if is_empty else 'non vide'}")
            self._debug_screenshot("basket_checked")
            return is_empty
        self.logger.warning("❌ Pas sur la page de login")
        self._debug_screenshot("not_on_login_page")
        return False
    
    def _navigate_to_planning(self, next_week=False):
        """Naviguer vers la page de planning"""
        start_time = time.perf_counter()
        self.logger.info("🗓️ Navigation vers planning...")
        
        self.driver.get(self.planning_url)
        WebDriverWait(self.driver, timeout=self.time_sleep, poll_frequency=self.poll_frequency).until(
            EC.presence_of_element_located((By.XPATH, "//button[@data-class-time]"))
        )
        self.logger.info(f"⏱️ Planning chargé en {time.perf_counter() - start_time:.3f}s")

        if next_week:
            self.logger.info(f"⏭️ Next Week → recherche {self.target_date}...")
            
            next_week_btn = self.driver.find_element(By.XPATH, "//input[@value='Next Week']")
            self.driver.execute_script("arguments[0].click();", next_week_btn)
            
            # Attendre spécifiquement la target date
            try:
                WebDriverWait(self.driver, timeout=self.web_wait_time).until(
                    EC.presence_of_element_located((
                        By.XPATH, 
                        f"//button[contains(@data-class-date, '{self.target_date}')]"
                    ))
                )
                self.logger.info(f"✅ Date {self.target_date} trouvée!")
            except TimeoutException:
                self.logger.error(f"❌ Date {self.target_date} non trouvée")
                self._debug_screenshot("date_not_found")
            
            self.logger.info(f"⏱️ Total: {time.perf_counter() - start_time:.3f}s")
    
    def _select_player(self):
        """Sélectionner le joueur"""
        start_time = time.perf_counter()  # ← AJOUTER

        self.logger.info(f"👤 Sélection du joueur: {self.player_name}")
        self._debug_screenshot("before_player_selection")
        
        # Longer timeout for player page (can be slow)
        wait = WebDriverWait(self.driver, timeout=self.web_wait_time, poll_frequency=self.poll_frequency)
        
        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, f"//*[contains(text(), '{self.player_name}')]")
            ))
        except TimeoutException:
            self.logger.error(f"❌ {self.player_name} non trouvé")
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
                self.logger.info(f"✅ Bouton trouvé pour {self.player_name}")
                button = select_buttons[0]
                current_url = self.driver.current_url
                
                try:
                    # Wait for clickable
                    button = wait.until(EC.element_to_be_clickable(button))
                    button.click()
                    self.logger.info("✅ Click normal réussi")
                except TimeoutException:
                    # Fallback: force JS click
                    self.logger.warning("⚠️ Timeout clickable, force JS click...")
                    self.driver.execute_script("arguments[0].click();", button)
                
                # Wait for result
                try:
                    wait.until(lambda d: 
                        d.current_url != current_url or 
                        len(d.find_elements(By.XPATH, "//*[contains(text(), 'Checkout')]")) > 0
                    )
                    self.logger.info("✅ Joueur sélectionné")
                    self.logger.info(f"⏱️ Sélection joueur en {time.perf_counter() - start_time:.3f}s")
                    self._debug_screenshot("player_selected")
                    return True
                except TimeoutException:
                    self.logger.warning("⚠️ Click sans effet visible")
        
        self.logger.error(f"❌ Sélection impossible")
        self._debug_screenshot("player_selection_failed")
        return False
    
    def _confirm_booking(self):
        """Confirmer la réservation"""
        start_time = time.perf_counter()  # ← AJOUTER

        self.logger.info("✅ Confirmation de la réservation...")
        self._debug_screenshot("before_checkout")
        
        wait = WebDriverWait(self.driver, timeout=self.web_wait_time, poll_frequency=self.poll_frequency)
        
        try:
            # Attendre que Checkout apparaisse
            checkout_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(text(), 'Checkout')]")
            ))
            
            current_url = self.driver.current_url
            checkout_button.click()
            self.logger.info("🔄 Checkout cliqué, attente confirmation...")
            
            # Attendre signe de succès (URL change OU message confirmation)
            try:
                wait.until(lambda d: 
                    d.current_url != current_url or
                    len(d.find_elements(By.XPATH, "//*[contains(text(), 'confirmed') or contains(text(), 'Confirmed') or contains(text(), 'Success')]")) > 0
                )
                self.logger.info("🎉 RÉSERVATION CONFIRMÉE!")
                self.logger.info(f"⏱️ Confirmation en {time.perf_counter() - start_time:.3f}s")  # ← AJOUTER

                self._debug_screenshot("booking_confirmed")
                return True
                
            except TimeoutException:
                self.logger.warning("⚠️ Pas de confirmation visible, mais checkout cliqué")
                self._debug_screenshot("checkout_no_confirmation")
                return True  # Considérer comme succès si pas d'erreur
            
        except TimeoutException:
            self.logger.error("❌ Bouton Checkout non trouvé")
            self._debug_screenshot("checkout_not_found")
            return False
        
    def _cancel_basket(self):
        """Cancel basket (two confirmations required)"""
        start_time = time.perf_counter()
        self.logger.info("🗑️ Cancelling basket...")
        self._debug_screenshot("before_cancel_basket")


        wait = WebDriverWait(self.driver, timeout=self.web_wait_time, poll_frequency=self.poll_frequency)

        try:
            # First cancel
            cancel_btn = wait.until(EC.element_to_be_clickable(
             (By.XPATH, "//a[normalize-space(text())='Cancel Basket']")
            ))
            current_url = self.driver.current_url

            cancel_btn.click()
            self.logger.info("✅ First 'Cancel Basket' clicked")
            self._debug_screenshot("after_first_cancel")

            # Wait for confirmation page to load
            wait.until(EC.url_changes(current_url))
            self.logger.info(f"📍 New URL: {self.driver.current_url}")
            # Second cancel (confirmation)
            cancel_btn2 = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@type='submit' and @value='Cancel Basket']")
            ))
            cancel_btn2.click()
            self.logger.info("✅ Second 'Cancel basket' clicked")
            self.logger.info(f"⏱️ Cancel basket en {time.perf_counter() - start_time:.3f}s")
            self._debug_screenshot("after_second_cancel")
            return True
            
        except TimeoutException:
            self.logger.error("❌ Cancel basket button not found")
            self._debug_screenshot("cancel_basket_failed")
            return False
      
    def _click_book_slot(self, slot):
        """Cliquer pour réserver le créneau"""
        start_time = time.perf_counter()
        self.logger.info("📝 Réservation du créneau...")
        self._debug_screenshot("before_book_click")

        wait = WebDriverWait(self.driver, timeout=self.web_wait_time, poll_frequency=self.poll_frequency)

        # === DIAGNOSTIC: Analyser le slot reçu ===
        self.logger.info("=== ANALYSE DU SLOT ===")
        slot_button = slot['button']
        # self.logger.info(f"📊 Slot disponible: {slot.get('available')}")
        # self.logger.info(f"👥 Places: {slot.get('spaces')}")
        # self.logger.info(f"📍 Position: {slot_button.location}")
        # self.logger.info(f"📏 Taille: {slot_button.size}")
        # self.logger.info(f"👁️ Visible: {slot_button.is_displayed()}")
        # self.logger.info(f"✅ Activé: {slot_button.is_enabled()}")

        # Attributs du slot button
        # slot_attrs = {
        #     'class-name': slot_button.get_attribute('data-class-name'),
        #     'class-date': slot_button.get_attribute('data-class-date'),
        #     'class-time': slot_button.get_attribute('data-class-time'),
        #     'class-code': slot_button.get_attribute('data-class-code'),
        #     'tag': slot_button.tag_name
        # }
        # self.logger.info(f"🏷️ Attributs du slot: {slot_attrs}")

        # === RECHERCHE DES BOUTONS BOOK ===
        self.logger.info("=== RECHERCHE BOUTONS BOOK ===")
        parent = slot_button.find_element(By.XPATH, "./..")
        self.logger.info(f"📦 Parent tag: {parent.tag_name}")
        self.logger.info(f"📦 Parent class: {parent.get_attribute('class')}")

        # Chercher tous les boutons Book dans le parent
        book_buttons = parent.find_elements(
            By.XPATH, 
            ".//*[contains(text(), 'Book Now') or contains(text(), 'Book')]"
)

        self.logger.info(f"🔍 Nombre de boutons 'Book' trouvés: {len(book_buttons)}")

        if not book_buttons:
            self.logger.error("❌ Aucun bouton 'Book' trouvé")
            self.logger.info(f"⏱️ Échec en {time.perf_counter() - start_time:.3f}s")
            
            # Diagnostic supplémentaire
            self.logger.info("🔎 HTML du parent:")
            self.logger.info(parent.get_attribute('innerHTML')[:500])
            
            self._debug_screenshot("book_button_not_found")
            return False

        # === ANALYSE DE TOUS LES BOUTONS TROUVÉS ===
        self.logger.info("=== DÉTAILS DES BOUTONS BOOK ===")
        for i, btn in enumerate(book_buttons):
            self.logger.info(f"--- Bouton [{i}] ---")
            self.logger.info(f"  Texte: {btn.text}")
            self.logger.info(f"  Tag: {btn.tag_name}")
            self.logger.info(f"  Class: {btn.get_attribute('class')}")
            self.logger.info(f"  data-class-name: {btn.get_attribute('data-class-name')}")
            self.logger.info(f"  data-class-code: {btn.get_attribute('data-class-code')}")
            self.logger.info(f"  Position: {btn.location}")
            self.logger.info(f"  Visible: {btn.is_displayed()}")
            self.logger.info(f"  Activé: {btn.is_enabled()}")
    
            # Vérifier quel élément est physiquement au-dessus
            top_element_html = self.driver.execute_script("""
                var rect = arguments[0].getBoundingClientRect();
                var centerX = rect.left + rect.width / 2;
                var centerY = rect.top + rect.height / 2;
                var topElement = document.elementFromPoint(centerX, centerY);
                return topElement ? topElement.outerHTML.substring(0, 300) : 'null';
            """, btn)
            self.logger.info(f"  🎯 Élément au centre: {top_element_html[:100]}...")

        # === SÉLECTION DU BON BOUTON ===
        self.logger.info("=== SÉLECTION DU BOUTON ===")

        # Essayer de filtrer par data-class-name si disponible
        target_buttons = [
            btn for btn in book_buttons 
            if btn.get_attribute('data-class-name') and 
                self.course_level in btn.get_attribute('data-class-name')
        ]

        if target_buttons:
            self.logger.info(f"✅ Filtré par course_level: {len(target_buttons)} bouton(s)")
            button = target_buttons[0]
        else:
            self.logger.warning(f"⚠️ Pas de filtre possible, utilisation du premier bouton")
            button = book_buttons[0]

        self.logger.info(f"🎯 Bouton sélectionné: {button.get_attribute('data-class-name') or button.text}")

        # === TENTATIVE DE CLICK ===
        try:
            self.logger.info("=== PRÉPARATION DU CLICK ===")
            
            # Attendre que le bouton soit cliquable
            button = wait.until(EC.element_to_be_clickable(button))
            self.logger.info("✅ Bouton cliquable confirmé par WebDriverWait")
            self.logger.info(f"⏱️ Bouton prêt en {time.perf_counter() - start_time:.3f}s")
            
            # Scroll le bouton au centre
            self.logger.info("📜 Scroll vers le bouton...")
            self.driver.execute_script("""
                arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});
                window.scrollBy(0, -100);
            """, button)
            time.sleep(0.3)
            self.logger.info("✅ Scroll effectué")
            
            self._debug_screenshot("button_centered")
    
    # Vérifier à nouveau ce qui est au-dessus après scroll
            top_after_scroll = self.driver.execute_script("""
                var rect = arguments[0].getBoundingClientRect();
                var centerX = rect.left + rect.width / 2;
                var centerY = rect.top + rect.height / 2;
                var topElement = document.elementFromPoint(centerX, centerY);
                return {
                    html: topElement ? topElement.outerHTML.substring(0, 200) : 'null',
                    isSameElement: topElement === arguments[0]
                };
            """, button)
    
            self.logger.info(f"🔍 Après scroll - Même élément au centre: {top_after_scroll['isSameElement']}")
            if not top_after_scroll['isSameElement']:
                self.logger.warning(f"⚠️ ÉLÉMENT BLOQUANT: {top_after_scroll['html']}")
            
            current_url = self.driver.current_url
            self.logger.info(f"📍 URL actuelle: {current_url}")
            
            # Essayer click normal d'abord
            self.logger.info("🖱️ Tentative de click normal...")
            try:
                button.click()
                self.logger.info("✅ Click normal réussi")
            except Exception as e:
                self.logger.warning(f"⚠️ Click normal échoué: {type(e).__name__}")
                self.logger.warning(f"   Message: {str(e)[:200]}")
                self.logger.info("🔧 Basculement vers JS click...")
                self.driver.execute_script("arguments[0].click();", button)
                self.logger.info("✅ JS click exécuté")
    
            self._debug_screenshot("after_click")
            
            # Attendre preuve du succès
            self.logger.info("⏳ Attente de confirmation...")
            wait.until(lambda d: 
                d.current_url != current_url or
                len(d.find_elements(By.XPATH, f"//*[contains(text(), '{self.player_name}')]")) > 0 or
                len(d.find_elements(By.XPATH, "//*[contains(text(), 'Select') or contains(text(), 'Choose')]")) > 0
            )
            
            self.logger.info(f"📍 Nouvelle URL: {self.driver.current_url}")
            self.logger.info("✅ Slot booké, page suivante chargée")
            self.logger.info(f"⏱️ Click book total: {time.perf_counter() - start_time:.3f}s")
            self._debug_screenshot("book_button_clicked")
            return True
    
        except TimeoutException as e:
            self.logger.error("❌ Timeout lors du click")
            self.logger.error(f"   Temps écoulé: {time.perf_counter() - start_time:.3f}s")
            self.logger.error(f"   URL finale: {self.driver.current_url}")
            self._debug_screenshot("book_click_timeout")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Erreur inattendue: {type(e).__name__}")
            self.logger.error(f"   Message: {str(e)}")
            self.logger.error(f"   Temps écoulé: {time.perf_counter() - start_time:.3f}s")
            self._debug_screenshot("book_click_failed")
            return False
    

    def _find_and_wait_for_bookable_slot(self, max_refresh=8, timeout=3):
        """Chercher un créneau disponible"""
        overall_start = time.perf_counter()  # ← AJOUTER

        self.logger.info("🔍 Recherche de créneaux...")
        self._debug_screenshot("before_slot_search")

        def get_matching_slots():
            slots = []
            max_attempts = 3

            for attempt in range(max_attempts):
                try:
                    course_buttons = self.driver.find_elements(By.XPATH, "//button[@data-class-time]")
                    self.logger.info(f"📋 {len(course_buttons)} boutons trouvés")
                    slots = []

                    for button in course_buttons:
                        class_name   = button.get_attribute('data-class-name')  or ''
                        class_date   = button.get_attribute('data-class-date')  or ''
                        class_time   = button.get_attribute('data-class-time')  or ''
                        class_spaces = int(button.get_attribute('data-class-spaces') or '0')

                        date_match  = self.target_date  in class_date
                        level_match = self.course_level in class_name
                        time_match  = self.target_time  in class_time.split("-")[0]

                        self.logger.debug(f"Bouton : {class_name} | {class_date} | {class_time} | Espaces: {class_spaces}")
                        self.logger.debug(f"  Date match: {date_match} | Level match: {level_match} | Time match: {time_match}")

                        if date_match and time_match and level_match:
                            self.logger.info(f"✅ Match: {class_name} | {class_date} | {class_time} | spaces={class_spaces}")
                            slots.append({'button': button, 'spaces': class_spaces})
                            self._debug_screenshot("slot_found")

                    return slots  # success

                except StaleElementReferenceException:
                    self.logger.warning(f"⚠️ StaleElement lors de la lecture — retry {attempt + 1}/{max_attempts}")
                    time.sleep(0.5)

            self.logger.error("❌ StaleElement persistant après retries")
            return []

        # --- Step 1: initial fetch ---
        matching_slots = get_matching_slots()

        # --- Step 2: no match → return None ---
        if not matching_slots:
            self.logger.error("❌ Aucun slot correspondant trouvé")
            self._debug_screenshot("no_matching_slot_found")
            return None

        # --- Step 3: all slots have 0 spaces → return available False ---
        if all(slot['spaces'] == 0 for slot in matching_slots):
            self.logger.warning("⚠️ Tous les slots ont 0 place disponible")
            self._debug_screenshot("slot_no_spaces")
            return {'button': matching_slots[0]['button'], 'available': False, 'spaces': 0}

        # --- Step 4: refresh until bookable ---
        for refresh_count in range(max_refresh):
            self._debug_screenshot(f"search_attempt_{refresh_count + 1}")
            self.logger.info(f"🔄 Tentative {refresh_count + 1}/{max_refresh}")

            first_slot = matching_slots[0]
            parent = first_slot['button'].find_element(By.XPATH, "./..")
            book_buttons = parent.find_elements(
                By.XPATH,
                ".//*[contains(text(), 'Book Now') or contains(text(), 'Book')]"
            )

            if not bool(book_buttons):
                self.logger.warning(f"⏳ Slot non bookable - Refresh {refresh_count + 1}/{max_refresh}")
                self._debug_screenshot(f"slot_unavailable_{refresh_count + 1}")
            else:
                # --- Step 5: book first slot with spaces ---
                for slot in matching_slots:
                    if slot['spaces'] > 0:
                        self.logger.info(f"🎉 SLOT BOOKABLE! ({slot['spaces']} places)")
                        self._debug_screenshot("slot_bookable_ready")
                        return {'button': slot['button'], 'available': True, 'spaces': slot['spaces']}

                self.logger.warning("⚠️ Slots bookable mais aucune place disponible")
                self._debug_screenshot("slot_no_spaces")
                return {'button': first_slot['button'], 'available': False, 'spaces': 0}

            # Refresh and re-fetch fresh references
            if refresh_count < max_refresh - 1:
                wait = WebDriverWait(self.driver, timeout=timeout, poll_frequency=0.2)

                try:
                    self.driver.refresh()
                    time.sleep(self.time_sleep)
                    wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//*[contains(text(), 'Book Now') or contains(text(), 'Book')]")
                        )
                    )
                    self.logger.info("✅ Book Now détecté après refresh!")
                    matching_slots = get_matching_slots()  # fresh DOM references
                except TimeoutException:
                    self.logger.warning(f"⏱️ Timeout après refresh {refresh_count + 1}")
                    matching_slots = get_matching_slots()  # still re-fetch

        self.logger.error(f"❌ Impossible de trouver un slot bookable après {max_refresh} tentatives")
        self._debug_screenshot("no_bookable_slot_found")
        return None

    def book(self):
        """Méthode principale de réservation"""
        booking_start = time.perf_counter()  # ← AJOUTER

        if not self.logged_in:
            self.logger.error("❌ Pas connecté. Appelez login() d'abord")
            return False
        
        self.logger.info("🎯 Début de la réservation...")
        self._debug_screenshot("booking_start")
        
        # 1. Vérifier la date
        can_book, next_week = self._check_date_validity()
        if not can_book:
            self.logger.error("❌ Date non valide pour réservation")
            self._debug_screenshot("invalid_date")
            return False
        
        # 2. Vérifier panier vide
        #if not self._check_basket_empty():
        #    self.logger.error("❌ Panier non vide")
        #    return False
        
        # 3. Aller au planning
        self._navigate_to_planning(next_week)
        
        # 4. Chercher créneau
        slot = self._find_and_wait_for_bookable_slot()
        if not slot:
            self.logger.error("❌ Aucun créneau disponible")
            return True
        
        if not slot['available']:
            self.logger.info("❌ Créneau complet")
            return True
        
        # 5. Réserver le créneau
        if not self._click_book_slot(slot):
            return False
        

        
        # 6. Sélectionner joueur
        if not self._select_player():
            return False
        
        # 7. Hold only mode → attendre puis quitter sans confirmer
        if self.hold_only:
            self.logger.info(f"⏸️ HOLD MODE: spot bloqué {self.hold_duration}s")
            time.sleep(self.hold_duration)
            self.logger.info("⏸️ Hold terminé → release du spot")
            self.logger.info("⏸️ Hold terminé → cancelling basket")
            return self._cancel_basket()

        # 7. Confirmer
        success = self._confirm_booking()
        if success:
            self.logger.info(f"⏱️ RÉSERVATION TOTALE: {time.perf_counter() - booking_start:.3f}s")  # ← AJOUTER
            self._debug_screenshot("final_success")
        else:
            self._debug_screenshot("final_failure")
        
        return success
    

    def quit(self):
        """Fermer le driver"""
        if self.driver:
            self._debug_screenshot("before_quit")
            self.driver.quit()
            self.logger.info("🔒 Driver fermé")
