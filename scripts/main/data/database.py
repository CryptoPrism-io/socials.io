"""Database connection and operations module for socials.io."""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os

# Database connection configuration
DB_CONFIG = {
    'host': '34.55.195.199',        # GCP PostgreSQL instance public IP
    'database': 'dbcp',             # Database name
    'user': 'yogass09',             # Username
    'password': 'jaimaakamakhya',   # Password
    'port': 5432                    # PostgreSQL default port
}

def get_gcp_engine():
    """Create and return a SQLAlchemy engine for the GCP PostgreSQL database."""
    connection_url = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@" \
                     f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    return create_engine(connection_url)

# Initialize the GCP engine
gcp_engine = get_gcp_engine()

def fetch_crypto_data(query):
    """Execute a SQL query and return results as DataFrame."""
    try:
        df = pd.read_sql_query(query, gcp_engine)
        return df
    except Exception as e:
        print(f"Error executing query: {e}")
        return pd.DataFrame()

def fetch_top_coins(start_rank=1, end_rank=24):
    """Fetch top cryptocurrency data by rank range with DMV scores."""
    query = f"""
      SELECT
        c.slug, c.cmc_rank, c.last_updated, c.symbol, c.price, c.percent_change24h, c.market_cap,
        d."Durability_Score", d."Momentum_Score", d."Valuation_Score"
      FROM crypto_listings_latest_1000 c
      LEFT JOIN "FE_DMV_SCORES" d ON c.slug = d.slug
      WHERE c.cmc_rank BETWEEN {start_rank} AND {end_rank}
      """

    try:
        df = pd.read_sql_query(query, gcp_engine)
        # Convert market_cap to billions and round to 2 decimal places
        df['market_cap'] = (df['market_cap'] / 1_000_000_000).round(2)
        df['price'] = (df['price']).round(2)
        df['percent_change24h'] = (df['percent_change24h']).round(2)

        # Fetch logos
        slugs = df['slug'].tolist()
        slugs_placeholder = ', '.join(f"'{slug}'" for slug in slugs)

        query_logos = f"""
        SELECT logo, slug FROM "FE_CC_INFO_URL"
        WHERE slug IN ({slugs_placeholder})
        """

        logos_and_slugs = pd.read_sql_query(query_logos, gcp_engine)
        df = pd.merge(df, logos_and_slugs, on='slug', how='left')
        df = df.sort_values(by='cmc_rank', ascending=True)

        return df

    except Exception as e:
        print(f"Error fetching top coins data: {e}")
        return pd.DataFrame()

