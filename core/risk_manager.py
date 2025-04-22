from typing import Dict, Any

class RiskManager:
    def __init__(self, params: Dict[str, Any]):
        self.rr_ratio = params.get('rr_ratio', 3)
        self.max_risk = params.get('max_risk', 0.01)
        
    def calculate_position(self, atr: float, key_levels: Dict[str, float]):
        # Calculate position size based on volatility
        position_size = (self.max_risk * 100) / (atr * self.rr_ratio)
        
        return {
            'entry': key_levels['entry'],
            'target1': key_levels['entry'] + (atr * 1),
            'target2': key_levels['entry'] + (atr * self.rr_ratio),
            'stop_loss': key_levels['entry'] - atr,
            'leverage': min(20, max(1, int(10 / atr))),
            'size': position_size
        }
