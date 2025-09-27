#!/bin/bash
LOG_FILE="postcreate.log"

echo "Starting post-create setup..." | tee $LOG_FILE
pip install --upgrade pip 2>&1 | tee -a $LOG_FILE
echo "pip upgrade completed" | tee -a $LOG_FILE
source ../git_history_functions.sh 2>&1 | tee -a $LOG_FILE
echo "git_history_functions.sh sourced" | tee -a $LOG_FILE
echo "Setup completed successfully" | tee -a $LOG_FILE