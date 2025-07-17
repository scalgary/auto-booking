#!/bin/bash
echo "🚀 Lancement de Jupyter Lab..."
echo "🔗 Jupyter sera accessible via l'onglet PORTS de Codespaces"
echo "📝 Notebooks disponibles dans le dossier 'notebooks/'"
echo ""
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --notebook-dir=notebooks
