# security/classical.py
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
import binascii, hashlib

class ClassicalCrypto:
    def __init__(self, public_key_path="public.pem"):
        with open(public_key_path, "rb") as f:
            self.public_key = serialization.load_pem_public_key(f.read())

    def verify_signature(self, message: str, hex_signature: str) -> bool:
        try:
            print("🔎 Server verifying message:", message)
            print("🔎 Server SHA256:", hashlib.sha256(message.encode()).hexdigest())

            signature = binascii.unhexlify(hex_signature)
            self.public_key.verify(signature, message.encode(), ec.ECDSA(hashes.SHA256()))
            print("✅ Signature valid")
            return True
        except (InvalidSignature, ValueError, binascii.Error) as e:
            print("❌ Verification failed:", str(e))
            return False