def fetch_btc_snapshot():
    """Fetch comprehensive Bitcoin data including sentiment analysis."""
    query_top_1 = """
    SELECT slug, cmc_rank, last_updated, symbol, price, percent_change24h, volume24h, market_cap, percent_change7d, percent_change30d, ytd_price_change_percentage
    FROM crypto_listings_latest_1000
    WHERE cmc_rank < 2
    """

    try:
        btc_data = pd.read_sql_query(query_top_1, gcp_engine)

        # Format market cap and volume
        def format_market_cap(market_cap):
            if pd.isnull(market_cap):
                return market_cap
            market_cap = float(market_cap)
            if market_cap >= 1e12:
                return f"${market_cap / 1e12:.2f} T"
            elif market_cap >= 1e9:
                return f"${market_cap / 1e9:.2f} B"
            elif market_cap >= 1e6:
                return f"${market_cap / 1e6:.2f} M"
            else:
                return f"${market_cap:.2f}"

        btc_data['market_cap'] = btc_data['market_cap'].apply(format_market_cap)
        btc_data['volume24h'] = btc_data['volume24h'].apply(format_market_cap)

        # Format percentage changes
        for col in ['percent_change24h', 'percent_change7d', 'percent_change30d', 'ytd_price_change_percentage']:
            btc_data[col] = btc_data[col].apply(lambda x: f"{x:.2f}" if not pd.isnull(x) else x)

        # Format price
        btc_data['price'] = btc_data['price'].apply(lambda x: f"${x:.2f}" if not pd.isnull(x) else x)

        # Fetch DMV data for sentiment analysis - get specific sentiment columns
        dmv_query = """
        SELECT
          "bullish",
          "bearish",
          "neutral"
        FROM
          "public"."FE_DMV_ALL"
        WHERE
          "slug" = 'bitcoin'
        """
        dmv_bitcoin = pd.read_sql_query(dmv_query, gcp_engine)

        if not dmv_bitcoin.empty:
            # The columns now directly contain the sentiment values
            bullish_count = int(dmv_bitcoin.iloc[0]['bullish'])
            bearish_count = int(dmv_bitcoin.iloc[0]['bearish'])
            neutral_count = int(dmv_bitcoin.iloc[0]['neutral'])

            # Reduce neutral by 11 as requested (hardcoded adjustment)
            neutral_count = neutral_count - 11 if neutral_count > 11 else 0

            btc_data.loc[0, 'bullish'] = bullish_count
            btc_data.loc[0, 'bearish'] = bearish_count
            btc_data.loc[0, 'neutral'] = neutral_count
            btc_data.loc[0, 'sentiment_diff'] = bullish_count - bearish_count

            # Classify trend with 6 categories based on sentiment strength
            def classify_trend(sentiment_diff):
                if sentiment_diff > 8:
                    return "Bullish+"  # Extreme bullish sentiment
                elif sentiment_diff > 4:
                    return "Bullish"   # Strong bullish sentiment
                elif sentiment_diff >= 2:
                    return "Consolidating+"  # Slight bullish lean
                elif sentiment_diff >= -4:
                    return "Consolidating-"  # Slight bearish lean
                elif sentiment_diff >= -8:
                    return "Bearish"   # Strong bearish sentiment
                else:
                    return "Bearish-"  # Extreme bearish sentiment

            trend_value = classify_trend(bullish_count - bearish_count)
            btc_data.loc[0, 'Trend'] = trend_value

            # Map Trend to colors
            color_map = {
                "Bullish+": "orange",
                "Bullish": "green",
                "Consolidating+": "blue",
                "Consolidating-": "lightblue",
                "Bearish": "red",
                "Bearish-": "orange"
            }
            btc_data.loc[0, 'color'] = color_map.get(trend_value, "gray")

            print(f"DEBUG 6-Category Trend: bullish={bullish_count}, bearish={bearish_count}, diff={bullish_count - bearish_count}, trend={trend_value}")

        # Fetch real Fear & Greed Index data from database
        def get_fear_greed_label(value):
            if value <= 25:
                return "Extreme Fear"
            elif value <= 45:
                return "Fear"
            elif value <= 55:
                return "Neutral"
            elif value <= 75:
                return "Greed"
            else:
                return "Extreme Greed"

        # Get historical Fear & Greed Index data from database (last 30 days)
        fear_greed_query = '''
        SELECT
            timestamp,
            fear_greed_index,
            sentiment
        FROM "FE_FEAR_GREED_CMC"
        ORDER BY timestamp DESC
        LIMIT 30
        '''

        fear_greed_df = pd.read_sql_query(fear_greed_query, gcp_engine)

        # Fetch Bitcoin historical price data (last 31 days - to match Fear & Greed data)
        btc_price_query = '''
        SELECT
          "timestamp",
          "slug",
          "name",
          "close"
        FROM
          "public"."1K_coins_ohlcv"
        WHERE
          "slug" = 'bitcoin'
        ORDER BY
          "timestamp" DESC
        LIMIT
          31
        '''

        btc_price_df = pd.read_sql_query(btc_price_query, gcp_engine)
        print(f"🔍 Debug: btc_price_history has {len(btc_price_df)} entries")

        # Convert to the format expected by the template (reverse order for chronological display)
        fear_greed_history = []
        # Process Bitcoin price data (reverse to match chronological order)
        if not btc_price_df.empty:
            btc_price_df = btc_price_df.iloc[::-1].reset_index(drop=True)  # Reverse for chronological order

            # Calculate price scaling for secondary y-axis
            btc_prices = [float(row['close']) for _, row in btc_price_df.iterrows()]
            btc_min_price = min(btc_prices)
            btc_max_price = max(btc_prices)
            print(f"💰 BTC price range: ${btc_min_price:.0f}-${btc_max_price:.0f}")

        if not fear_greed_df.empty:
            # Reverse to get chronological order (oldest to newest)
            fear_greed_df = fear_greed_df.iloc[::-1].reset_index(drop=True)

            # Calculate min/max for dynamic scaling
            min_val = fear_greed_df['fear_greed_index'].min()
            max_val = fear_greed_df['fear_greed_index'].max()

            # Add some padding to the range for better visualization
            range_padding = (max_val - min_val) * 0.2
            scaled_min = max(0, min_val - range_padding)  # Don't go below 0
            scaled_max = min(100, max_val + range_padding)  # Don't go above 100

            print(f"📊 Fear & Greed data range: {min_val}-{max_val}, scaled: {scaled_min:.1f}-{scaled_max:.1f}")

            for i, row in fear_greed_df.iterrows():
                # Scale value to use full chart height (0-100 range mapped to 0-300px)
                raw_value = int(row['fear_greed_index'])

                # Map the actual data range to the full 0-100 display range for better visualization
                if scaled_max > scaled_min:
                    # Normalize to 0-1, then scale to utilize more of the chart space
                    normalized = (raw_value - scaled_min) / (scaled_max - scaled_min)
                    # Map to 20-80 range instead of 0-100 for better visual impact
                    scaled_value = 20 + (normalized * 60)
                else:
                    scaled_value = raw_value

                # Get corresponding Bitcoin price for this data point (if available)
                btc_price = 0
                if not btc_price_df.empty and i < len(btc_price_df):
                    btc_price = float(btc_price_df.iloc[i]['close'])

                fear_greed_history.append({
                    'day': i + 1,
                    'value': int(scaled_value),  # Use scaled value for chart positioning
                    'raw_value': raw_value,     # Keep original for reference
                    'price': btc_price,         # Bitcoin price for this data point
                    'label': row['sentiment']   # Use actual sentiment from database
                })

        # Get current fear/greed index (most recent)
        if not fear_greed_df.empty:
            latest_fear_greed = fear_greed_df.iloc[-1]  # Last row after reversal = most recent
            current_fear_greed = int(latest_fear_greed['fear_greed_index'])
            current_fear_greed_label = latest_fear_greed['sentiment']
        else:
            # If no data available, use defaults (but this shouldn't happen)
            current_fear_greed = 50
            current_fear_greed_label = "Neutral"

        btc_data.loc[0, 'fear_greed_index'] = current_fear_greed
        btc_data.loc[0, 'fear_greed_label'] = current_fear_greed_label

        # Store fear_greed_history as a column (will be handled properly in template)
        # Note: We can't use DataFrame.attrs as they get lost in pandas operations
        btc_data.loc[0, 'fear_greed_history_json'] = str(fear_greed_history)

        # Add Bitcoin price scaling data for dual-axis chart
        if not btc_price_df.empty:
            btc_data.loc[0, 'btc_min_price'] = btc_min_price
            btc_data.loc[0, 'btc_max_price'] = btc_max_price
        else:
            # Default values if no price data
            btc_data.loc[0, 'btc_min_price'] = 0
            btc_data.loc[0, 'btc_max_price'] = 120000

        # Remove synthetic altseason data - use real data or remove entirely
        # For now, setting to neutral values
        btc_data.loc[0, 'altseason_gauge'] = 90  # Neutral value
        btc_data.loc[0, 'altseason_status'] = "No"

        # Fetch logo
        logo_query = "SELECT logo, slug FROM \"FE_CC_INFO_URL\" WHERE slug = 'bitcoin'"
        logo_data = pd.read_sql_query(logo_query, gcp_engine)
        btc_data = pd.merge(btc_data, logo_data, on='slug', how='left')

        return btc_data

    except Exception as e:
        print(f"Error fetching BTC snapshot: {e}")
        return pd.DataFrame()

