import numpy as np
from typing import Dict, Any
from config import settings

class HarmonicPatterns:
    @staticmethod
    def detect_gartley(ohlc: Dict[str, Any]) -> Dict[str, Any]:
        high, low = np.array(ohlc['high']), np.array(ohlc['low'])
        
        # یافتن نقاط XABCD
        x = high.argmax() if len(high) > 0 else -1
        a = low.argmin() if len(low) > 0 else -1
        
        if x == -1 or a == -1:
            return {'detected': False}
        
        # محاسبه فیبوناچی
        xa = high[x] - low[a]
        ab = high[x] - (xa * settings.HARMONIC_PATTERNS['gartley']['ab_retrace'])
        
        # شرایط الگو
        is_valid = (
            (ab > low[a]) and 
            (abs(ab - (high[x] - xa * 0.618)) / high[x] < 0.02
        )
        
        return {
            'detected': is_valid,
            'pattern': 'gartley',
            'points': {'X': x, 'A': a},
            'entry': ab,
            'target': high[x],
            'stop_loss': low[a] * 0.99
        }

    @staticmethod
    def detect_bat(ohlc: Dict[str, Any]) -> Dict[str, Any]:
        # پیاده‌سازی مشابه برای الگوی Bat
        pass
    
    @staticmethod
    def detect_all(ohlc: Dict[str, Any]) -> Dict[str, Any]:
        patterns = {
            'gartley': HarmonicPatterns.detect_gartley(ohlc),
            'bat': HarmonicPatterns.detect_bat(ohlc),
            # اضافه کردن سایر الگوها
        }
        return {k: v for k, v in patterns.items() if v['detected']}
