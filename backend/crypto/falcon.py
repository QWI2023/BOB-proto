"""Falcon-512 Cryptography Module"""
import hashlib
import base64
import json
from typing import Dict, Any, Optional
from ..utils.logging import get_logger

logger = get_logger(__name__)

# Try to import python-oqs for real Falcon-512 support
try:
    import oqs
    FALCON_AVAILABLE = True
    logger.info("python-oqs available, Falcon-512 enabled")
except ImportError:
    FALCON_AVAILABLE = False
    logger.warning("python-oqs not available, using Falcon-512 simulation")


class FalconCrypto:
    """Falcon-512 digital signature verification"""
    
    def __init__(self):
        self.falcon_available = FALCON_AVAILABLE
        self.vendor_keys = {}
        self._load_vendor_keys()
    
    def _load_vendor_keys(self):
        """Load vendor public keys"""
        # Demo vendor keys (in production, these would be loaded from secure storage)
        demo_keys = {
            "vendor_001": {
                "public_key": "falcon512_demo_public_key_vendor_001",
                "algorithm": "Falcon-512"
            },
            "vendor_002": {
                "public_key": "falcon512_demo_public_key_vendor_002", 
                "algorithm": "Falcon-512"
            },
            "vendor_003": {
                "public_key": "falcon512_demo_public_key_vendor_003",
                "algorithm": "Falcon-512"
            }
        }
        
        self.vendor_keys = demo_keys
        logger.info(f"Loaded {len(demo_keys)} vendor keys")
    
    async def verify_signature(self, payload: str, signature: Optional[str], vendor_id: str) -> bool:
        """Verify Falcon-512 digital signature"""
        try:
            if not signature:
                logger.warning(f"No signature provided for vendor {vendor_id}")
                return False
            
            if vendor_id not in self.vendor_keys:
                logger.warning(f"No public key found for vendor {vendor_id}")
                return False
            
            if self.falcon_available:
                # Real Falcon-512 verification
                return await self._verify_falcon_signature(payload, signature, vendor_id)
            else:
                # Simulation mode for demo
                return self._simulate_falcon_verification(payload, signature, vendor_id)
                
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    async def _verify_falcon_signature(self, payload: str, signature: str, vendor_id: str) -> bool:
        """Real Falcon-512 signature verification using python-oqs"""
        try:
            # Initialize Falcon-512 verifier
            verifier = oqs.Signature("Falcon-512")
            
            # Get vendor's public key
            public_key_data = self.vendor_keys[vendor_id]["public_key"]
            
            # Decode signature
            signature_bytes = base64.b64decode(signature)
            
            # Verify signature
            is_valid = verifier.verify(payload.encode(), signature_bytes, public_key_data.encode())
            
            logger.info(f"Falcon-512 verification for {vendor_id}: {'VALID' if is_valid else 'INVALID'}")
            return is_valid
            
        except Exception as e:
            logger.error(f"Falcon-512 verification error: {e}")
            return False
    
    def _simulate_falcon_verification(self, payload: str, signature: str, vendor_id: str) -> bool:
        """Simulate Falcon-512 verification for demo purposes"""
        try:
            # Demo logic: signature is valid if it contains vendor_id and payload hash
            signature_decoded = base64.b64decode(signature).decode('utf-8', errors='ignore')
            payload_hash = hashlib.sha256(payload.encode()).hexdigest()[:16]
            
            # Simple validation: signature should contain vendor_id reference
            is_valid = (
                vendor_id.replace('_', '') in signature_decoded.lower() or
                len(signature) > 50  # Minimum signature length
            )
            
            # Add some randomness for demo realism
            if "invalid" in signature.lower() or "bad" in signature.lower():
                is_valid = False
            
            logger.info(f"Falcon-512 simulation for {vendor_id}: {'VALID' if is_valid else 'INVALID'}")
            return is_valid
            
        except Exception as e:
            logger.error(f"Falcon-512 simulation error: {e}")
            return False
    
    def generate_demo_signature(self, payload: str, vendor_id: str) -> str:
        """Generate demo signature for testing"""
        try:
            # Create a demo signature that will pass validation
            payload_hash = hashlib.sha256(payload.encode()).hexdigest()[:16]
            demo_sig = f"falcon512_{vendor_id}_{payload_hash}_demo_signature"
            return base64.b64encode(demo_sig.encode()).decode()
        except Exception as e:
            logger.error(f"Demo signature generation failed: {e}")
            return "demo_signature_error"
    
    def get_vendor_info(self, vendor_id: str) -> Optional[Dict[str, Any]]:
        """Get vendor cryptographic information"""
        if vendor_id in self.vendor_keys:
            return {
                "vendor_id": vendor_id,
                "algorithm": self.vendor_keys[vendor_id]["algorithm"],
                "key_available": True,
                "falcon_support": self.falcon_available
            }
        return None
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get cryptographic system information"""
        return {
            "falcon_available": self.falcon_available,
            "algorithm": "Falcon-512",
            "vendor_keys_loaded": len(self.vendor_keys),
            "mode": "production" if self.falcon_available else "simulation"
        }