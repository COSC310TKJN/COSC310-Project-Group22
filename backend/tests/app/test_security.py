from backend.app.security import hash_password, verify_password


def test_hash_password_returns_sha256_string():
    hashed_password = hash_password("StrongPass123")

    assert hashed_password != "StrongPass123"
    assert len(hashed_password) == 64


def test_verify_password_matches_hash():
    hashed_password = hash_password("StrongPass123")

    assert verify_password("StrongPass123", hashed_password) is True
    assert verify_password("WrongPass123", hashed_password) is False
