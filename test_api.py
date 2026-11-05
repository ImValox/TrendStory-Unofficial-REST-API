"""
Script de test automatique pour l'API TrendStory.
Ce script teste tous les endpoints principaux directement.
"""

from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def print_section(title):
    print("\n" + "=" * 50)
    print(f"👉 {title}")
    print("=" * 50)

def main():
    print("🚀 Lancement des tests de l'API TrendStory...")

    # 1. Santé
    print_section("1. Test de santé de l'API")
    res = client.get("/")
    print(f"Status: {res.status_code}")
    print("Réponse:", json.dumps(res.json(), indent=2))

    # 2. Statut Auth
    print_section("2. Test du statut d'authentification")
    res = client.get("/auth/status")
    print(f"Status: {res.status_code}")
    print("Réponse:", json.dumps(res.json(), indent=2))

    # 3. Compte et Crédits
    print_section("3. Test du compte et des crédits")
    res_me = client.get("/account/me")
    print("Profil:", res_me.json().get("data", {}).get("email"))
    res_credits = client.get("/account/credits")
    print("Crédits:", json.dumps(res_credits.json().get("data", {}), indent=2))

    # 4. Liste des créations (vidéos)
    print_section("4. Test : Voir mes créations")
    res_videos = client.get("/videos")
    videos = res_videos.json().get("data", [])
    print(f"Nombre de vidéos trouvées: {len(videos)}")

    # 5. Modèles disponibles
    print_section("5. Test : Modèles IA disponibles dans le Studio")
    res_models = client.get("/studio/models")
    image_models = res_models.json().get("data", {}).get("image", [])
    print(f"Modèles d'image disponibles ({len(image_models)}):")
    for m in image_models[:3]:
        print(f"  - {m.get('name')} (clé: {m.get('key')}, coût: {m.get('credits')} crédits)")

    # 6. Test de génération
    print_section("6. Test : Lancer une génération")
    payload = {
        "prompt": "Un court fait insolite sur l'espace",
        "style": "cinematic",
        "duration_option": "30s"
    }
    res_gen = client.post("/videos/generate", json=payload)
    print(f"Status: {res_gen.status_code}")
    print("Réponse:", json.dumps(res_gen.json(), indent=2))

    print("\n" + "✅ Tous les tests sont terminés !")

if __name__ == "__main__":
    main()

