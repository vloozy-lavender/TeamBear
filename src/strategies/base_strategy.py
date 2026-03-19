from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseStrategy(ABC):
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
    
    @abstractmethod
    def generate_signals(self, client) -> List[Dict[str, Any]]:
        pass
