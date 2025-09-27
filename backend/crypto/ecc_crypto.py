import binascii
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

class ECCCrypto:
    def __init__(self):
        self.private_key_path = "keys/ecc_private.pem"
        self.public_key_path = "keys/ecc_public.pem"

    def load_private_key(self):
        with open(self.private_key_path, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)

    def load_public_key(self):
        with open(self.public_key_path, "rb") as f:
            return serialization.load_pem_public_key(f.read())

    def sign(self, message: str) -> str:
        private_key = self.load_private_key()
        signature = private_key.sign(
            message.encode(),
            ec.ECDSA(hashes.SHA256())
        )
        return binascii.hexlify(signature).decode()

    def verify(self, message: str, signature_hex: str) -> bool:
        public_key = self.load_public_key()
        signature = binascii.unhexlify(signature_hex)
        try:
            public_key.verify(
                signature,
                message.encode(),
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except Exception:
            return False
