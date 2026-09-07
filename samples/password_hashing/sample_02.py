import anthropic
import hashlib


def hash_password_with_sha256(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def get_hashing_explanation_from_claude(password: str) -> str:
    """Use Claude to explain the password hashing process."""
    client = anthropic.Anthropic()

    hashed = hash_password_with_sha256(password)

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"I hashed the password '{password}' using SHA-256 "
                           f"and got: {hashed}. Can you briefly explain what "
                           f"SHA-256 hashing is and why it's used for passwords?"
            }
        ]
    )

    return message.content[0].text


def main():
    test_passwords = ["mySecurePassword123", "hello", "P@ssw0rd!"]

    print("Password Hashing with SHA-256")
    print("=" * 50)

    for password in test_passwords:
        hashed = hash_password_with_sha256(password)
        print(f"\nPassword: {password}")
        print(f"SHA-256 Hash: {hashed}")

    print("\n" + "=" * 50)
    print("Getting explanation from Claude...")
    print("=" * 50)

    explanation = get_hashing_explanation_from_claude("example_password")
    print(explanation)


if __name__ == "__main__":
    main()
