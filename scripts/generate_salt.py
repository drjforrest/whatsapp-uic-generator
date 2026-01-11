#!/usr/bin/env python3
"""
Generate a secure random salt for UIC hashing.

Run this script to generate a secure salt for your .env file.
"""
import secrets


def generate_salt(length: int = 32) -> str:
    """
    Generate a cryptographically secure random salt.

    Args:
        length: Number of bytes (will be longer when encoded)

    Returns:
        URL-safe base64-encoded random string
    """
    return secrets.token_urlsafe(length)


def main():
    """Generate and display a secure salt."""
    print("🔐 UIC Salt Generator")
    print("=" * 50)
    print()

    salt = generate_salt()

    print(f"Generated salt (length: {len(salt)} characters):")
    print()
    print(f"  {salt}")
    print()
    print("📋 Add this to your .env file:")
    print()
    print(f"  UIC_SALT=\"{salt}\"")
    print()
    print("⚠️  Keep this secret and never commit it to version control!")
    print()


if __name__ == "__main__":
    main()
