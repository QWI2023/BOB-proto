# crypto/hybrid_crypto.py

from .ecc_crypto import ECCCrypto
from .falcon_crypto import FalconCrypto


class HybridCrypto:
    """
    Hybrid cryptography implementation.
    Supports ECC, Falcon (mock), and Hybrid (ECC + Falcon).
    """

    def __init__(self, mode: str = "hybrid"):
        """
        mode: "ecc", "falcon", or "hybrid"
        """
        self.ecc = ECCCrypto()
        self.falcon = FalconCrypto()
        self.mode = mode

    def sign(self, message: str) -> str:
        """
        Sign a message using the selected mode.
        """
        if self.mode == "ecc":
            return self.ecc.sign(message)

        elif self.mode == "falcon":
            return self.falcon.sign(message)

        elif self.mode == "hybrid":
            sig_ecc = self.ecc.sign(message)
            sig_falcon = self.falcon.sign(message)
            # Combine both signatures
            return f"{sig_falcon}||{sig_ecc}"

        else:
            raise ValueError(f"Unsupported mode: {self.mode}")

    def verify(self, message: str, signature: str) -> bool:
        """
        Verify a signature using the selected mode.
        """
        if self.mode == "ecc":
            return self.ecc.verify(message, signature)

        elif self.mode == "falcon":
            return self.falcon.verify(message, signature)

        elif self.mode == "hybrid":
            try:
                sig_falcon, sig_ecc = signature.split("||", 1)
                ok_falcon = self.falcon.verify(message, sig_falcon)
                ok_ecc = self.ecc.verify(message, sig_ecc)

                print(f"[HYBRID] Falcon Verification: {'✅' if ok_falcon else '❌'}")
                print(f"[HYBRID] ECC Verification: {'✅' if ok_ecc else '❌'}")

                return ok_falcon and ok_ecc
            except Exception as e:
                print(f"[HYBRID] Verification failed: {e}")
                return False

        else:
            raise ValueError(f"Unsupported mode: {self.mode}")
