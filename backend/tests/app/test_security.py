from backend.app.security import hash_password


def test_hash_password_returns_sha256_string():
    hashed_password = hash_password("StrongPass123")

    assert hashed_password != "StrongPass123"
    assert len(hashed_password) == 64
