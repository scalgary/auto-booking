#!/bin/bash

# Find files containing "{name}" in main branch
echo "=== Files containing 'CALDAV' in main branch ==="
git grep -l "CALDAV" main

echo -e "\n=== Detailed search with line numbers ==="
git grep -n "CALDAV" main

echo -e "\n=== History of files containing 'CALDAV' ==="
# Get list of files and show their history
git grep -l "CALDAV" main | while read file; do
    echo "--- History for: $file ---"
    git log --oneline --follow main -- "$file"
    echo ""
done

echo -e "\n=== Alternative: Combined history of all matching files ==="
git log --oneline main -- $(git grep -l "CALDAV" main | tr '\n' ' ')