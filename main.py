import asyncio
from core.trading_engine import TradingEngine
from integrations.elbank_api import ElbankClient
from integrations.telegram_bot import TelegramNotifier
from config import settings

async def main():
    # Initialize components
    elbank = ElbankClient(api_key=settings.ELBANK_API_KEY, 
                         api_secret=settings.ELBANK_SECRET)
    notifier = TelegramNotifier(bot_token=settings.TELEGRAM_TOKEN)
    
    # Create trading engine
    engine = TradingEngine(
        exchange=elbank,
        notifier=notifier,
        risk_params={
            'rr_ratio': 3,
            'max_risk': 0.01
        }
    )
    
    # Start trading loop
    await engine.run()

if __name__ == "__main__":
    asyncio.run(main())
