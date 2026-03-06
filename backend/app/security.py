"""Password hashing and verification helpers."""

import hashlib
import hmac
import secrets

# These constants define the password hashing algorithm configuration.
HASH_ALGORITHM = "sha256"
PBKDF2_ITERATIONS = 210_000
SALT_BYTES = 16


# Hash a password using PBKDF2 so only a derived value is stored.
def hash_password(password: str) -> str:
    # Generate a random salt per password to prevent rainbow table reuse.
    salt = secrets.token_bytes(SALT_BYTES)

    # Derive a secure hash from password + salt.
    derived_key = hashlib.pbkdf2_hmac(
        HASH_ALGORITHM,
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )

    # Serialize algorithm parameters and values for later verification.
    return f"{HASH_ALGORITHM}${PBKDF2_ITERATIONS}${salt.hex()}${derived_key.hex()}"


# Verify a plain password against the serialized PBKDF2 hash string.
def verify_password(password: str, stored_hash: str) -> bool:
    try:
        # Parse the stored hash into its components.
        algorithm, iterations_raw, salt_hex, expected_hex = stored_hash.split("$", maxsplit=3)
        iterations = int(iterations_raw)
        salt = bytes.fromhex(salt_hex)
    except (ValueError, TypeError):
        # Return False for malformed hash strings rather than raising.
        return False

    # Derive the hash for the provided password using stored parameters.
    candidate = hashlib.pbkdf2_hmac(
        algorithm,
        password.encode("utf-8"),
        salt,
        iterations,
    ).hex()

    # Use constant-time compare to reduce timing side-channel leakage.
    return hmac.compare_digest(candidate, expected_hex)
