#!/usr/bin/env python3
"""
Script Python pour imprimer SEULEMENT les URLs
Usage: python3 execution.py "date" "time"
"""

import os
import sys
from datetime import datetime

def main():
    """Fonction principale - Imprime seulement les URLs"""
    
    print("=== DÉMARRAGE DU SCRIPT ===")
    print(f"Timestamp: {datetime.now()}")
    
    # Récupérer les arguments
    if len(sys.argv) >= 3:
        date_arg = sys.argv[1]
        time_arg = sys.argv[2]
        print(f"Arguments reçus - Date: {date_arg}, Heure: {time_arg}")
    else:
        print("Arguments manquants. Usage: python3 execution.py 'date' 'heure'")
        date_arg = "Non fourni"
        time_arg = "Non fourni"
    
    print()
    print("=== AFFICHAGE DES URLs UNIQUEMENT ===")
    
    # Récupérer SEULEMENT les URLs
    logon_url = os.getenv('YOUR_SECRET_LOGON_URL')
    planning_url = os.getenv('YOUR_SECRET_PLANNING_URL')
    login_url = os.getenv('YOUR_SECRET_LOGIN_URL')
    
    print(f"LOGON_URL: {logon_url}")
    print(f"PLANNING_URL: {planning_url}")
    print(f"LOGIN_URL: {login_url}")
    print()
    
    # Vérifier les autres secrets SANS les afficher
    email = os.getenv('YOUR_SECRET_EMAIL')
    password = os.getenv('YOUR_SECRET_PASSWORD')
    my_name = os.getenv('YOUR_SECRET_My_NAME')
    
    # Status des autres secrets (sans les révéler)
    print("=== STATUS DES AUTRES SECRETS (MASQUÉS) ===")
    print(f"EMAIL: {'✅ DÉFINI' if email else '❌ MANQUANT'}")
    print(f"PASSWORD: {'✅ DÉFINI' if password else '❌ MANQUANT'}")
    print(f"MY_NAME: {'✅ DÉFINI' if my_name else '❌ MANQUANT'}")
    print()
    
    # Vérifier si des URLs manquent
    urls = {
        'LOGON_URL': logon_url,
        'PLANNING_URL': planning_url,
        'LOGIN_URL': login_url
    }
    
    missing_urls = [name for name, value in urls.items() if not value]
    
    if missing_urls:
        print(f"❌ URLs MANQUANTES: {', '.join(missing_urls)}")
    else:
        print("✅ TOUTES LES URLs SONT DÉFINIES")
    
    print()
    print("=== INFORMATIONS DES URLs ===")
    for name, value in urls.items():
        if value:
            print(f"{name}: longueur = {len(value)} caractères")
        else:
            print(f"{name}: NON DÉFINI")
    
    # Créer un fichier de log avec les URLs seulement
    print()
    print("📝 Création du fichier de log...")
    
    with open('execution_log.txt', 'w') as f:
        f.write("=== LOG DES URLs UNIQUEMENT ===\n")
        f.write(f"Timestamp: {datetime.now()}\n")
        f.write(f"Date argument: {date_arg}\n")
        f.write(f"Heure argument: {time_arg}\n")
        f.write("\n=== URLs COMPLÈTES ===\n")
        f.write(f"LOGON_URL: {logon_url}\n")
        f.write(f"PLANNING_URL: {planning_url}\n")
        f.write(f"LOGIN_URL: {login_url}\n")
        f.write(f"\n=== STATUS AUTRES SECRETS ===\n")
        f.write(f"EMAIL: {'DÉFINI' if email else 'MANQUANT'}\n")
        f.write(f"PASSWORD: {'DÉFINI' if password else 'MANQUANT'}\n")
        f.write(f"MY_NAME: {'DÉFINI' if my_name else 'MANQUANT'}\n")
        f.write(f"\nURLs manquantes: {missing_urls}\n")
        f.write("Status: COMPLETED\n")
    
    print("✅ Log sauvegardé dans 'execution_log.txt'")
    print()
    print("🔗 SCRIPT TERMINÉ - SEULES LES URLs ONT ÉTÉ AFFICHÉES")
    
    # Exit avec erreur si des URLs manquent
    if missing_urls:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
