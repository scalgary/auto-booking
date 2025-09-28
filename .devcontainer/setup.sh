#!/bin/bash
LOG_FILE="postcreate.log"

echo "Starting post-create setup..." | tee $LOG_FILE
pip install --upgrade pip 2>&1 | tee -a $LOG_FILE
echo "pip upgrade completed" | tee -a $LOG_FILE
source git_history_functions.sh 2>&1 | tee -a $LOG_FILE
echo "git_history_functions.sh sourced" | tee -a $LOG_FILE
echo "Setup completed successfully" | tee -a $LOG_FILE
type git_push >> $log_file
#!/bin/bash
# Fonction pour push avec historique ajouté au dernier commit
git_push_with_history() {
    echo "🔄 Sauvegarde de l'historique des commandes..."
    last_commit_msg=$(git log -1 --pretty=%B)

    # Forcer la sauvegarde de l'historique actuel
    history -a # Ajoute les commandes de la session courante au fichier
    
    echo "=== PUSH SESSION - $(date '+%Y-%m-%d %H:%M:%S') ===" >> mes_commandes.txt
    history 50 >> mes_commandes.txt
    echo "================================================" >> mes_commandes.txt
    echo "" >> mes_commandes.txt
    
    # Ajouter le fichier au dernier commit avec --amend
    git add mes_commandes.txt
    git commit --amend -m "$last_commit_msg" || true
    
    git push "$@"
    echo "✅ Bonjour Push terminé avec sauvegarde de l'historique ajoutée au dernier commit"
}

# Alias
alias git_push='git_push_with_history'