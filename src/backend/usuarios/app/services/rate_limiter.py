import time
from collections import defaultdict


class LoginRateLimiter:
    """
    In-memory rate limiter for login attempts keyed by email.
    5 failures in a 5-minute window trigger a 15-minute lockout.
    Resets on successful login.
    """

    def __init__(
        self,
        max_attempts: int = 5,
        window_seconds: int = 300,
        lockout_seconds: int = 900,
    ) -> None:
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._lockout_seconds = lockout_seconds
        self._attempts: dict[str, list[float]] = defaultdict(list)
        self._lockouts: dict[str, float] = {}

    def is_locked(self, key: str) -> bool:
        unlock_at = self._lockouts.get(key)
        if unlock_at is None:
            return False
        if time.monotonic() >= unlock_at:
            del self._lockouts[key]
            self._attempts.pop(key, None)
            return False
        return True

    def record_failure(self, key: str) -> None:
        now = time.monotonic()
        window_start = now - self._window_seconds
        self._attempts[key] = [t for t in self._attempts[key] if t >= window_start]
        self._attempts[key].append(now)
        if len(self._attempts[key]) >= self._max_attempts:
            self._lockouts[key] = now + self._lockout_seconds
            self._attempts.pop(key, None)

    def reset(self, key: str) -> None:
        self._attempts.pop(key, None)
        self._lockouts.pop(key, None)


# Module-level singleton shared across requests in the same process.
login_rate_limiter = LoginRateLimiter()
