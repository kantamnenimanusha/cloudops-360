from app.config import Settings
from app.security import LoginLimiter, authenticate, create_token, decode_token, has_role

S = Settings(jwt_secret="x" * 40, viewer_password="viewer-password-1", admin_password="admin-password-22", token_ttl_minutes=5)


def test_authenticate():
    assert authenticate(S, "viewer", "viewer-password-1") == "viewer"
    assert authenticate(S, "admin", "admin-password-22") == "admin"
    assert authenticate(S, "admin", "viewer-password-1") is None
    assert authenticate(S, "nobody", "x") is None
    assert authenticate(S, "viewer", "") is None


def test_token_roundtrip_and_role():
    claims = decode_token(S, create_token(S, "viewer", "viewer"))
    assert claims["sub"] == "viewer"
    assert has_role(claims, "viewer") and not has_role(claims, "admin")


def test_expired_and_tampered_tokens_rejected():
    assert decode_token(S, create_token(S, "viewer", "viewer", now=1000)) is None
    other = Settings(jwt_secret="y" * 40)
    assert decode_token(other, create_token(S, "viewer", "viewer")) is None
    assert decode_token(S, "garbage") is None


def test_settings_validation():
    assert Settings().validate()
    assert Settings(jwt_secret="x" * 32, viewer_password="a" * 12, admin_password="b" * 12).validate() == []
    assert Settings(jwt_secret="x" * 32, viewer_password="a" * 12, admin_password="a" * 12).validate()


def test_login_limiter():
    lim = LoginLimiter(limit=2, window=10)
    lim.record_failure("ip", now=0)
    assert not lim.blocked("ip", now=1)
    lim.record_failure("ip", now=2)
    assert lim.blocked("ip", now=3)
    assert not lim.blocked("ip", now=20)  # window passed
