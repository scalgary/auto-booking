#!/usr/bin/env python3
# test_caldav_complete.py - Test complet CalDAV avec URLs et headers

import os
import logging
from caldav import DAVClient
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_all_caldav_options():
    """Teste toutes les combinaisons URL + headers pour CalDAV"""
    
    user = os.getenv("CALDAV_USER")
    password = os.getenv("CALDAV_PASSWORD")
    
    print(f"🔍 Testing with user: {user}")
    print(f"🔍 Password length: {len(password) if password else 0}")
    
    if not user or not password:
        print("❌ CALDAV credentials missing!")
        return None
    
    # Headers pour simuler différents clients
    headers_configs = [
        {
            'name': 'Standard (no headers)',
            'headers': None
        },
        {
            'name': 'Safari Mac',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'text/xml',
                'Content-Type': 'text/xml; charset=utf-8'
            }
        },
        {
            'name': 'Calendar App',
            'headers': {
                'User-Agent': 'CalendarAgent/1.0 (Mac OS X 10.15.7)',
                'Accept': 'text/calendar, text/xml',
                'Content-Type': 'text/xml; charset=utf-8'
            }
        },
        {
            'name': 'Thunderbird',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Thunderbird/91.0',
                'Accept': 'text/xml',
                'Content-Type': 'text/xml; charset=utf-8'
            }
        }
    ]
    
    # URLs à tester
    urls_to_test = [
        'https://caldav.icloud.com',
        f'https://caldav.icloud.com/{user}',
        'https://p01-caldav.icloud.com',
        f'https://p01-caldav.icloud.com/{user}',
        'https://caldav.icloud.com:443',
        f'https://caldav.icloud.com:443/{user}',
        'https://p02-caldav.icloud.com',
        'https://p03-caldav.icloud.com',
        'https://p04-caldav.icloud.com'
    ]
    
    print(f"\n🔬 Testing {len(urls_to_test)} URLs with {len(headers_configs)} header configs")
    print("=" * 60)
    
    working_configs = []
    
    for url in urls_to_test:
        print(f"\n🌐 Testing URL: {url}")
        
        for config in headers_configs:
            print(f"  📋 {config['name']}... ", end="")
            
            try:
                if config['headers']:
                    # Avec headers personnalisés
                    session = requests.Session()
                    session.headers.update(config['headers'])
                    client = DAVClient(url=url, username=user, password=password, session=session)
                else:
                    # Sans headers
                    client = DAVClient(url=url, username=user, password=password)
                
                # Test de connexion
                principal = client.principal()
                calendars = principal.calendars()
                
                print(f"✅ SUCCESS! ({len(calendars)} calendars)")
                
                # Lister les calendriers
                for cal in calendars:
                    print(f"    📅 {cal.name}")
                
                working_configs.append({
                    'url': url,
                    'headers': config['name'],
                    'calendars': len(calendars)
                })
                
            except Exception as e:
                print(f"❌ {str(e)[:50]}...")
    
    print("\n" + "=" * 60)
    print("📊 RESULTS:")
    
    if working_configs:
        print(f"✅ Found {len(working_configs)} working configurations:")
        for i, config in enumerate(working_configs, 1):
            print(f"  {i}. {config['url']} with {config['headers']} ({config['calendars']} calendars)")
        
        # Recommandation
        best = working_configs[0]
        print(f"\n🎯 RECOMMENDED CONFIG:")
        print(f"   URL: {best['url']}")
        print(f"   Headers: {best['headers']}")
        
        return best
    else:
        print("❌ NO WORKING CONFIGURATIONS FOUND")
        print("\n🔍 Possible issues:")
        print("  - App-specific password incorrect")
        print("  - Apple ID format wrong (should be full email)")
        print("  - iCloud CalDAV disabled")
        print("  - GitHub Actions IP blocked by Apple")
        
        return None

def test_basic_http():
    """Test basique HTTP pour voir si on peut atteindre iCloud"""
    user = os.getenv("CALDAV_USER")
    password = os.getenv("CALDAV_PASSWORD")
    
    print("\n🌐 Testing basic HTTP access to iCloud...")
    
    try:
        auth = (user, password)
        response = requests.get('https://caldav.icloud.com', auth=auth, timeout=10)
        print(f"📊 HTTP Status: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 401:
            print("❌ Authentication failed - check credentials")
        elif response.status_code == 403:
            print("❌ Forbidden - possibly blocked IP or wrong URL")
        elif response.status_code in [200, 207]:
            print("✅ HTTP access works!")
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ HTTP test failed: {e}")

if __name__ == "__main__":
    print("🧪 CALDAV CONNECTION TEST")
    print("=" * 60)
    
    # Test 1: HTTP basique
    test_basic_http()
    
    # Test 2: CalDAV complet
    working_config = test_all_caldav_options()
    
    if working_config:
        print(f"\n✅ SUCCESS! Use this configuration in your script.")
    else:
        print(f"\n❌ CalDAV not working - use iCal file fallback")