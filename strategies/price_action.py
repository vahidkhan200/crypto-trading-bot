import numpy as np
from typing import Dict, List, Any

class PriceActionAnalyzer:
    @staticmethod
    def identify_key_levels(ohlc: Dict[str, Any], lookback: int = 20) -> Dict[str, float]:
        highs = np.array(ohlc['high'][-lookback:])
        lows = np.array(ohlc['low'][-lookback:])
        
        resistance = highs.max()
        support = lows.min()
        pivot = (resistance + support) / 2
        
        return {
            'resistance': float(resistance),
            'support': float(support),
            'pivot': float(pivot)
        }
    
    @staticmethod
    def detect_pinbar(ohlc: Dict[str, Any]) -> bool:
        body = abs(ohlc['open'][-1] - ohlc['close'][-1])
        upper_wick = ohlc['high'][-1] - max(ohlc['open'][-1], ohlc['close'][-1])
        lower_wick = min(ohlc['open'][-1], ohlc['close'][-1]) - ohlc['low'][-1]
        
        is_pinbar = (
            (lower_wick > 2 * body and upper_wick < body) or  # Bullish pinbar
            (upper_wick > 2 * body and lower_wick < body)     # Bearish pinbar
        )
        return is_pinbar
    
    @staticmethod
    def analyze_candles(ohlc: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'key_levels': PriceActionAnalyzer.identify_key_levels(ohlc),
            'pinbar': PriceActionAnalyzer.detect_pinbar(ohlc),
            'inside_bar': PriceActionAnalyzer.detect_inside_bar(ohlc),
            'engulfing': PriceActionAnalyzer.detect_engulfing(ohlc)
        }
