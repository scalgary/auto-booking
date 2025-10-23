from datetime import datetime, date, timedelta
import json
import logging
import os

from caldav import DAVClient
from dotenv import load_dotenv
import icalendar

# Configuration
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration simple
CALDAV_USER = os.getenv("CALDAV_USER")
CALDAV_PASSWORD = os.getenv("CALDAV_PASSWORD")
CALDAV_URL = 'https://caldav.icloud.com'
CALENDAR_NAME = "Family"
SEARCH_TERMS = ['🏓', '🎾']

# Mapping des mois
MONTH_MAP = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

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
                        'summary': '🏓 registration Pickleball'
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






def main():
    """Point d'entrée principal"""
    try:
        manager = PickleballCalendarManager()
        manager.sync_pickleball_events()
        
    except ValueError as e:
        logger.error(f"❌ Erreur config: {e}")
        logger.info("Vérifiez CALDAV_USER et CALDAV_PASSWORD dans .env")
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        raise


if __name__ == "__main__":
    main()
