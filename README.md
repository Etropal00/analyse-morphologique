# Programme d'analyse morphologique par IA

Application web pour **publier sur le web** une analyse morphologique à partir de photos, avec l’aide de l’IA. Vous fournissez une ou plusieurs photos, le programme les analyse et génère un **rapport complet** téléchargeable.

## Fonctionnalités

- **Upload** d’une ou plusieurs photos (glisser-déposer ou clic)
- **Analyse par IA** : OpenAI (cloud) ou **IA locale** (Ollama avec modèle vision : llava, llama3.2-vision, etc.)
- **Rapport complet** affiché à l’écran et **exportable en HTML** (téléchargement)

## Installation

1. **Cloner ou copier** le projet dans un dossier.

2. **Créer un environnement virtuel** (recommandé) :
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

4. **Choisir l’IA** (un seul des deux) :
   - **OpenAI (cloud)** : dans `.env`, mettez `OPENAI_API_KEY=votre_cle_api` ([créer une clé](https://platform.openai.com/api-keys)).
   - **IA locale (Ollama)** : installez [Ollama](https://ollama.com), lancez un modèle vision (ex. `ollama pull llava`), puis dans `.env` mettez :
     ```
     OPENAI_BASE_URL=http://localhost:11434/v1
     OPENAI_MODEL=llava
     ```
     (vous pouvez laisser `OPENAI_API_KEY` vide ou mettre `ollama`.)

## Lancer le programme

```bash
python app.py
```

Puis ouvrez dans le navigateur : **http://localhost:5000**

## Utilisation

1. Sur la page d’accueil, **ajoutez une ou plusieurs photos** (clic ou glisser-déposer).
2. Cliquez sur **« Lancer l’analyse »**.
3. Attendez la génération du rapport (quelques secondes).
4. Lisez le rapport à l’écran et cliquez sur **« Télécharger le rapport (HTML) »** pour le sauvegarder.

## Structure du projet

```
PROGRAMME DE MORPHOLOGIE/
├── app.py              # Serveur Flask + API analyse + export
├── requirements.txt    # Dépendances Python
├── .env.example        # Exemple de configuration (copier en .env)
├── README.md           # Ce fichier
├── static/
│   ├── index.html      # Interface web
│   └── reports/        # Rapports HTML générés (créé automatiquement)
└── uploads/            # Fichiers temporaires (créé automatiquement)
```

## Mettre l'application en ligne

**Guide de A à Z :** voir **[DEPLOY.md](DEPLOY.md)** (GitHub + Render.com, gratuit).

- En **local** : le programme tourne sur `http://localhost:5000`.
- Pour le rendre **accessible sur internet** (hébergement) :
  - Déployer sur un serveur (VPS, cloud) avec Python et les dépendances.
  - Configurer un reverse proxy (Nginx, Caddy) et éventuellement HTTPS.
  - Définir `OPENAI_API_KEY` dans les variables d’environnement du serveur.
  - En production, lancer avec un serveur WSGI (ex. Gunicorn) au lieu de `python app.py`.

## Notes

- **IA locale** : avec Ollama, les photos restent sur votre machine (aucun envoi sur internet).
- **OpenAI** : les images sont envoyées à leur API ; respectez leur politique de confidentialité.
- Limite d’upload : 50 Mo par requête (configurable dans `app.py`).
