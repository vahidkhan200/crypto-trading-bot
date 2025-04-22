import numpy as np
from typing import Dict, Any

class SmartMoneyConcepts:
    @staticmethod
    def detect_liquidity_zones(ohlc: Dict[str, Any]) -> Dict[str, Any]:
        highs = np.array(ohlc['high'])
        lows = np.array(ohlc['low'])
        volumes = np.array(ohlc['volume'])
        
        # یافتن نقدینگی بالا
        high_vol_idx = volumes.argsort()[-3:][::-1]
        liquidity_zones = {
            'highs': [float(highs[i]) for i in high_vol_idx],
            'lows': [float(lows[i]) for i in high_vol_idx]
        }
        
        return liquidity_zones
    
    @staticmethod
    def detect_ob(ohlc: Dict[str, Any]) -> bool:
        # تشخیص اوردر بلاک
        close = np.array(ohlc['close'])
        volume = np.array(ohlc['volume'])
        
        is_bullish_ob = (
            (close[-1] > close[-2]) and 
            (volume[-1] > volume[-2] * 1.5)
        )
        
        is_bearish_ob = (
            (close[-1] < close[-2]) and 
            (volume[-1] > volume[-2] * 1.5)
        )
        
        return {
            'bullish_ob': is_bullish_ob,
            'bearish_ob': is_bearish_ob
        }
    
    @staticmethod
    def analyze(ohlc: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'liquidity_zones': SmartMoneyConcepts.detect_liquidity_zones(ohlc),
            'order_blocks': SmartMoneyConcepts.detect_ob(ohlc),
            'fair_value_gap': SmartMoneyConcepts.detect_fvg(ohlc)
        }
