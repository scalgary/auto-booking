# main.py
import logging
from datetime import datetime
from TennisBookingBot import TennisBookingBot
import sys
import os
import time

start = time.perf_counter()

debug_mode = False  # ou False

# ✅ Configurer UNE FOIS avant de créer le bot
log_filename = f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.DEBUG if debug_mode else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_filename, encoding='utf-8')
    ]
)

# Logger pour main.py lui-même
logger = logging.getLogger(__name__)
logger.info("🚀 Démarrage...")


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



# Valeurs par défaut
DEFAULT_DATE = "02-Jun-26"
DEFAULT_TIME = "4:30"
DEFAULT_LEVEL = "Open"
DEFAULT_NAME = os.getenv('YOUR_SECRET_MY_NAME', 'Player')
DEFAULT_HOLD = False

# Arguments ou défauts
target_date = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATE
target_time = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TIME
course_level = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_LEVEL
player_name = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_NAME
hold_status = sys.argv[5] if len(sys.argv) > 5 else DEFAULT_HOLD

web_wait_time=25
time_sleep=3
implicit_wait=0.5
web_wait_time=4
poll_frequency=0.1


    # Créer bot avec mode debug
bot = TennisBookingBot(
        target_date=target_date,
        target_time=target_time, 
        course_level=course_level,
        player_name=player_name,
        time_sleep=time_sleep,
        web_wait_time=web_wait_time,
        poll_frequency=poll_frequency,
        debug_mode=debug_mode,
        hold_only=hold_status
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

#test 1 creneau complet
