import aiohttp
from typing import Dict, Any, List

class ElbankClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.elbank.com/v1"
        
    async def get_ohlc(self, symbol: str, timeframe: str = '1h'):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/market/ohlc?symbol={symbol}&timeframe={timeframe}"
            async with session.get(url) as response:
                return await response.json()
                
    async def get_all_symbols(self) -> List[str]:
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/market/symbols"
            async with session.get(url) as response:
                data = await response.json()
                return data['symbols']
