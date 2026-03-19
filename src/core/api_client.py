import requests
import time
import hmac
import hashlib
import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv('config/.env')
logger = logging.getLogger(__name__)

# --- API Configuration ---
BASE_URL = os.getenv('ROOSTOO_BASE_URL', 'https://mock-api.roostoo.com')
API_KEY = os.getenv('ROOSTOO_API_KEY')
SECRET_KEY = os.getenv('ROOSTOO_API_SECRET')

logger.info(f"API Key loaded: {API_KEY[:10]}...{API_KEY[-10:] if len(API_KEY) > 20 else '***'}")
logger.info(f"Secret Key loaded: {SECRET_KEY[:10]}...{SECRET_KEY[-10:] if len(SECRET_KEY) > 20 else '***'}")

# ------------------------------
# Utility Functions
# ------------------------------

def _get_timestamp() -> str:
    """Return a 13-digit millisecond timestamp as string."""
    return str(int(time.time() * 1000))

def _get_signed_headers(payload: dict = None):
    """
    Generate signed headers and totalParams for RCL_TopLevelCheck endpoints.
    Signature = HMAC SHA256(secretKey, sorted_params_string)
    """
    if payload is None:
        payload = {}
    
    payload['timestamp'] = _get_timestamp()
    sorted_keys = sorted(payload.keys())
    total_params = "&".join(f"{k}={payload[k]}" for k in sorted_keys)
    
    logger.debug(f"Signing params: {total_params}")
    
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        total_params.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    logger.debug(f"Signature: {signature}")
    
    headers = {
        'RST-API-KEY': API_KEY,
        'MSG-SIGNATURE': signature
    }
    
    return headers, payload, total_params

# ------------------------------
# Public Endpoints (No Auth)
# ------------------------------

def check_server_time() -> Dict[str, Any]:
    """Check API server time - RCL_NoVerification."""
    url = f"{BASE_URL}/v3/serverTime"
    try:
        res = requests.get(url)
        res.raise_for_status()
        logger.info("API GET /v3/serverTime: Success")
        return res.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API GET /v3/serverTime: Failed - {str(e)}")
        raise

def get_exchange_info() -> Dict[str, Any]:
    """Get exchange trading pairs and info - RCL_NoVerification."""
    url = f"{BASE_URL}/v3/exchangeInfo"
    try:
        res = requests.get(url)
        res.raise_for_status()
        logger.info("API GET /v3/exchangeInfo: Success")
        return res.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API GET /v3/exchangeInfo: Failed - {str(e)}")
        raise

def get_ticker(pair: Optional[str] = None) -> Dict[str, Any]:
    """Get ticker for one or all pairs - RCL_TSCheck (timestamp only)."""
    url = f"{BASE_URL}/v3/ticker"
    params = {'timestamp': _get_timestamp()}
    if pair:
        params['pair'] = pair
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

# ------------------------------
# Signed Endpoints (RCL_TopLevelCheck)
# ------------------------------

def get_balance() -> Dict[str, Any]:
    """Get wallet balances - RCL_TopLevelCheck."""
    url = f"{BASE_URL}/v3/balance"
    headers, payload, _ = _get_signed_headers({})
    try:
        res = requests.get(url, headers=headers, params=payload)
        res.raise_for_status()
        result = res.json()
        logger.debug(f"Balance response: {result}")
        if not result.get('Success', True):
            raise Exception(f"Roostoo API Error: {result.get('ErrMsg', 'Unknown error')}")
        logger.info("API GET /v3/balance: Success")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"API GET /v3/balance: Failed - {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response Status: {e.response.status_code}")
            logger.error(f"Response Body: {e.response.text}")
        raise

def get_pending_count() -> Dict[str, Any]:
    """Get total pending order count - RCL_TopLevelCheck."""
    url = f"{BASE_URL}/v3/pending_count"
    headers, payload, _ = _get_signed_headers({})
    try:
        res = requests.get(url, headers=headers, params=payload)
        res.raise_for_status()
        result = res.json()
        if not result.get('Success', True):
            raise Exception(f"Roostoo API Error: {result.get('ErrMsg', 'Unknown error')}")
        logger.info("API GET /v3/pending_count: Success")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"API GET /v3/pending_count: Failed - {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        raise

def place_order(pair: str, side: str, quantity: float, 
                price: Optional[float] = None, order_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Place a LIMIT or MARKET order - RCL_TopLevelCheck.
    """
    url = f"{BASE_URL}/v3/place_order"
    
    # Ensure pair format is XXX/USD
    if '/' not in pair:
        pair = f"{pair}/USD"
    
    # Determine order type
    if order_type is None:
        order_type = 'LIMIT' if price is not None else 'MARKET'
    
    if order_type.upper() == 'LIMIT' and price is None:
        raise ValueError("LIMIT orders require a price")
    
    payload = {
        'pair': pair,
        'side': side.upper(),
        'type': order_type.upper(),
        'quantity': str(quantity)
    }
    if order_type.upper() == 'LIMIT':
        payload['price'] = str(price)
    
    headers, _, total_params = _get_signed_headers(payload)
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    
    logger.info(f"Placing {order_type} {side} order: {quantity} {pair} @ {price if price else 'MARKET'}")
    logger.debug(f"POST params: {total_params}")
    
    try:
        # POST with form-urlencoded data (NOT JSON!)
        res = requests.post(url, headers=headers, data=total_params)
        res.raise_for_status()
        result = res.json()
        logger.debug(f"Order response: {result}")
        if not result.get('Success', True):
            raise Exception(f"Roostoo API Error: {result.get('ErrMsg', 'Unknown error')}")
        logger.info(f"API POST /v3/place_order: Success - OrderID: {result.get('OrderDetail', {}).get('OrderID')}")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"API POST /v3/place_order: Failed - {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response Status: {e.response.status_code}")
            logger.error(f"Response Body: {e.response.text}")
        raise

def query_order(order_id: Optional[str] = None, pair: Optional[str] = None, 
                pending_only: bool = False) -> Dict[str, Any]:
    """Query order history - RCL_TopLevelCheck."""
    url = f"{BASE_URL}/v3/query_order"
    payload = {}
    if order_id:
        payload['order_id'] = str(order_id)
    elif pair:
        payload['pair'] = pair
        payload['pending_only'] = 'TRUE' if pending_only else 'FALSE'
    
    headers, _, total_params = _get_signed_headers(payload)
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    
    try:
        res = requests.post(url, headers=headers, data=total_params)
        res.raise_for_status()
        result = res.json()
        if not result.get('Success', True):
            raise Exception(f"Roostoo API Error: {result.get('ErrMsg', 'Unknown error')}")
        logger.info("API POST /v3/query_order: Success")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"API POST /v3/query_order: Failed - {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        raise

def cancel_order(order_id: Optional[str] = None, pair: Optional[str] = None) -> Dict[str, Any]:
    """Cancel specific or all pending orders - RCL_TopLevelCheck."""
    url = f"{BASE_URL}/v3/cancel_order"
    payload = {}
    if order_id:
        payload['order_id'] = str(order_id)
    elif pair:
        payload['pair'] = pair
    
    headers, _, total_params = _get_signed_headers(payload)
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    
    try:
        res = requests.post(url, headers=headers, data=total_params)
        res.raise_for_status()
        result = res.json()
        if not result.get('Success', True):
            raise Exception(f"Roostoo API Error: {result.get('ErrMsg', 'Unknown error')}")
        logger.info("API POST /v3/cancel_order: Success")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"API POST /v3/cancel_order: Failed - {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        raise
