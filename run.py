"""
Launcher for TrendStory Unofficial REST API Gateway.
"""

import os
import socket
import argparse
import uvicorn
from dotenv import load_dotenv

load_dotenv()


def get_local_ip() -> str:
    """Tente de récupérer l'adresse IP locale de la machine sur le réseau."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TrendStory API Gateway")
    parser.add_argument(
        "--no-docs",
        action="store_true",
        help="Désactiver la documentation Swagger et Redoc (/docs, /redoc, /openapi.json)",
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Hôte d'écoute (ex: 0.0.0.0 pour réseau local, défaut: env HOST ou 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port d'écoute (défaut: 8000 ou env PORT)",
    )
    args = parser.parse_args()

    if args.no_docs:
        os.environ["ENABLE_DOCS"] = "false"

    # Par défaut 0.0.0.0 pour être accessible sur le réseau local
    host = args.host or os.getenv("HOST", "0.0.0.0")
    port = args.port or int(os.getenv("PORT", "8000"))
    docs_enabled = os.getenv("ENABLE_DOCS", "true").strip().lower() in ("true", "1", "yes")

    local_ip = get_local_ip()

    print("\n" + "=" * 60)
    print("🚀 Démarrage de TrendStory API Gateway")
    print("=" * 60)
    print(f"👉 Local (cette machine) :      http://localhost:{port}")
    if host in ("0.0.0.0", "::"):
        print(f"👉 Réseau local (autres appareils) : http://{local_ip}:{port}")
    else:
        print(f"👉 Écoute spécifique sur :        http://{host}:{port}")

    if docs_enabled:
        print(f"📖 Documentation Swagger :        http://{local_ip if host == '0.0.0.0' else host}:{port}/docs")
    else:
        print("🔒 Documentation Swagger/Redoc désactivée")
    print("=" * 60 + "\n")

    uvicorn.run("app.main:app", host=host, port=port, reload=True)
