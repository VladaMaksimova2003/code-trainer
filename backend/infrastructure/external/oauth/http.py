import httpx

from shared.exceptions import AuthError


async def post_form(url: str, data: dict[str, str]) -> dict:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, data=data)
    except httpx.HTTPError as exc:
        raise AuthError("OAuth provider is unavailable.") from exc

    if response.status_code >= 400:
        raise AuthError("OAuth provider rejected the authorization request.")

    try:
        payload = response.json()
    except ValueError as exc:
        raise AuthError("OAuth provider returned an invalid response.") from exc
    if not isinstance(payload, dict):
        raise AuthError("OAuth provider returned an invalid response.")
    return payload


async def get_json(url: str, *, headers: dict[str, str] | None = None) -> dict:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers or {})
    except httpx.HTTPError as exc:
        raise AuthError("OAuth provider is unavailable.") from exc

    if response.status_code >= 400:
        raise AuthError("OAuth provider rejected the profile request.")

    try:
        payload = response.json()
    except ValueError as exc:
        raise AuthError("OAuth provider returned an invalid response.") from exc
    if not isinstance(payload, dict):
        raise AuthError("OAuth provider returned an invalid response.")
    return payload
