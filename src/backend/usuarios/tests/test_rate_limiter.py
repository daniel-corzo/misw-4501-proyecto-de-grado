import time
import pytest
from app.services.rate_limiter import LoginRateLimiter


def make_limiter(max_attempts=3, window_seconds=60, lockout_seconds=120):
    return LoginRateLimiter(
        max_attempts=max_attempts,
        window_seconds=window_seconds,
        lockout_seconds=lockout_seconds,
    )


def test_not_locked_initially():
    limiter = make_limiter()
    assert not limiter.is_locked("user@example.com")


def test_locks_after_max_attempts():
    limiter = make_limiter(max_attempts=3)
    for _ in range(3):
        limiter.record_failure("user@example.com")
    assert limiter.is_locked("user@example.com")


def test_not_locked_before_max_attempts():
    limiter = make_limiter(max_attempts=3)
    limiter.record_failure("user@example.com")
    limiter.record_failure("user@example.com")
    assert not limiter.is_locked("user@example.com")


def test_reset_clears_lockout():
    limiter = make_limiter(max_attempts=3)
    for _ in range(3):
        limiter.record_failure("user@example.com")
    assert limiter.is_locked("user@example.com")
    limiter.reset("user@example.com")
    assert not limiter.is_locked("user@example.com")


def test_reset_clears_attempt_history():
    limiter = make_limiter(max_attempts=3)
    limiter.record_failure("user@example.com")
    limiter.reset("user@example.com")
    # After reset, 2 more failures should not lock
    limiter.record_failure("user@example.com")
    limiter.record_failure("user@example.com")
    assert not limiter.is_locked("user@example.com")


def test_different_emails_are_independent():
    limiter = make_limiter(max_attempts=3)
    for _ in range(3):
        limiter.record_failure("alice@example.com")
    assert limiter.is_locked("alice@example.com")
    assert not limiter.is_locked("bob@example.com")


def test_lockout_expires():
    limiter = LoginRateLimiter(max_attempts=2, window_seconds=60, lockout_seconds=0)
    for _ in range(2):
        limiter.record_failure("user@example.com")
    # lockout_seconds=0 means it expires immediately
    time.sleep(0.01)
    assert not limiter.is_locked("user@example.com")
