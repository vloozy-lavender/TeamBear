import logging
import sys
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# Enable DEBUG logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/debug_full.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    load_dotenv('config/.env')
    
    logger.info("=" * 70)
    logger.info("ROOSTOO API DEBUG - FULL LOG FOR SUPPORT")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"API Key: {os.getenv('ROOSTOO_API_KEY', 'NOT SET')[:10]}...")
    logger.info(f"Base URL: {os.getenv('ROOSTOO_BASE_URL', 'NOT SET')}")
    logger.info("=" * 70)
    
    from src.core.api_client import (
        check_server_time,
        get_exchange_info,
        get_ticker,
        get_balance,
        get_pending_count
    )
    
    # Test 1: Server Time (no auth)
    logger.info("\n" + "=" * 70)
    logger.info("TEST 1: GET /v3/serverTime (NO AUTH)")
    logger.info("=" * 70)
    try:
        result = check_server_time()
        logger.info(f"✅ SUCCESS: {result}")
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
    
    # Test 2: Exchange Info (no auth)
    logger.info("\n" + "=" * 70)
    logger.info("TEST 2: GET /v3/exchangeInfo (NO AUTH)")
    logger.info("=" * 70)
    try:
        result = get_exchange_info()
        logger.info(f"✅ SUCCESS: {len(result.get('TradePairs', {}))} pairs found")
        logger.info(f"Initial Wallet: {result.get('InitialWallet', {})}")
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
    
    # Test 3: Balance (auth required)
    logger.info("\n" + "=" * 70)
    logger.info("TEST 3: GET /v3/balance (AUTH REQUIRED)")
    logger.info("=" * 70)
    try:
        result = get_balance()
        logger.info(f"✅ SUCCESS: {result}")
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response Status: {e.response.status_code}")
            logger.error(f"Response Body: {e.response.text}")
    
    # Test 4: Ticker (auth required)
    logger.info("\n" + "=" * 70)
    logger.info("TEST 4: GET /v3/ticker?pair=BTC/USD (AUTH REQUIRED)")
    logger.info("=" * 70)
    try:
        result = get_ticker('BTC/USD')
        logger.info(f"✅ SUCCESS: {result}")
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response Status: {e.response.status_code}")
            logger.error(f"Response Body: {e.response.text}")
    
    # Test 5: Pending Count (auth required)
    logger.info("\n" + "=" * 70)
    logger.info("TEST 5: GET /v3/pending_count (AUTH REQUIRED)")
    logger.info("=" * 70)
    try:
        result = get_pending_count()
        logger.info(f"✅ SUCCESS: {result}")
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response Status: {e.response.status_code}")
            logger.error(f"Response Body: {e.response.text}")
    
    logger.info("\n" + "=" * 70)
    logger.info("DEBUG COMPLETE")
    logger.info("=" * 70)
    logger.info("\nPlease send logs/debug_full.log to Roostoo support")

if __name__ == '__main__':
    main()
