#!/bin/bash

# Fonction pour push avec historique
git_push_with_history() {
    echo "🔄 Sauvegarde de l'historique des commandes..."
    
    # Forcer la sauvegarde de l'historique actuel
    history -a  # Ajoute les commandes de la session courante au fichier
    
    echo "=== PUSH SESSION - $(date '+%Y-%m-%d %H:%M:%S') ===" >> mes_commandes.txt
    history 50 >> mes_commandes.txt
    echo "================================================" >> mes_commandes.txt
    echo "" >> mes_commandes.txt
    
    git add mes_commandes.txt
    git commit -m "📋 Update command history $(date '+%Y-%m-%d %H:%M:%S')" || true
    git push "$@"
    
    echo "✅ Push terminé avec sauvegarde de l'historique"
}

# Alias
alias git_push='git_push_with_history'