def fetch_global_market_data():
    """Fetch global cryptocurrency market data."""
    query = """
    SELECT
        total_market_cap,
        total_volume24h_reported,
        altcoin_volume24h_reported,
        altcoin_market_cap,
        total_market_cap_yesterday_percentage_change,
        total_volume24h_yesterday_percentage_change,
        derivatives_volume24h_reported,
        derivatives24h_percentage_change,
        active_crypto_currencies,
        total_crypto_currencies,
        active_exchanges,
        total_exchanges,
        stablecoin_volume24h_reported,
        stablecoin_market_cap,
        stablecoin24h_percentage_change,
        defi_volume24h_reported,
        defi_market_cap,
        defi24h_percentage_change,
        btc_dominance24h_percentage_change,
        eth_dominance24h_percentage_change,
        btc_dominance,
        eth_dominance
    FROM
        crypto_global_latest
    """

    try:
        global_data = pd.read_sql_query(query, gcp_engine)

        # Format large numbers
        def format_large_number(value, include_dollar=True):
            if pd.isnull(value):
                return value
            value = float(value)
            prefix = "$" if include_dollar else ""

            if value >= 1e12:
                return f"{prefix}{value / 1e12:.2f} T"
            elif value >= 1e9:
                return f"{prefix}{value / 1e9:.2f} B"
            elif value >= 1e6:
                return f"{prefix}{value / 1e6:.2f} M"
            elif value >= 1e3:
                return f"{prefix}{value / 1e3:.2f} K"
            else:
                return f"{prefix}{value:.2f}"

        # Apply formatting
        for col in ['total_market_cap', 'total_volume24h_reported', 'derivatives_volume24h_reported', 'defi_volume24h_reported']:
            global_data[col] = global_data[col].apply(lambda x: format_large_number(x, include_dollar=False))

        # Convert to billions for other columns
        for col in ['altcoin_volume24h_reported', 'altcoin_market_cap', 'stablecoin_volume24h_reported', 'stablecoin_market_cap', 'defi_market_cap']:
            global_data[col] = (global_data[col] / 1_000_000_000).round(2)

        # Round percentages
        percentage_cols = ['total_market_cap_yesterday_percentage_change', 'total_volume24h_yesterday_percentage_change',
                          'derivatives24h_percentage_change', 'stablecoin24h_percentage_change', 'defi24h_percentage_change',
                          'btc_dominance24h_percentage_change', 'eth_dominance24h_percentage_change', 'btc_dominance', 'eth_dominance']
        for col in percentage_cols:
            global_data[col] = global_data[col].round(2)

        return global_data

    except Exception as e:
        print(f"Error fetching global market data: {e}")
        return pd.DataFrame()

