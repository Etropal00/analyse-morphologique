# Mettre l’application en ligne (de A à Z)

Ce guide vous permet de déployer **Analyse morphologique** sur internet avec **GitHub** + **Render.com** (gratuit).

---

## Étape 1 : Installer Git (si besoin)

1. Téléchargez Git : https://git-scm.com/download/win  
2. Installez-le en laissant les options par défaut.  
3. Ouvrez **PowerShell** ou **Invite de commandes** et tapez : `git --version` pour vérifier.

---

## Étape 2 : Créer un compte GitHub

1. Allez sur https://github.com  
2. Cliquez sur **Sign up** et créez un compte (gratuit).

---

## Étape 3 : Créer un dépôt GitHub et envoyer le code

1. Sur GitHub, cliquez sur **+** (en haut à droite) → **New repository**.  
2. Donnez un nom (ex. `analyse-morphologique`), laissez **Public**, ne cochez pas « Add a README ».  
3. Cliquez sur **Create repository**.  
4. Sur votre PC, ouvrez **PowerShell** et allez dans le dossier du projet :
   ```powershell
   cd "c:\ai\PROGRAMME DE MORPHOLOGIE"
   ```
5. Initialisez Git et envoyez le code (remplacez `VOTRE_UTILISATEUR` par votre nom d’utilisateur GitHub) :
   ```powershell
   git init
   git add .
   git commit -m "Première version - analyse morphologique"
   git branch -M main
   git remote add origin https://github.com/VOTRE_UTILISATEUR/analyse-morphologique.git
   git push -u origin main
   ```
6. Si GitHub demande de vous connecter, utilisez un **Personal Access Token** comme mot de passe :  
   GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Generate new token** (cochez au moins `repo`), copiez le token et collez-le quand Git demande le mot de passe.

---

## Étape 4 : Créer un compte Render

1. Allez sur https://render.com  
2. Cliquez sur **Get Started** et connectez-vous avec votre compte **GitHub** (c’est le plus simple).

---

## Étape 5 : Créer le service web sur Render

1. Dans le tableau de bord Render, cliquez sur **New +** → **Web Service**.  
2. Choisissez **Connect a repository** et sélectionnez votre dépôt `analyse-morphologique` (autorisez Render si demandé).  
3. Renseignez :
   - **Name** : `analyse-morphologique` (ou un autre nom)
   - **Region** : choisissez la plus proche (ex. Frankfurt)
   - **Branch** : `main`
   - **Runtime** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn --bind 0.0.0.0:$PORT app:app`
4. Cliquez sur **Advanced** et ajoutez les **Environment Variables** :
   - **Key** : `OPENAI_API_KEY`  
   - **Value** : votre clé API OpenAI (commence par `sk-...`)  
   (Ne mettez pas d’espaces. Si vous utilisez une IA locale, vous mettrez plutôt `OPENAI_BASE_URL` et `OPENAI_MODEL`.)
5. Cliquez sur **Create Web Service**.  
6. Render va construire et lancer l’app (2–5 minutes). Quand le statut est **Live**, votre site est en ligne.

---

## Étape 6 : Ouvrir votre site

- L’URL sera du type : **https://analyse-morphologique-xxxx.onrender.com**  
- Elle s’affiche en haut de la page du service sur Render. Cliquez dessus pour ouvrir l’application.

---

## Mises à jour (après modification du code)

Dans le dossier du projet sur votre PC :

```powershell
cd "c:\ai\PROGRAMME DE MORPHOLOGIE"
git add .
git commit -m "Description des changements"
git push
```

Render redéploiera automatiquement après chaque `git push`.

---

## Important

- **Clé API** : ne mettez jamais votre clé OpenAI dans le code. Gardez-la uniquement dans les **Environment Variables** sur Render.  
- **Gratuit** : le plan gratuit Render met le service en veille après ~15 min sans visite ; la première visite peut prendre 1–2 min pour redémarrer.  
- **Fichier `.env`** : il n’est pas envoyé sur GitHub (il est dans `.gitignore`). La clé est uniquement sur Render.

---

## Dépannage

- **Build failed** : vérifiez que `requirements.txt` et `Procfile` sont bien à la racine du dépôt.  
- **Application Error** : vérifiez que `OPENAI_API_KEY` est bien définie dans Render (Environment).  
- **Timeout** : sur le plan gratuit, les requêtes longues (analyse d’images) peuvent être limitées ; si ça coupe, réessayez avec une seule photo.
