from cryptography.fernet import Fernet
from backend.app.config import settings
import base64

def get_cipher():
    key = settings.ENCRYPTION_KEY
    if len(key) != 44:
        key = base64.urlsafe_b64encode(b"0" * 32).decode('utf-8')
    return Fernet(key.encode('utf-8'))

def encrypt(plaintext: str) -> str:
    if not plaintext:
        return ""
    cipher = get_cipher()
    return cipher.encrypt(plaintext.encode('utf-8')).decode('utf-8')

def decrypt(ciphertext: str) -> str:
    if not ciphertext:
        return ""
    cipher = get_cipher()
    return cipher.decrypt(ciphertext.encode('utf-8')).decode('utf-8')