def fetch_trading_opportunities(opportunity_type="long", limit=15):
    """Fetch trading opportunities based on sentiment analysis."""
    if opportunity_type == "long":
        query = f"""
        SELECT
          "FE_DMV_ALL"."id",
          "FE_DMV_ALL"."slug",
          "FE_DMV_ALL"."name",
          "FE_DMV_ALL"."bullish",
          "FE_DMV_ALL"."bearish",
          "crypto_listings_latest_1000"."symbol",
          "crypto_listings_latest_1000"."percent_change24h",
          "crypto_listings_latest_1000"."percent_change7d",
          "crypto_listings_latest_1000"."percent_change30d",
          "crypto_listings_latest_1000"."cmc_rank",
          "crypto_listings_latest_1000"."price",
          "crypto_listings_latest_1000"."market_cap",
          "FE_CC_INFO_URL"."logo",
          "FE_RATIOS"."m_rat_alpha",
          "FE_RATIOS"."d_rat_beta",
          "FE_RATIOS"."m_rat_omega",
          d."Durability_Score",
          d."Momentum_Score",
          d."Valuation_Score"
        FROM
          "FE_DMV_ALL"
        JOIN
          "crypto_listings_latest_1000"
        ON
          "FE_DMV_ALL"."slug" = "crypto_listings_latest_1000"."slug"
        JOIN
          "FE_CC_INFO_URL"
        ON
          "FE_DMV_ALL"."slug" = "FE_CC_INFO_URL"."slug"
        JOIN
          "FE_RATIOS"
        ON
          "FE_DMV_ALL"."slug" = "FE_RATIOS"."slug"
        JOIN
          "FE_DMV_SCORES" d ON "FE_DMV_ALL"."slug" = d.slug
        WHERE
          "crypto_listings_latest_1000"."cmc_rank" < 100
          AND ("FE_RATIOS"."d_rat_beta" > 1 OR "FE_RATIOS"."d_rat_beta" IS NULL)
          AND ("FE_RATIOS"."m_rat_omega" > 1 OR "FE_RATIOS"."m_rat_omega" IS NULL)
        ORDER BY
          "FE_DMV_ALL"."bullish" DESC
        LIMIT
          {limit};
        """
    else:  # short opportunities
        query = f"""
        SELECT
          "FE_DMV_ALL"."id",
          "FE_DMV_ALL"."slug",
          "FE_DMV_ALL"."name",
          "FE_DMV_ALL"."bullish",
          "FE_DMV_ALL"."bearish",
          "crypto_listings_latest_1000"."symbol",
          "crypto_listings_latest_1000"."percent_change24h",
          "crypto_listings_latest_1000"."percent_change7d",
          "crypto_listings_latest_1000"."percent_change30d",
          "crypto_listings_latest_1000"."cmc_rank",
          "crypto_listings_latest_1000"."price",
          "crypto_listings_latest_1000"."market_cap",
          "FE_CC_INFO_URL"."logo",
          "FE_RATIOS"."m_rat_alpha",
          "FE_RATIOS"."d_rat_beta",
          "FE_RATIOS"."m_rat_omega",
          d."Durability_Score",
          d."Momentum_Score",
          d."Valuation_Score"
        FROM
          "FE_DMV_ALL"
        JOIN
          "crypto_listings_latest_1000"
        ON
          "FE_DMV_ALL"."slug" = "crypto_listings_latest_1000"."slug"
        JOIN
          "FE_CC_INFO_URL"
        ON
          "FE_DMV_ALL"."slug" = "FE_CC_INFO_URL"."slug"
        JOIN
          "FE_RATIOS"
        ON
          "FE_DMV_ALL"."slug" = "FE_RATIOS"."slug"
        JOIN
          "FE_DMV_SCORES" d ON "FE_DMV_ALL"."slug" = d.slug
        WHERE
          "crypto_listings_latest_1000"."cmc_rank" < 100
          AND ("FE_RATIOS"."d_rat_beta" > 1 OR "FE_RATIOS"."d_rat_beta" IS NULL)
          AND ("FE_RATIOS"."m_rat_omega" < 2 OR "FE_RATIOS"."m_rat_omega" IS NULL)
        ORDER BY
          "FE_DMV_ALL"."bearish" DESC
        LIMIT
          {limit};
        """

    try:
        df = pd.read_sql_query(query, gcp_engine)

        # Convert and format numeric columns with error handling
        numeric_cols = ['market_cap', 'price', 'percent_change24h', 'percent_change7d', 'percent_change30d',
                       'bullish', 'bearish', 'm_rat_alpha', 'd_rat_beta', 'm_rat_omega', 'Durability_Score', 'Momentum_Score', 'Valuation_Score']

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Format specific columns after conversion
        if 'market_cap' in df.columns:
            df['market_cap'] = (df['market_cap'] / 1_000_000_000).round(2)
        if 'price' in df.columns:
            df['price'] = df['price'].round(2)

        # Round percentage and ratio columns
        for col in ['percent_change24h', 'percent_change7d', 'percent_change30d', 'm_rat_alpha', 'd_rat_beta', 'm_rat_omega']:
            if col in df.columns:
                df[col] = df[col].round(2)

        return df

    except Exception as e:
        print(f"Error fetching {opportunity_type} opportunities: {e}")
        return pd.DataFrame()

def close_connection():
    """Close the database connection."""
    try:
        gcp_engine.dispose()
        print("Database connection closed.")
    except Exception as e:
        print(f"Error closing connection: {e}")