import string
import random

def generate_secret_key():
    chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(random.choice(chars) for _ in range(50))

if __name__ == "__main__":
    secret_key = generate_secret_key()
    print(f"SECRET_KEY={secret_key}")
    print(f"\nCopy this secret key for your Render.com environment variables:")
    print(f"SECRET_KEY={secret_key}")
