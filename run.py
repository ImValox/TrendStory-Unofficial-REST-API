"""
Launcher for TrendStory Unofficial REST API Gateway.
"""

import os
import argparse
import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TrendStory API Gateway")
    parser.add_argument(
        "--no-docs",
        action="store_true",
        help="Désactiver la documentation Swagger et Redoc (/docs, /redoc, /openapi.json)",
    )
    parser.add_argument("--host", default=None, help="Hôte d'écoute (défaut: 127.0.0.1 ou env HOST)")
    parser.add_argument("--port", type=int, default=None, help="Port d'écoute (défaut: 8000 ou env PORT)")
    args = parser.parse_args()

    if args.no_docs:
        os.environ["ENABLE_DOCS"] = "false"

    host = args.host or os.getenv("HOST", "127.0.0.1")
    port = args.port or int(os.getenv("PORT", "8000"))
    docs_enabled = os.getenv("ENABLE_DOCS", "true").strip().lower() in ("true", "1", "yes")

    print(f"🚀 Démarrage de TrendStory API Gateway sur http://{host}:{port}")
    if docs_enabled:
        print(f"📖 Documentation Swagger interactive sur http://{host}:{port}/docs")
    else:
        print("🔒 Documentation Swagger/Redoc désactivée (/docs et /redoc inaccessibles)")

    uvicorn.run("app.main:app", host=host, port=port, reload=True)
