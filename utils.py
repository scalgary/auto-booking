from datetime import datetime

def check_date(target_date, today=None):
    """
    Vérifie si target_date est une date valide au format "%d-%b-%y" et effectue les tests demandés.
    Retourne (possible, next_week).
    """
    if not isinstance(target_date, str):
        raise TypeError("target_date doit être une chaîne de caractères au format '%d-%b-%y'.")

    try:
        your_date = datetime.strptime(target_date, "%d-%b-%y")
    except Exception as e:
        raise ValueError(f"target_date '{target_date}' n'est pas au format '%d-%b-%y' (ex: 07-Sep-25)") from e

    if today is None:
        today = datetime.now()
    elif not isinstance(today, datetime):
        raise TypeError("today doit être un objet datetime ou None.")

    days_difference = (your_date.date() - today.date()).days
    is_after_today = days_difference > 0
    less_7_days = 0 <= days_difference <= 7
    next_week = days_difference == 7
    possible = less_7_days
    return possible, next_week