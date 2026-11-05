# TrendStory Unofficial REST API Gateway 🎬

Microservice REST passerelle (Gateway) non officiel pour automatiser la plateforme de génération de vidéos IA [TrendStory](https://www.trendstory.io).

Développé en **Python (FastAPI + HTTPX)** avec persistance automatique de la session et auto-renouvellement des jetons JWT.

---

## ⚡ Fonctionnalités

* 🔐 **Authentification transparente** : Support du login classique et **auto-refresh sans captcha** via le jeton de renouvellement Supabase (`refresh_token`).
* 💳 **Compte & Crédits** : Consultation de votre solde (`plan_credits`, `topup_credits`, `total`) et de votre profil.
* 🎥 **Génération de Vidéos IA** : Lancement d'une vidéo complète (script, voix, scènes, animations, sous-titres) à partir d'un simple prompt texte.
* 📋 **Mes Créations** : Listing de toutes vos vidéos générées et suivi des rendus en cours (`pending`).
* 📥 **Téléchargement direct** : Récupération immédiate du lien de téléchargement direct (.MP4 haute résolution).
* 🎨 **Studio & Outils créatifs** : Exploration des modèles IA (Nano Banana, Grok, Kling, Flux), gestion des projets studio, bibliothèque musicale et presets de personnages (ex: Fraisita).

---

## 🚀 Démarrage Rapide

### 1. Prérequis
- Python 3.10 ou supérieur

### 2. Installation
L'environnement virtuel `.venv` est déjà configuré dans le dossier. Si vous repartez de zéro :
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Lancement du microservice
```bash
# Lancement standard (avec documentation Swagger sur /docs) :
.venv/bin/python run.py

# Lancement sans la documentation (/docs et /redoc désactivés) :
.venv/bin/python run.py --no-docs
```

Le serveur démarrera sur **http://127.0.0.1:8000**.

> 💡 **Astuce** : Vous pouvez aussi désactiver la doc de façon permanente en ajoutant `ENABLE_DOCS=false` dans votre fichier `.env`.

### 4. Documentation Swagger Interactive
Ouvrez votre navigateur sur :
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** (ou `/redoc`)

Vous pouvez tester directement chaque endpoint depuis l'interface web !

---

## 📚 Endpoints Disponibles

### 🔐 Authentification (`/auth`)
* `POST /auth/login` : Connexion avec email et mot de passe (optionnellement avec un captcha Turnstile si le site l'exige).
* `POST /auth/refresh` : Renouvelle le jeton d'accès sans captcha.
* `GET /auth/status` : Indique si le client est actuellement authentifié.

### 👤 Compte & Crédits (`/account`)
* `GET /account/me` : Récupère le profil du compte (id, email, plan, droits d'accès).
* `GET /account/credits` : Affiche le solde des crédits disponibles.

### 🎬 Vidéos (`/videos`)
* `GET /videos` : **Voir mes créations** (liste de toutes les vidéos rendues).
* `GET /videos/pending` : Liste des vidéos actuellement en file d'attente ou en rendu.
* `POST /videos/generate` : **Lancer une génération** vidéo complète.
* `GET /videos/{video_id}` : Obtenir le statut et les détails d'une vidéo.
* `GET /videos/{video_id}/download-url` : **Récupérer l'URL finale** signée (MP4).
* `POST /videos/{video_id}/cancel` : Annuler un rendu en cours.

### 🎨 Studio & Modèles (`/studio`)
* `GET /studio/projects` : Liste de vos projets du Studio.
* `POST /studio/projects` : Créer un nouveau projet Studio.
* `GET /studio/projects/{id}` : Détails d'un projet et de ses scènes.
* `GET /studio/models` : Modèles d'images et vidéos disponibles et leurs coûts.
* `POST /studio/fast-video` : Génération rapide d'un clip vidéo unique.
* `GET /studio/character-presets` : Liste des personnages IA cohérents.
* `GET /studio/music` : Pistes musicales de fond disponibles.

---

## 💻 Exemples d'utilisation

### Lancer une génération de vidéo (cURL)

```bash
curl -X POST "http://localhost:8000/videos/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Top 5 des faits insolites sur les chats que tu ignorais",
    "style": "cinematic",
    "video_model": "kling-v1",
    "duration_option": "30s",
    "locale": "fr"
  }'
```

### Récupérer l'URL finale de téléchargement (cURL)

```bash
curl -s "http://localhost:8000/videos/VOTRE_VIDEO_ID/download-url"
```

### Utilisation directe en Python (SDK)

Si vous voulez utiliser la librairie Python directement sans lancer le serveur REST :

```python
import asyncio
from trendstory import TrendStoryClient

async def main():
    client = TrendStoryClient()
    
    # 1. Vérifier le profil et les crédits
    me = await client.get_me()
    print("Connecté en tant que:", me["email"])
    
    # 2. Lister les vidéos existantes
    videos = await client.list_videos()
    print(f"Vous avez {len(videos)} vidéos générées.")
    
    # 3. Lancer une vidéo (si crédits > 0)
    # job = await client.generate_video(prompt="Une histoire incroyable")
    # print("ID vidéo:", job["video"]["id"])

asyncio.run(main())
```

---

## 🔒 Gestion des Sessions

La session est persistée localement dans le fichier `session.json`.
Le client s'occupe automatiquement de :
1. Détecter l'expiration du token JWT.
2. Contacter l'endpoint Supabase pour obtenir un nouveau token via le `refresh_token` (aucun captcha requis).
3. Re-sauvegarder la session à jour.

