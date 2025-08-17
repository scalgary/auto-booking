
import os


import sys

# Récupérer les arguments
if len(sys.argv) != 3:
    print("Usage: python mon_script.py <variable1> <variable2> ")
    sys.exit(1)

TARGET_DATE = sys.argv[1]
COURSE_TYPE = "Indoor Pickleball Intermediate"
TARGET_TIME = sys.argv[2]

print(f"Variable 1: {TARGET_DATE}")
#print(f"Variable 2: {COURSE_TYPE}")
print(f"Variable 2: {TARGET_TIME}")

# Modifiez juste ces valeurs :
#TARGET_DATE = "19-Aug-25"  # ← VOTRE DATE ICI
#COURSE_TYPE = "Indoor Pickleball Intermediate"
#TARGET_TIME = "4:30"





logon_url = os.environ.get("YOUR_SECRET_LOGON_URL")
if not isinstance(logon_url, str) or not logon_url:
    raise ValueError("YOUR_SECRET_LOGON_URL is missing or not a string")
