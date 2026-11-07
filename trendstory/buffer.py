"""
Buffer API integration for posting videos to social channels (TikTok, Instagram, etc.).
Uses Buffer's modern GraphQL API (https://api.buffer.com).
"""

import os
from typing import Any, Dict, List, Optional
import httpx

BUFFER_GRAPHQL_ENDPOINT = "https://api.buffer.com"


class BufferApiError(Exception):
    def __init__(self, message: str, status_code: int = 500, details: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details


class BufferClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("BUFFER_API_KEY")

    def _get_headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise BufferApiError(
                "Clé API Buffer non configurée. Définissez BUFFER_API_KEY dans le .env ou passez-la en paramètre.",
                status_code=400,
            )
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def get_channels(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste de tous vos canaux connectés sur Buffer (ex: comptes TikTok, Instagram).
        """
        query = """
        query GetChannels {
            account {
                organizations {
                    id
                    name
                    channels {
                        id
                        name
                        service
                        avatarUrl
                    }
                }
            }
        }
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                BUFFER_GRAPHQL_ENDPOINT,
                headers=self._get_headers(),
                json={"query": query},
            )

            if resp.status_code != 200:
                raise BufferApiError(
                    f"Erreur Buffer ({resp.status_code}): {resp.text}",
                    status_code=resp.status_code,
                )

            data = resp.json()
            if "errors" in data and data["errors"]:
                raise BufferApiError(
                    f"Erreur GraphQL Buffer: {data['errors'][0].get('message')}",
                    details=data["errors"],
                )

            channels = []
            orgs = (
                data.get("data", {})
                .get("account", {})
                .get("organizations", [])
            )
            for org in orgs:
                for ch in org.get("channels", []):
                    channels.append(ch)
            return channels

    async def publish_video(
        self,
        channel_id: str,
        video_url: str,
        text: str,
        post_now: bool = True,
    ) -> Dict[str, Any]:
        """
        Publie ou planifie une vidéo sur un canal (ex: TikTok) via son URL publique/signée.
        """
        mutation = """
        mutation CreatePost($input: CreatePostInput!) {
            createPost(input: $input) {
                ... on PostActionSuccess {
                    post {
                        id
                        status
                        text
                    }
                }
                ... on MutationError {
                    message
                }
            }
        }
        """
        variables = {
            "input": {
                "text": text,
                "channelId": channel_id,
                "schedulingType": "now" if post_now else "automatic",
                "mode": "postNow" if post_now else "addToQueue",
                "assets": [
                    {
                        "video": {
                            "url": video_url
                        }
                    }
                ],
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                BUFFER_GRAPHQL_ENDPOINT,
                headers=self._get_headers(),
                json={"query": mutation, "variables": variables},
            )

            if resp.status_code != 200:
                raise BufferApiError(
                    f"Erreur Buffer ({resp.status_code}): {resp.text}",
                    status_code=resp.status_code,
                )

            data = resp.json()
            if "errors" in data and data["errors"]:
                raise BufferApiError(
                    f"Erreur GraphQL Buffer: {data['errors'][0].get('message')}",
                    details=data["errors"],
                )

            create_post = data.get("data", {}).get("createPost", {})
            if "message" in create_post and "post" not in create_post:
                raise BufferApiError(
                    f"Erreur Buffer ({create_post.get('__typename', 'MutationError')}): {create_post.get('message')}",
                    details=create_post,
                )

            return create_post

