"""
FastAPI application entry point for TrendStory Unofficial API Gateway.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routes import auth, account, videos, studio

load_dotenv()

# Option pour activer / désactiver la documentation Swagger et Redoc
enable_docs = os.getenv("ENABLE_DOCS", "true").strip().lower() in ("true", "1", "yes")

app = FastAPI(
    title="TrendStory Unofficial REST API Gateway",
    description=(
        "Microservice passerelle REST non officiel pour https://www.trendstory.io.\n\n"
        "Fonctionnalités intégrées :\n"
        "- **Authentification** : Gestion des tokens Supabase et auto-refresh sans captcha.\n"
        "- **Compte & Crédits** : Consultation du solde, du plan et du profil.\n"
        "- **Vidéos & Générations** : Création de vidéos IA, suivi des rendus en cours, détails et statut.\n"
        "- **Téléchargement** : Récupération de l'URL finale MP4 directe.\n"
        "- **Studio & Outils** : Projets, modèles IA, musiques, personnages et génération rapide."
    ),
    version="1.0.0",
    docs_url="/docs" if enable_docs else None,
    redoc_url="/redoc" if enable_docs else None,
    openapi_url="/openapi.json" if enable_docs else None,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(account.router)
app.include_router(videos.router)
app.include_router(studio.router)


@app.get("/", tags=["Santé"])
async def root():
    return {
        "status": "online",
        "service": "TrendStory Unofficial REST API",
        "docs": "/docs" if enable_docs else "disabled",
        "version": "1.0.0",
    }
