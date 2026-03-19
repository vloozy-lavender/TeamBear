import logging

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self, initial_capital: float = 1000000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_position_size = 0.25
        self.max_daily_drawdown = 0.05
        self.stop_loss_pct = 0.03
        self.risk_per_trade = 0.02
        self.max_open_positions = 5
        self.daily_high = initial_capital
    
    def update_capital(self, new_capital: float):
        self.current_capital = new_capital
        self.daily_high = max(self.daily_high, new_capital)
    
    def check_daily_drawdown(self) -> bool:
        drawdown = (self.daily_high - self.current_capital) / self.daily_high
        if drawdown >= self.max_daily_drawdown:
            logger.warning(f"Drawdown limit reached: {drawdown:.2%}")
            return False
        return True
    
    def can_open_position(self, count: int) -> bool:
        if count >= self.max_open_positions:
            return False
        return self.check_daily_drawdown()
