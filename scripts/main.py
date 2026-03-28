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
    logger.info("=" * 70)
    logger.info("🐻 TEAMBEAR - ROOSTOO TRADING BOT")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 70)
    
    from src.core.api_client import get_balance, get_ticker, get_exchange_info, place_order
    from src.strategies.ma_crossover_strategy import MACrossoverStrategy
    from src.core.risk_manager import RiskManager
    
    # Initialize components
    risk_manager = RiskManager(initial_capital=1_000_000)
    symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD']
    strategy = MACrossoverStrategy(symbols=symbols, short_window=5, long_window=20)
    
    # Get initial balance
    logger.info("Getting account balance...")
    balance = get_balance()
    usd_free = balance['SpotWallet']['USD']['Free']
    logger.info(f"💰 Available USD: ${usd_free:,.2f}")
    risk_manager.update_capital(usd_free)
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ BOT READY - Starting trading loop...")
    logger.info("=" * 70)
    logger.info(f"Strategy: MA Crossover ({strategy.short_window}/{strategy.long_window})")
    logger.info(f"Symbols: {symbols}")
    logger.info("Press Ctrl+C to stop")
    
    # Main trading loop
    loop_count = 0
    while True:
        try:
            loop_count += 1
            logger.info(f"\n{'='*50}")
            logger.info(f"[Loop {loop_count}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"{'='*50}")
            
            # Get updated balance
            balance = get_balance()
            usd_free = balance['SpotWallet']['USD']['Free']
            risk_manager.update_capital(usd_free)
            logger.info(f"💰 USD Balance: ${usd_free:,.2f}")
            
            # Check drawdown limits
            if not risk_manager.check_daily_drawdown():
                logger.warning("⚠️ Daily drawdown limit reached - pausing trading")
                time.sleep(300)
                continue
            
            # Generate trading signals
            logger.info("Generating trading signals...")
            signals = strategy.generate_signals(client=None)  # Will fix client passing
            
            # Execute signals
            for signal in signals:
                logger.info(f"Signal: {signal['action']} {signal['symbol']} @ ${signal['price']:,.2f}")
                # TODO: Add order execution logic here
            
            # Wait before next loop
            logger.info("Waiting 60 seconds...")
            time.sleep(60)
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Loop error: {e}")
            time.sleep(5)
    
    logger.info("=" * 70)
    logger.info("Bot shutdown complete")
    logger.info("=" * 70)

if __name__ == '__main__':
    main()
