import anthropic
import hashlib


def hash_password_with_sha256(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def get_claude_explanation(password: str, hashed_password: str) -> str:
    """Get Claude's explanation of the hashing process."""
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"I just hashed the password '{password}' using "
                           f"SHA-256 and got: {hashed_password}. Can you "
                           f"briefly explain what SHA-256 hashing is and why "
                           f"it's used for passwords?"
            }
        ]
    )

    return message.content[0].text


def main():
    password = "MySecurePassword123!"

    hashed = hash_password_with_sha256(password)
    print(f"Original password: {password}")
    print(f"SHA-256 hash: {hashed}")
    print(f"Hash length: {len(hashed)} characters")
    print()

    explanation = get_claude_explanation(password, hashed)
    print("Claude's explanation:")
    print(explanation)


if __name__ == "__main__":
    main()
