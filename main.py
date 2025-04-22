import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from config import settings
from core.pattern_detector import PatternDetector
from core.risk_manager import RiskManager
from integrations.elbank_api import ElbankClient
from integrations.telegram_bot import TelegramNotifier
from strategies.harmonic import HarmonicPatterns
from strategies.price_action import PriceActionAnalyzer
from strategies.smart_money import SmartMoneyConcepts

# تنظیمات لاگ‌گیری
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self):
        # Initialize components
        self.exchange = ElbankClient(
            api_key=settings.ELBANK_API_KEY,
            api_secret=settings.ELBANK_API_SECRET
        )
        self.notifier = TelegramNotifier(
            bot_token=settings.TELEGRAM_TOKEN,
            chat_id=settings.TELEGRAM_CHAT_ID
        )
        self.risk_manager = RiskManager(
            risk_per_trade=settings.RISK_PER_TRADE,
            rr_ratio=settings.RR_RATIO
        )
        self.pattern_detector = PatternDetector()
        
        # آخرین سیگنال‌های ارسال شده
        self.last_signals: Dict[str, datetime] = {}

    async def get_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """دریافت داده‌های بازار برای یک نماد خاص"""
        try:
            ohlc = await self.exchange.get_ohlc(symbol, timeframe='1h')
            news = await self.exchange.get_news(symbol)
            return {
                'ohlc': ohlc,
                'news': news,
                'symbol': symbol,
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error getting data for {symbol}: {str(e)}")
            return None

    async def analyze_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """آنالیز کامل یک نماد"""
        market_data = await self.get_market_data(symbol)
        if not market_data:
            return None

        analysis = {
            'symbol': symbol,
            'timestamp': market_data['timestamp'],
            'harmonic': {},
            'price_action': {},
            'smart_money': {},
            'indicators': {},
            'news_sentiment': None
        }

        # تحلیل هارمونیک
        if settings.MODULES['harmonic']:
            analysis['harmonic'] = HarmonicPatterns.detect_all(market_data['ohlc'])

        # تحلیل پرایس اکشن
        if settings.MODULES['price_action']:
            analysis['price_action'] = PriceActionAnalyzer.analyze_candles(market_data['ohlc'])

        # تحلیل اسمارت مانی
        if settings.MODULES['smart_money']:
            analysis['smart_money'] = SmartMoneyConcepts.analyze(market_data['ohlc'])

        # محاسبه اندیکاتورها
        analysis['indicators'] = self.pattern_detector.calculate_indicators(market_data['ohlc'])

        # تحلیل اخبار
        if settings.MODULES['news']:
            analysis['news_sentiment'] = self.pattern_detector.analyze_news_sentiment(market_data['news'])

        return analysis

    def should_send_signal(self, symbol: str) -> bool:
        """بررسی آیا باید برای این نماد سیگنال ارسال کرد یا نه"""
        last_signal_time = self.last_signals.get(symbol)
        if not last_signal_time:
            return True
            
        # حداقل 4 ساعت از آخرین سیگنال گذشته باشد
        return datetime.utcnow() - last_signal_time > timedelta(hours=4)

    async def generate_signal(self, analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """تولید سیگنال معاملاتی بر اساس تحلیل"""
        if not self.should_send_signal(analysis['symbol']):
            return None

        # محاسبه نقاط ورود و خروج
        risk_data = self.risk_manager.calculate_position(
            atr=analysis['indicators']['atr'],
            current_price=analysis['ohlc']['close'][-1],
            key_levels=analysis['price_action'].get('key_levels', {})
        )

        # تعیین جهت معامله
        is_bullish = self._determine_trend_direction(analysis)
        
        signal = {
            'symbol': analysis['symbol'],
            'position_type': 'BUY' if is_bullish else 'SELL',
            'entry': risk_data['entry'],
            'target1': risk_data['target1'],
            'target2': risk_data['target2'],
            'stop_loss': risk_data['stop_loss'],
            'leverage': risk_data['leverage'],
            'pattern': self._get_strongest_pattern(analysis),
            'rr_ratio': settings.RR_RATIO,
            'strength': self._calculate_signal_strength(analysis),
            'timestamp': datetime.utcnow().isoformat(),
            'analysis_summary': self._generate_analysis_summary(analysis)
        }

        return signal

    async def run(self):
        """حلقه اصلی اجرای ربات"""
        logger.info("Starting Advanced Trading Bot...")
        
        while True:
            try:
                symbols = await self.exchange.get_all_symbols()
                logger.info(f"Analyzing {len(symbols)} symbols...")
                
                for symbol in symbols:
                    try:
                        analysis = await self.analyze_symbol(symbol)
                        if not analysis:
                            continue
                            
                        signal = await self.generate_signal(analysis)
                        if signal:
                            await self.notifier.send_signal(signal)
                            self.last_signals[signal['symbol']] = datetime.utcnow()
                            logger.info(f"Signal sent for {signal['symbol']}")
                            
                    except Exception as e:
                        logger.error(f"Error processing {symbol}: {str(e)}")
                        continue
                        
                await asyncio.sleep(60)  # استراحت 1 دقیقه‌ای بین هر چرخه
                
            except Exception as e:
                logger.error(f"Main loop error: {str(e)}")
                await asyncio.sleep(300)  # در صورت خطا 5 دقیقه صبر کنید

    # --- متدهای کمکی ---
    def _determine_trend_direction(self, analysis: Dict[str, Any]) -> bool:
        """تعیین جهت کلی بازار بر اساس تحلیل‌ها"""
        # 1. بررسی اندیکاتورها
        indicators_bullish = (
            analysis['indicators']['rsi'] > 50 and
            analysis['indicators']['macd'] > 0 and
            analysis['indicators']['ema50'] > analysis['indicators']['ema200']
        )
        
        # 2. بررسی پرایس اکشن
        price_action_bullish = (
            analysis['price_action'].get('pinbar', False) or
            analysis['price_action'].get('engulfing', False)
        )
        
        # 3. بررسی هارمونیک
        harmonic_bullish = any(
            p['detected'] and p['pattern_type'] == 'bullish'
            for p in analysis['harmonic'].values()
        )
        
        # 4. بررسی اسمارت مانی
        smart_money_bullish = (
            analysis['smart_money'].get('order_blocks', {}).get('bullish_ob', False)
        )
        
        return (indicators_bullish + price_action_bullish + 
                harmonic_bullish + smart_money_bullish) >= 2

    def _get_strongest_pattern(self, analysis: Dict[str, Any]) -> str:
        """شناسایی قوی‌ترین الگوی تشخیص داده شده"""
        patterns = []
        
        # الگوهای هارمونیک
        for name, pattern in analysis['harmonic'].items():
            if pattern['detected']:
                patterns.append((f"Harmonic {name}", pattern['confidence']))
        
        # الگوهای پرایس اکشن
        if analysis['price_action'].get('pinbar'):
            patterns.append(("Pin Bar", 0.8))
        if analysis['price_action'].get('engulfing'):
            patterns.append(("Engulfing", 0.7))
            
        # اوردر بلاک‌ها
        if analysis['smart_money'].get('order_blocks', {}).get('bullish_ob'):
            patterns.append(("Bullish OB", 0.9))
        elif analysis['smart_money'].get('order_blocks', {}).get('bearish_ob'):
            patterns.append(("Bearish OB", 0.9))
            
        if not patterns:
            return "Multiple Indicators"
            
        return max(patterns, key=lambda x: x[1])[0]

    def _calculate_signal_strength(self, analysis: Dict[str, Any]) -> int:
        """محاسبه قدرت سیگنال از 1 تا 5"""
        strength = 0
        
        # امتیاز اندیکاتورها
        if analysis['indicators']['rsi'] > 60 or analysis['indicators']['rsi'] < 40:
            strength += 1
        if analysis['indicators']['macd'] > 0:
            strength += 1
        if analysis['indicators']['adx'] > 25:
            strength += 1
            
        # امتیاز الگوها
        if analysis['harmonic']:
            strength += 2
        if analysis['price_action'].get('pinbar') or analysis['price_action'].get('engulfing'):
            strength += 1
        if analysis['smart_money'].get('order_blocks'):
            strength += 1
            
        return min(5, max(1, strength))

    def _generate_analysis_summary(self, analysis: Dict[str, Any]) -> str:
        """تولید خلاصه تحلیل برای گزارش"""
        summary = []
        
        if analysis['harmonic']:
            summary.append(f"📊 Harmonic Patterns: {', '.join(analysis['harmonic'].keys())}")
        
        if analysis['price_action']:
            pa = analysis['price_action']
            pa_items = []
            if pa.get('pinbar'): pa_items.append("Pin Bar")
            if pa.get('engulfing'): pa_items.append("Engulfing")
            if pa_items:
                summary.append(f"🕯️ Price Action: {', '.join(pa_items)}")
        
        if analysis['smart_money'].get('order_blocks'):
            sm = analysis['smart_money']
            if sm['order_blocks'].get('bullish_ob'):
                summary.append("💰 Smart Money: Bullish OB")
            elif sm['order_blocks'].get('bearish_ob'):
                summary.append("💰 Smart Money: Bearish OB")
        
        if analysis['news_sentiment']:
            sentiment = analysis['news_sentiment']['sentiment']
            summary.append(f"📰 News Sentiment: {sentiment.capitalize()}")
        
        return "\n".join(summary) if summary else "No strong patterns detected"

async def main():
    bot = TradingBot()
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
