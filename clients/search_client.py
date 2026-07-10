import httpx
import xml.etree.ElementTree as ET
from core.logger import get_logger

logger = get_logger("SearchClient")

async def get_crypto_prices() -> str:
    """Fetch BTC and ETH prices from CoinGecko API"""
    logger.info("Fetching crypto prices from CoinGecko...")
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            btc_price = data.get("bitcoin", {}).get("usd", "N/A")
            btc_change = data.get("bitcoin", {}).get("usd_24h_change", 0.0)
            eth_price = data.get("ethereum", {}).get("usd", "N/A")
            eth_change = data.get("ethereum", {}).get("usd_24h_change", 0.0)
            
            return f"Bitcoin (BTC) Price: ${btc_price} (24h change: {btc_change:.2f}%)\nEthereum (ETH) Price: ${eth_price} (24h change: {eth_change:.2f}%)"
    except Exception as e:
        logger.error(f"Error fetching crypto prices: {e}")
        return "Bitcoin and Ethereum prices are currently unavailable due to an API error."

async def get_crypto_news() -> str:
    """Fetch latest crypto news from CoinDesk RSS feed"""
    logger.info("Fetching crypto news from CoinDesk RSS...")
    url = "https://www.coindesk.com/arc/outboundfeeds/rss/"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            root = ET.fromstring(response.text)
            items = root.findall(".//item")[:5] # Get top 5 news
            
            news_list = []
            for idx, item in enumerate(items):
                title = item.find("title").text if item.find("title") is not None else "No Title"
                description = item.find("description").text if item.find("description") is not None else "No Description"
                news_list.append(f"News {idx+1}: {title}\nSummary: {description}")
                
            return "\n".join(news_list)
    except Exception as e:
        logger.error(f"Error fetching crypto news: {e}")
        return "Latest cryptocurrency news is currently unavailable."

async def get_market_context() -> str:
    """Combine prices and news into a single context string"""
    prices = await get_crypto_prices()
    news = await get_crypto_news()
    
    context = (
        "--- LATEST MARKET DATA (DO NOT HALLUCINATE) ---\n"
        f"{prices}\n\n"
        "--- LATEST CRYPTO NEWS ---\n"
        f"{news}\n"
        "----------------------------------------------\n"
    )
    return context
