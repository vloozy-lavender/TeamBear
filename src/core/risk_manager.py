import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self, initial_capital: float = 1_000_000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_position_size = 0.25
        self.max_daily_drawdown = 0.05
        self.stop_loss_pct = 0.03
        self.risk_per_trade = 0.02
        self.max_open_positions = 5
        self.daily_high = initial_capital
        self.trade_count = 0
        
    def update_capital(self, new_capital: float):
        self.current_capital = new_capital
        self.daily_high = max(self.daily_high, new_capital)
        
    def check_daily_drawdown(self) -> bool:
        current_drawdown = (self.daily_high - self.current_capital) / self.daily_high
        if current_drawdown >= self.max_daily_drawdown:
            logger.warning(f"Daily drawdown limit reached: {current_drawdown:.2%}")
            return False
        return True
    
    def calculate_position_size(self, price: float, available_balance: float) -> float:
        max_by_capital = available_balance * self.max_position_size / price
        max_by_risk = (self.current_capital * self.risk_per_trade) / (price * self.stop_loss_pct)
        return min(max_by_capital, max_by_risk)
    
    def can_open_position(self, current_positions: int) -> bool:
        if current_positions >= self.max_open_positions:
            logger.warning("Max open positions reached")
            return False
        return self.check_daily_drawdown()
    
    def get_stop_loss_price(self, entry_price: float, side: str) -> float:
        if side == 'BUY':
            return entry_price * (1 - self.stop_loss_pct)
        else:
            return entry_price * (1 + self.stop_loss_pct)
    
    def reset_daily_metrics(self):
        self.daily_high = self.current_capital
        self.trade_count = 0
        logger.info("Daily metrics reset")
