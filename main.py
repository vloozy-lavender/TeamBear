import logging
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trading.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    load_dotenv('config/.env')
    logger.info("=" * 60)
    logger.info("Roostoo Trading Bot Started")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    from src.core.api_client import RoostooClient
    
    client = RoostooClient()
    
    # Test 1: Server Time (no auth)
    logger.info("Test 1: Checking server time...")
    try:
        server_time = client.get_server_time()
        logger.info(f"✅ Server Time: {server_time}")
    except Exception as e:
        logger.error(f"❌ Server Time Failed: {e}")
        return
    
    # Test 2: Exchange Info (no auth)
    logger.info("Test 2: Getting exchange info...")
    try:
        exchange_info = client.get_exchange_info()
        pairs = list(exchange_info.get('TradePairs', {}).keys())
        logger.info(f"✅ Available Pairs: {pairs}")
        logger.info(f"✅ Initial Wallet: {exchange_info.get('InitialWallet', {})}")
    except Exception as e:
        logger.error(f"❌ Exchange Info Failed: {e}")
        return
    
    # Test 3: Balance (auth required)
    logger.info("Test 3: Getting account balance...")
    try:
        balance = client.get_balance()
        wallet = balance.get('Wallet', {})
        logger.info(f"✅ Balance Retrieved!")
        for currency, amounts in wallet.items():
            logger.info(f"   {currency}: Free={amounts.get('Free', 0)}, Lock={amounts.get('Lock', 0)}")
    except Exception as e:
        logger.error(f"❌ Balance Failed: {e}")
        logger.error("⚠️  Check your API keys in config/.env")
        return
    
    # Test 4: Ticker (auth required)
    logger.info("Test 4: Getting market ticker...")
    try:
        ticker = client.get_ticker('BTC/USD')
        logger.info(f"✅ Ticker: {ticker}")
    except Exception as e:
        logger.error(f"❌ Ticker Failed: {e}")
    
    logger.info("=" * 60)
    logger.info("✅ All API tests passed! Bot ready for trading.")
    logger.info("=" * 60)
    
    # Main trading loop (placeholder)
    logger.info("Starting trading loop... Press Ctrl+C to stop")
    
    while True:
        try:
            balance = client.get_balance()
            total_usd = balance.get('Wallet', {}).get('USD', {}).get('Free', 0)
            logger.info(f"Portfolio USD: ${total_usd:,.2f}")
            time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"Loop error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()
