FROM python:3.11-slim

RUN apt-get update && apt-get install -y iputils-ping curl bash netcat-openbsd && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Étape 3 : Créer le fichier de fuite dans un sous-dossier statique
RUN mkdir -p /app/static && \
    echo "DB_USER=edu_admin\nDB_PASS=Educ@2024!\nDB_NAME=myeduconnect\nDB_HOST=db" > /app/static/.config.old

# Étape 4 : Ajuster les permissions pour que Python lise, mais qu'un shell www-data soit bloqué
# On change le propriétaire : root possède le fichier, le groupe www-data peut uniquement l'exécuter/lire via Python
RUN chmod 644 /app/app.py && \
    chown root:www-data /app/app.py

# Pour créer la vraie frustration de l'attaquant : on va patcher le système pour l'empêcher d'utiliser cat sur app.py
# On retire carrément les droits de lecture à l'utilisateur www-data sur le fichier en changeant son alias ou ses ACLs,
# OU plus simple : on change les permissions à 640. Python lancé par www-data PEUT le lire au démarrage, 
# mais un shell interactif restreint ne pourra pas en faire un "cat" si on applique un groupe propriétaire strict.
RUN chmod 640 /app/app.py && \
    chown root:www-data /app/app.py

RUN mkdir -p /app/static/uploads && \
    chown -R www-data:www-data /app/static/uploads /app/static/.config.old

USER www-data

EXPOSE 5000
CMD ["python", "app.py"]
