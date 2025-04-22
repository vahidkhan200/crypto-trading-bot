import os
from typing import Dict, Any

class Settings:
    # تنظیمات API
    ELBANK_API_KEY: str = os.getenv("ELBANK_API_KEY", "your_api_key_here")
    ELBANK_API_SECRET: str = os.getenv("ELBANK_API_SECRET", "your_api_secret_here")
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "your_bot_token_here")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "@your_channel")
    
    # تنظیمات ترید
    RISK_PER_TRADE: float = 0.01  # 1% از سرمایه
    RR_RATIO: int = 3  # نسبت ریسک به ریوارد
    MAX_LEVERAGE: int = 20  # حداکثر لورج مجاز
    
    # تنظیمات الگوها
    HARMONIC_PATTERNS: Dict[str, Any] = {
        'gartley': {'xa_retrace': 0.618, 'ab_retrace': 0.382},
        'bat': {'xa_retrace': 0.886, 'ab_retrace': 0.382},
        'butterfly': {'xa_retrace': 0.786, 'ab_retrace': 0.382},
        'crab': {'xa_retrace': 1.618, 'ab_retrace': 0.382}
    }
    
    # تنظیمات تایم‌فریم
    TIMEFRAMES: list = ['1h', '4h', '1d']
    
    # فعال/غیرفعال کردن ماژول‌ها
    MODULES: Dict[str, bool] = {
        'harmonic': True,
        'price_action': True,
        'smart_money': True,
        'news': True
    }

settings = Settings()
