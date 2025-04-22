import requests
from typing import Dict, Any

class TelegramNotifier:
    def __init__(self, bot_token: str):
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
    async def send_signal(self, signal: Dict[str, Any]):
        message = self._format_signal(signal)
        url = f"{self.base_url}/sendMessage"
        params = {
            'chat_id': signal.get('chat_id', '@trading_signals'),
            'text': message,
            'parse_mode': 'Markdown'
        }
        requests.post(url, params=params)
        
    def _format_signal(self, signal: Dict[str, Any]) -> str:
        return (
            f"🚀 *{signal['symbol']} {signal['position_type']} Signal*\n\n"
            f"• Entry: `{signal['entry']}`\n"
            f"• Targets: `{signal['target1']} | {signal['target2']}`\n"
            f"• Stop Loss: `{signal['stop_loss']}`\n"
            f"• Leverage: {signal['leverage']}x\n"
            f"• Pattern: {signal['pattern']}\n"
            f"• Strength: {signal['strength']}/5\n"
            f"• R/R: 1:{self.rr_ratio}"
        )
