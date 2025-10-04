"""Instagram caption generation using standard AI models - fallbacks allowed."""

import os
import json
import pandas as pd
from .openrouter_client import create_openrouter_client

def safe_get(dataframe, column, row=0, default='N/A'):
    """Safely extract data from DataFrame"""
    try:
        if dataframe is None or dataframe.empty:
            return default

        if isinstance(dataframe, pd.DataFrame):
            if column in dataframe.columns and len(dataframe) > row:
                value = dataframe.iloc[row][column]
                return str(value) if pd.notna(value) else default

        return default
    except (IndexError, KeyError, AttributeError, ValueError):
        return default

def truncate_caption(text, max_length=2200):
    """Truncate caption to fit character limit"""
    if len(text) <= max_length:
        return text

    # Find last complete line within limit
    truncated = text[:max_length]
    last_newline = truncated.rfind('\n')
    if last_newline > max_length * 0.8:
        return truncated[:last_newline]

    # Find last sentence
    for punct in ['. ', '! ', '? ']:
        last_punct = truncated.rfind(punct)
        if last_punct > max_length * 0.8:
            return truncated[:last_punct + len(punct)]

    return truncated[:truncated.rfind(' ')] + '...'

def generate_base_caption(market_data=None, btc_data=None, gainer_data=None, loser_data=None,
                         top_shorts=None, top_longs=None):
    """Generate base caption with error handling"""
    try:
        # Build caption sections
        sections = ["🚨 Crypto Alert! Market Never Sleeps 🚨\n"]

        # Market overview
        if market_data and not market_data.empty:
            market_row = market_data.iloc[0] if len(market_data) > 0 else {}
            sections.extend([
                f"📅 {safe_get(market_data, 'Todays_Date')}",
                f"💰 Volume: {safe_get(market_data, 'total_volume24h_reported')} ({safe_get(market_data, 'total_volume24h_yesterday_percentage_change')}%)",
                f"₿ BTC Dom: {safe_get(market_data, 'btc_dominance')}% | Ⓔ ETH Dom: {safe_get(market_data, 'eth_dominance')}%\n"
            ])

        # Bitcoin data
        if btc_data and not btc_data.empty:
            btc_row = btc_data.iloc[0] if len(btc_data) > 0 else {}
            price = safe_get(btc_data, 'price')
            change_24h = safe_get(btc_data, 'percent_change24h')
            volume = safe_get(btc_data, 'volume24h')
            market_cap = safe_get(btc_data, 'market_cap')

            if price != 'N/A':
                sections.extend([
                    f"₿ BITCOIN UPDATE 🟢",
                    f"Price: {price} ({change_24h}%)",
                    f"Volume: {volume}",
                    f"Market Cap: {market_cap}\n"
                ])

        # Top movers
        if gainer_data and loser_data:
            gainer_symbol = safe_get(gainer_data, 'symbol') if not gainer_data.empty else 'N/A'
            gainer_pct = safe_get(gainer_data, 'percent_change24h') if not gainer_data.empty else '0'
            loser_symbol = safe_get(loser_data, 'symbol') if not loser_data.empty else 'N/A'
            loser_pct = safe_get(loser_data, 'percent_change24h') if not loser_data.empty else '0'

            if gainer_symbol != 'N/A':
                sections.extend([
                    "📈 TOP MOVERS (24H)",
                    f"🚀 Best: {gainer_symbol} +{gainer_pct}%",
                    f"📉 Worst: {loser_symbol} {loser_pct}%\n"
                ])

        # Trading opportunities
        if top_shorts is not None and len(top_shorts) > 0:
            sections.append("🔻 SHORT OPPORTUNITIES:")
            for i in range(min(2, len(top_shorts))):
                coin = safe_get(top_shorts, 'slug', i)
                bearish = safe_get(top_shorts, 'bearish', i)
                sections.append(f"• {coin} (Bearish: {bearish})")

        if top_longs is not None and len(top_longs) > 0:
            sections.append("\n🔺 LONG OPPORTUNITIES:")
            for i in range(min(2, len(top_longs))):
                coin = safe_get(top_longs, 'slug', i)
                bullish = safe_get(top_longs, 'bullish', i)
                sections.append(f"• {coin} (Bullish: {bullish})")

        # Engagement & hashtags
        sections.extend([
            "\n💎 What's your move? Drop your thoughts! 👇",
            "Follow @cryptoprism.io for daily insights!",
            "\n#Crypto #Bitcoin #Trading #MarketUpdate #CryptoPrism #BullishOrBearish"
        ])

        caption = '\n'.join(sections)
        return truncate_caption(caption, 2200)

    except Exception as e:
        print(f"⚠️ Error generating base caption: {e}")
        return "🚨 Crypto Market Update! 📈\n\nDaily market analysis coming your way.\n\n#Crypto #MarketUpdate #CryptoPrism"

def generate_ai_caption(base_caption):
    """Generate AI-enhanced caption with fallback using OpenRouter API"""
    try:
        client = create_openrouter_client()

        prompt = f"""Create a 1900-character Instagram caption from this crypto data:

{base_caption}

Rules:
- MAX 1900 characters (strict)
- Hook opening line
- Mobile-friendly format
- Strategic emojis
- Include @cryptoprism.io mention
- 2-3 engagement CTAs
- End with hashtags
- NO markdown formatting
- NO "Here's your caption" responses

Make it engaging and scroll-stopping!"""

        result = client.generate_with_fallback(
            prompt=prompt,
            preferred_models=['gpt-4o-mini', 'claude-haiku', 'gemma-2-9b'],
            max_tokens=500,
            temperature=0.7
        )

        if not result['success']:
            print(f"⚠️ OpenRouter API failed: {result['error']}, using base caption")
            return base_caption

        ai_caption = result['content']

        # Clean AI commentary
        lines = [line.strip() for line in ai_caption.split('\n')
                if line.strip() and not any(phrase in line.lower()
                for phrase in ['here is', 'here\'s', 'caption:'])]

        ai_caption = '\n'.join(lines)
        ai_caption = truncate_caption(ai_caption, 2000)

        if len(ai_caption) > 100:
            print(f"✅ AI caption generated ({len(ai_caption)} chars)")
            return ai_caption
        else:
            print("⚠️ AI caption too short, using base")
            return base_caption

    except Exception as e:
        print(f"⚠️ AI generation failed: {e}")
        return base_caption

def generate_social_media_caption(market_data=None, btc_data=None, gainer_data=None,
                                loser_data=None, top_shorts=None, top_longs=None):
    """Generate complete social media caption with AI enhancement."""
    print("🔄 Generating caption...")

    # Generate base caption
    base_caption = generate_base_caption(market_data, btc_data, gainer_data,
                                       loser_data, top_shorts, top_longs)
    print(f"✅ Base caption: {len(base_caption)} characters")

    # Generate AI-enhanced version
    final_caption = generate_ai_caption(base_caption)
    print(f"✅ Final caption: {len(final_caption)} characters")

    # Ensure we have a caption (fallback is allowed for captions)
    if not final_caption or len(final_caption) < 50:
        final_caption = base_caption
        print("⚠️ Using base caption as fallback")

    return final_caption