import json

import pytest

from application.auth.oauth.pkce import generate_pkce_pair
from application.auth.oauth.state_store import consume_oauth_state, create_oauth_state
from shared.exceptions import AuthError


class _FakeRedis:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def setex(self, key: str, _ttl: int, value: str) -> None:
        self._data[key] = value

    def get(self, key: str) -> str | None:
        return self._data.get(key)

    def delete(self, key: str) -> None:
        self._data.pop(key, None)


@pytest.fixture
def fake_redis(monkeypatch):
    client = _FakeRedis()
    monkeypatch.setattr("application.auth.oauth.state_store._redis_client", lambda: client)
    return client


def test_oauth_state_store_roundtrip(fake_redis):
    verifier, _ = generate_pkce_pair()
    state = create_oauth_state(provider="google", code_verifier=verifier)
    payload = consume_oauth_state(state)
    assert payload == {"provider": "google", "code_verifier": verifier}


def test_oauth_state_store_is_one_time(fake_redis):
    verifier, _ = generate_pkce_pair()
    state = create_oauth_state(provider="vk", code_verifier=verifier)
    consume_oauth_state(state)
    with pytest.raises(AuthError, match="Invalid OAuth state"):
        consume_oauth_state(state)


def test_oauth_state_store_rejects_unknown(fake_redis):
    with pytest.raises(AuthError, match="Invalid OAuth state"):
        consume_oauth_state("missing-state-token")
