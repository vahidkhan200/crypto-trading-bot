import asyncio
from datetime import datetime
from typing import Dict, Any
from core.pattern_detector import PatternDetector
from core.risk_manager import RiskManager

class TradingEngine:
    def __init__(self, exchange, notifier, risk_params):
        self.exchange = exchange
        self.notifier = notifier
        self.risk_manager = RiskManager(risk_params)
        self.pattern_detector = PatternDetector()
        
    async def analyze_market(self, symbol: str):
        # Get market data
        ohlc = await self.exchange.get_ohlc(symbol)
        news = await self.exchange.get_news(symbol)
        
        # Detect patterns
        analysis = {
            'candle': self.pattern_detector.detect_candle_patterns(ohlc),
            'harmonic': self.pattern_detector.detect_harmonic_patterns(ohlc),
            'chart': self.pattern_detector.detect_chart_patterns(ohlc),
            'indicators': self.pattern_detector.calculate_indicators(ohlc),
            'price_action': self.pattern_detector.analyze_price_action(ohlc),
            'smart_money': self.pattern_detector.detect_smart_money(ohlc),
            'news_sentiment': self.pattern_detector.analyze_news(news)
        }
        
        return analysis
    
    async def generate_signal(self, symbol: str, analysis: Dict[str, Any]):
        # Risk calculation
        risk_data = self.risk_manager.calculate_position(
            analysis['indicators']['atr'],
            analysis['price_action']['key_levels']
        )
        
        # Prepare signal
        signal = {
            'symbol': symbol,
            'position_type': 'BUY' if analysis['bullish'] else 'SELL',
            'entry': risk_data['entry'],
            'target1': risk_data['target1'],
            'target2': risk_data['target2'],
            'stop_loss': risk_data['stop_loss'],
            'leverage': risk_data['leverage'],
            'pattern': self._get_strongest_pattern(analysis),
            'rr_ratio': 3,
            'strength': self._calculate_signal_strength(analysis),
            'timestamp': datetime.utcnow()
        }
        
        return signal
    
    async def run(self):
        while True:
            symbols = await self.exchange.get_all_symbols()
            for symbol in symbols:
                analysis = await self.analyze_market(symbol)
                if self._is_strong_signal(analysis):
                    signal = await self.generate_signal(symbol, analysis)
                    await self.notifier.send_signal(signal)
            await asyncio.sleep(60)  # Run every minute
