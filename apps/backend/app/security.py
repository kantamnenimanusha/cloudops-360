"""Authentication/authorization helpers: JWT issue/verify, constant-time password check, login throttling."""
import hmac
import time
from collections import defaultdict, deque

import jwt

ROLES = {"viewer": 1, "admin": 2}


def authenticate(settings, username, password):
    """Return the role for valid credentials, else None. Constant-time comparison."""
    expected = {"viewer": settings.viewer_password, "admin": settings.admin_password}.get(username)
    if not expected or not password:
        return None
    return username if hmac.compare_digest(password.encode(), expected.encode()) else None


def create_token(settings, username, role, now=None):
    now = int(now if now is not None else time.time())
    claims = {"sub": username, "role": role, "iat": now, "exp": now + settings.token_ttl_minutes * 60}
    return jwt.encode(claims, settings.jwt_secret, algorithm="HS256")


def decode_token(settings, token):
    """Return claims or None if the token is invalid/expired."""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"], options={"require": ["exp", "sub", "role"]})
    except jwt.PyJWTError:
        return None


def has_role(claims, required):
    return bool(claims) and ROLES.get(claims.get("role"), 0) >= ROLES[required]


class LoginLimiter:
    """Allow at most `limit` failed attempts per `window` seconds per key (e.g. client IP)."""

    def __init__(self, limit=5, window=300):
        self.limit, self.window = limit, window
        self._failures = defaultdict(deque)

    def _prune(self, key, now):
        q = self._failures[key]
        while q and now - q[0] > self.window:
            q.popleft()
        return q

    def blocked(self, key, now=None):
        now = now if now is not None else time.time()
        return len(self._prune(key, now)) >= self.limit

    def record_failure(self, key, now=None):
        now = now if now is not None else time.time()
        self._prune(key, now).append(now)

    def reset(self, key):
        self._failures.pop(key, None)
