#!/usr/bin/env python3
# test_caldav.py - Test minimal pour GitHub Actions

import os
from caldav import DAVClient

def test_caldav_only():
    user = os.getenv("CALDAV_USER")
    password = os.getenv("CALDAV_PASSWORD")
    
    print(f"🔍 CALDAV_USER: {user}")
    print(f"🔍 CALDAV_PASSWORD: {'*' * len(password) if password else 'MISSING'}")
    
    if not user or not password:
        print("❌ CALDAV credentials missing!")
        return False
    
    try:
        print("🔗 Testing CalDAV connection...")
        client = DAVClient(
            url='https://caldav.icloud.com',
            username=user,
            password=password
        )
        
        principal = client.principal()
        calendars = principal.calendars()
        
        print(f"✅ SUCCESS! Found {len(calendars)} calendars:")
        for cal in calendars:
            print(f"  - {cal.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    test_caldav_only()