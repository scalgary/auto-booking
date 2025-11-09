#!/bin/bash

# Relance avec le .env
docker run -d --platform linux/amd64 \
  --name jupyter-selenium \
  -v $(pwd):/workspace \
  -w /workspace \
  -p 8888:8888 \
  --env-file .env \
  scalgary/selenium-env:latest \
  bash -c "pip install --root-user-action=ignore jupyter ipykernel && jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''"


echo "Attendre que Jupyter démarre..."
sleep 5
docker logs jupyter-selenium


# Arrête l'ancien
#docker stop jupyter-selenium
#docker rm jupyter-selenium


# http://localhost:8888
# docker-compose down && docker-compose up -d
# # Sur ton Mac (pas dans le container)

# Dans le container

