import pytest

from application.auth.oauth.pkce import generate_pkce_pair
from application.auth.oauth.state_token import create_oauth_state_token, decode_oauth_state_token
from shared.exceptions import AuthError


def test_pkce_pair_is_valid_s256():
    verifier, challenge = generate_pkce_pair()
    assert 43 <= len(verifier) <= 128
    assert challenge
    assert "=" not in challenge


def test_oauth_state_roundtrip():
    secret = "x" * 32
    verifier, _ = generate_pkce_pair()
    token = create_oauth_state_token(
        provider="google",
        code_verifier=verifier,
        secret_key=secret,
    )
    payload = decode_oauth_state_token(token, secret_key=secret)
    assert payload["provider"] == "google"
    assert payload["code_verifier"] == verifier


def test_oauth_state_rejects_tampered_token():
    secret = "x" * 32
    verifier, _ = generate_pkce_pair()
    token = create_oauth_state_token(
        provider="vk",
        code_verifier=verifier,
        secret_key=secret,
    )
    with pytest.raises(AuthError):
        decode_oauth_state_token(token, secret_key="y" * 32)
