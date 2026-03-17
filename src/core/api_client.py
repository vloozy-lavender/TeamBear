import requests
import hmac
import hashlib
import time
import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv('config/.env')
logger = logging.getLogger(__name__)

# API Configuration
BASE_URL = "https://mock-api.roostoo.com"
API_KEY = os.getenv('ROOSTOO_API_KEY')
SECRET_KEY = os.getenv('ROOSTOO_API_SECRET')

logger.info(f"API Key loaded: {API_KEY[:10]}...{API_KEY[-10:] if len(API_KEY) > 20 else '***'}")
logger.info(f"Secret Key loaded: {SECRET_KEY[:10]}...{SECRET_KEY[-10:] if len(SECRET_KEY) > 20 else '***'}")

def _get_timestamp() -> str:
    """Return 13-digit millisecond timestamp as string."""
    return str(int(time.time() * 1000))

def _generate_signature_v1(params: Dict[str, str]) -> str:
    """
    Method 1: Sort params, join with &, HMAC SHA256 with secret.
    This is the most common format.
    """
    sorted_keys = sorted(params.keys())
    param_string = "&".join(f"{k}={params[k]}" for k in sorted_keys)
    logger.debug(f"V1 param string: {param_string}")
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        param_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

def _generate_signature_v2(params: Dict[str, str]) -> str:
    """
    Method 2: Include API key in signature (some exchanges require this).
    """
    sorted_keys = sorted(params.keys())
    param_string = "&".join(f"{k}={params[k]}" for k in sorted_keys)
    message = f"{param_string}&apiKey={API_KEY}"
    logger.debug(f"V2 param string: {message}")
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

def _generate_signature_v3(params: Dict[str, str]) -> str:
    """
    Method 3: Just timestamp (simplest, some exchanges use this).
    """
    message = params.get('timestamp', '')
    logger.debug(f"V3 param string: {message}")
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

class RoostooClient:
    def __init__(self, signature_version: int = 1):
        self.base_url = BASE_URL
        self.rate_limit_delay = 0.5
        self.signature_version = signature_version
        logger.info(f"RoostooClient initialized (signature v{signature_version})")
        
    def _get_signed_headers(self, payload: Dict[str, str] = None) -> tuple:
        """Generate signed headers based on signature version."""
        if payload is None:
            payload = {}
        
        payload['timestamp'] = _get_timestamp()
        
        if self.signature_version == 1:
            signature = _generate_signature_v1(payload)
        elif self.signature_version == 2:
            signature = _generate_signature_v2(payload)
        elif self.signature_version == 3:
            signature = _generate_signature_v3(payload)
        else:
            signature = _generate_signature_v1(payload)
        
        headers = {
            'RST-API-KEY': API_KEY,
            'MSG-SIGNATURE': signature
        }
        
        logger.debug(f"Headers: RST-API-KEY={API_KEY[:10]}..., MSG-SIGNATURE={signature[:20]}...")
        
        return headers, payload
    
    # ============ Public Endpoints (No Auth) ============
    
    def get_server_time(self) -> Dict[str, Any]:
        """Check server time - no auth required."""
        url = f"{self.base_url}/v3/serverTime"
        time.sleep(self.rate_limit_delay)
        try:
            res = requests.get(url)
            res.raise_for_status()
            logger.info("API GET /v3/serverTime: Success")
            return res.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API GET /v3/serverTime: Failed - {str(e)}")
            raise
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """Get exchange info - no auth required."""
        url = f"{self.base_url}/v3/exchangeInfo"
        time.sleep(self.rate_limit_delay)
        try:
            res = requests.get(url)
            res.raise_for_status()
            logger.info("API GET /v3/exchangeInfo: Success")
            return res.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API GET /v3/exchangeInfo: Failed - {str(e)}")
            raise
    
    # ============ Authenticated Endpoints ============
    
    def get_balance(self, signature_version: Optional[int] = None) -> Dict[str, Any]:
        """Get wallet balance."""
        url = f"{self.base_url}/v3/balance"
        sig_ver = signature_version if signature_version else self.signature_version
        
        payload = {}
        payload['timestamp'] = _get_timestamp()
        
        if sig_ver == 1:
            signature = _generate_signature_v1(payload)
        elif sig_ver == 2:
            signature = _generate_signature_v2(payload)
        elif sig_ver == 3:
            signature = _generate_signature_v3(payload)
        else:
            signature = _generate_signature_v1(payload)
        
        headers = {
            'RST-API-KEY': API_KEY,
            'MSG-SIGNATURE': signature
        }
        
        logger.info(f"Trying signature v{sig_ver}")
        logger.debug(f"Payload: {payload}")
        logger.debug(f"Signature: {signature}")
        
        time.sleep(self.rate_limit_delay)
        try:
            res = requests.get(url, headers=headers, params=payload)
            res.raise_for_status()
            result = res.json()
            logger.info(f"Response: {result}")
            if not result.get('Success', True):
                raise Exception(f"Roostoo API Error: {result.get('ErrMsg', 'Unknown error')}")
            logger.info("API GET /v3/balance: Success")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"API GET /v3/balance: Failed - {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
    
    def get_ticker(self, pair: Optional[str] = None) -> Dict[str, Any]:
        """Get market ticker data."""
        url = f"{self.base_url}/v3/ticker"
        params = {'timestamp': _get_timestamp()}
        if pair:
            params['pair'] = pair
        
        time.sleep(self.rate_limit_delay)
        try:
            res = requests.get(url, params=params)
            res.raise_for_status()
            result = res.json()
            if not result.get('Success', True):
                raise Exception(f"Roostoo API Error: {result.get('ErrMsg', 'Unknown error')}")
            logger.info(f"API GET /v3/ticker: Success")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"API GET /v3/ticker: Failed - {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
