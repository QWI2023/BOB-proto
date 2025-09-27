import os

class FalconCrypto:
    """
    Mock Falcon-512 PQC implementation.
    For demo purposes, this just simulates sign/verify,
    but now loads keys from mock files to look realistic.
    """

    def __init__(self):
        self.private_key_path = "keys/falcon_private.mock"
        self.public_key_path = "keys/falcon_public.mock"

        # Load keys (mock text)
        self.private_key = self._load_key(self.private_key_path, "mock_falcon_private_key")
        self.public_key = self._load_key(self.public_key_path, "mock_falcon_public_key")

    def _load_key(self, path, default_value):
        """Load key from file, or create it if missing."""
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(default_value)
        with open(path, "r") as f:
            return f.read().strip()

    def sign(self, message: str) -> str:
        """
        Produce a mock Falcon signature.
        For demo: reverse the string and include the private key tag.
        """
        return f"falcon_sig::{self.private_key}::{message[::-1]}"

    def verify(self, message: str, signature: str) -> bool:
        """
        Verify the mock Falcon signature using the stored public key.
        """
        expected = f"falcon_sig::{self.private_key}::{message[::-1]}"
        return signature == expected
