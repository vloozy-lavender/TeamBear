import logging
from typing import List, Dict, Any
from .base_strategy import BaseStrategy

logger = logging.getLogger(__name__)

class MACrossoverStrategy(BaseStrategy):
    """
    Simple Moving Average Crossover Strategy
    
    Entry Signals:
    - BUY: Short MA crosses above Long MA (bullish)
    - SELL: Short MA crosses below Long MA (bearish)
    
    Parameters:
    - short_window: 5 periods
    - long_window: 20 periods
    """
    
    def __init__(self, symbols: List[str], short_window: int = 5, long_window: int = 20):
        super().__init__(symbols)
        self.short_window = short_window
        self.long_window = long_window
        self.price_history = {symbol: [] for symbol in symbols}
        self.positions = {}  # Track open positions
        
    def _calculate_sma(self, prices: List[float], window: int) -> float:
        """Calculate Simple Moving Average."""
        if len(prices) < window:
            return None
        return sum(prices[-window:]) / window
    
    def update_price(self, symbol: str, price: float):
        """Update price history for a symbol."""
        self.price_history[symbol].append(price)
        # Keep only enough data
        max_history = self.long_window + 5
        if len(self.price_history[symbol]) > max_history:
            self.price_history[symbol].pop(0)
    
    def generate_signals(self, client) -> List[Dict[str, Any]]:
        """Generate trading signals based on MA crossover."""
        signals = []
        
        for symbol in self.symbols:
            try:
                # Get current price
                ticker = client.get_ticker(symbol)
                price = ticker.get('Data', {}).get(symbol, {}).get('LastPrice', 0)
                
                if price <= 0:
                    continue
                
                # Update price history
                self.update_price(symbol, price)
                
                # Need enough data for signals
                if len(self.price_history[symbol]) < self.long_window:
                    logger.debug(f"{symbol}: Accumulating data ({len(self.price_history[symbol])}/{self.long_window})")
                    continue
                
                # Calculate current MAs
                short_ma = self._calculate_sma(self.price_history[symbol], self.short_window)
                long_ma = self._calculate_sma(self.price_history[symbol], self.long_window)
                
                # Calculate previous MAs (for crossover detection)
                prev_short = self._calculate_sma(self.price_history[symbol][:-1], self.short_window)
                prev_long = self._calculate_sma(self.price_history[symbol][:-1], self.long_window)
                
                if prev_short is None or prev_long is None:
                    continue
                
                logger.info(f"{symbol}: Price=${price:,.2f}, ShortMA=${short_ma:,.2f}, LongMA=${long_ma:,.2f}")
                
                # Bullish crossover (BUY signal)
                if prev_short <= prev_long and short_ma > long_ma:
                    if symbol not in self.positions:
                        signals.append({
                            'symbol': symbol,
                            'action': 'BUY',
                            'price': price,
                            'reason': 'MA Bullish Crossover',
                            'strength': (short_ma - long_ma) / long_ma
                        })
                        self.positions[symbol] = {'entry_price': price, 'side': 'BUY'}
                        logger.info(f"📈 BUY SIGNAL: {symbol} @ ${price:,.2f}")
                
                # Bearish crossover (SELL signal)
                elif prev_short >= prev_long and short_ma < long_ma:
                    if symbol in self.positions:
                        signals.append({
                            'symbol': symbol,
                            'action': 'SELL',
                            'price': price,
                            'reason': 'MA Bearish Crossover',
                            'strength': (long_ma - short_ma) / long_ma
                        })
                        del self.positions[symbol]
                        logger.info(f"📉 SELL SIGNAL: {symbol} @ ${price:,.2f}")
                        
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
        
        return signals
