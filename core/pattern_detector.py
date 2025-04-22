import talib
import numpy as np
from typing import Dict, Any

class PatternDetector:
    def detect_candle_patterns(self, ohlc: Dict[str, Any]) -> Dict[str, bool]:
        # Implement all 61 candlestick patterns
        patterns = {}
        for func in [f for f in dir(talib) if f.startswith('CDL')]:
            result = getattr(talib, func)(
                ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'])
            patterns[func] = bool(result[-1])
        return patterns
    
    def detect_harmonic_patterns(self, ohlc: Dict[str, Any]) -> Dict[str, bool]:
        # Implement harmonic patterns (Gartley, Bat, Butterfly, etc.)
        patterns = {
            'gartley': self._detect_gartley(ohlc),
            'bat': self._detect_bat(ohlc),
            'butterfly': self._detect_butterfly(ohlc),
            'crab': self._detect_crab(ohlc),
            'shark': self._detect_shark(ohlc)
        }
        return patterns
    
    def calculate_indicators(self, ohlc: Dict[str, Any]) -> Dict[str, Any]:
        # Calculate technical indicators
        closes = np.array(ohlc['close'])
        return {
            'rsi': talib.RSI(closes)[-1],
            'macd': talib.MACD(closes)[-1],
            'atr': talib.ATR(
                ohlc['high'], ohlc['low'], ohlc['close'])[-1],
            'ema50': talib.EMA(closes, 50)[-1],
            'ema200': talib.EMA(closes, 200)[-1],
            'adx': talib.ADX(
                ohlc['high'], ohlc['low'], ohlc['close'])[-1]
        }
