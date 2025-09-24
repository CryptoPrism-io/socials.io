"""Template rendering engine using Jinja2 for HTML content generation."""

import os
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

class TemplateRenderer:
    """HTML template renderer with Jinja2."""

    def __init__(self, template_dir=None):
        """Initialize the template renderer."""
        if template_dir is None:
            # Default to base_templates directory
            template_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'base_templates')

        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def render_template(self, template_name, context):
        """Render a template with given context."""
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            print(f"Error rendering template {template_name}: {e}")
            return ""

    def save_rendered_html(self, content, output_path):
        """Save rendered HTML content to file."""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"HTML saved to {output_path}")
            return True
        except Exception as e:
            print(f"Error saving HTML to {output_path}: {e}")
            return False

    def get_current_datetime(self):
        """Get formatted current date and time."""
        now = datetime.now()
        return {
            'current_date': now.strftime("%d %b, %Y"),  # Example: 17 Sep, 2025
            'current_time': now.strftime("%I:%M:%S %p")  # Example: 02:07:45 PM
        }

    def prepare_coins_data(self, df, coins_per_column=8):
        """Split DataFrame into columns for template rendering."""
        if df.empty:
            return {}, {}, {}

        # Split into 3 columns
        total_coins = len(df)
        col1_end = min(coins_per_column, total_coins)
        col2_end = min(coins_per_column * 2, total_coins)

        coins_part1 = df.iloc[0:col1_end].to_dict(orient='records') if col1_end > 0 else []
        coins_part2 = df.iloc[col1_end:col2_end].to_dict(orient='records') if col2_end > col1_end else []
        coins_part3 = df.iloc[col2_end:].to_dict(orient='records') if total_coins > col2_end else []

        return coins_part1, coins_part2, coins_part3

    def render_coins_page(self, template_name, df, output_path):
        """Render a cryptocurrency listing page."""
        if df.empty:
            print(f"No data to render for {template_name}")
            return False

        # Prepare data
        coins1, coins2, coins3 = self.prepare_coins_data(df)
        datetime_info = self.get_current_datetime()

        # Render template
        context = {
            'coins1': coins1,
            'coins2': coins2,
            'coins3': coins3,
            **datetime_info
        }

        content = self.render_template(template_name, context)
        return self.save_rendered_html(content, output_path)

    def render_gainers_losers_page(self, template_name, gainers_df, losers_df, output_path):
        """Render a page with top gainers and losers."""
        gainers_data = gainers_df.to_dict(orient='records') if not gainers_df.empty else []
        losers_data = losers_df.to_dict(orient='records') if not losers_df.empty else []

        context = {
            'coin1': losers_data,  # Top losers
            'coin2': gainers_data  # Top gainers
        }

        content = self.render_template(template_name, context)
        return self.save_rendered_html(content, output_path)

    def render_trading_opportunities_page(self, template_name, long_df, short_df, output_path):
        """Render a trading opportunities page."""
        long_positions = long_df.to_dict(orient='records') if not long_df.empty else []
        short_positions = short_df.to_dict(orient='records') if not short_df.empty else []

        context = {
            'coins1': long_positions,
            'coins2': short_positions
        }

        content = self.render_template(template_name, context)
        return self.save_rendered_html(content, output_path)

    def render_market_overview_page(self, template_name, global_data, btc_data, output_path):
        """Render market overview page with global data and BTC snapshot."""
        # Get logos for BTC and ETH
        btc_logo = ""
        eth_logo = ""

        if not btc_data.empty and 'logo' in btc_data.columns:
            btc_logo = btc_data['logo'].iloc[0] if not pd.isnull(btc_data['logo'].iloc[0]) else ""

        # For ETH logo, we'd need to fetch it separately or include it in the data
        # This is a placeholder - you might want to add ETH data fetching
        eth_logo = "https://s2.coinmarketcap.com/static/img/coins/64x64/1027.png"  # Placeholder

        datetime_info = self.get_current_datetime()

        context = {
            'coins': global_data.to_dict(orient='records') if not global_data.empty else [],
            'snap': btc_data.to_dict(orient='records') if not btc_data.empty else [],
            'btc_logo': btc_logo,
            'eth_logo': eth_logo,
            **datetime_info
        }

        content = self.render_template(template_name, context)
        return self.save_rendered_html(content, output_path)

    def render_btc_snapshot_page(self, template_name, btc_data, news_events, output_path):
        """Render Bitcoin snapshot page with news and events."""
        datetime_info = self.get_current_datetime()

        context = {
            'snap': btc_data.to_dict(orient='records') if not btc_data.empty else [],
            'news_events': news_events,
            **datetime_info
        }

        content = self.render_template(template_name, context)
        return self.save_rendered_html(content, output_path)

def get_template_renderer():
    """Factory function to get a configured template renderer."""
    return TemplateRenderer()