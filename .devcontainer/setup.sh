#!/bin/bash
LOG_FILE="postcreate.log"

echo "Starting post-create setup..." | tee $LOG_FILE
pip install --upgrade pip 2>&1 | tee -a $LOG_FILE
echo "pip upgrade completed" | tee -a $LOG_FILE
echo "Setup completed successfully" | tee -a $LOG_FILE
# Fonction pour push avec historique ajouté au dernier commit
pip install --no-cache-dir jupyterlab ipywidgets notebook black pylint caldav pytz 2>&1 | tee -a $LOG_FILE
