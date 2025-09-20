#!/usr/bin/env python3
"""
Consolidated Instagram content generation script.
Replaces multiple instapost scripts with unified CLI interface.
"""
import asyncio
import argparse
import os
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Optional

# Async imports
from playwright.async_api import async_playwright
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime

# Import centralized configuration, logging, and retry utilities
from config import config
from logging_config import logger, CorrelationContext, log_operation_start, log_operation_end, log_error
from retry_utils import database_retry_manager, playwright_retry_manager

# Legacy compatibility functions for backward compatibility
async def get_gcp_engine():
    """Create and return a SQLAlchemy engine using centralized config with retry logic."""
    from retry_utils import retry_async

    def _create_engine():
        """Internal synchronous engine creation."""
        return create_engine(
            config.database.get_connection_url(),
            pool_pre_ping=True,  # Test connections before use
            pool_recycle=3600,   # Recycle connections after 1 hour
        )

    try:
        # Execute with retry logic for initial connection
        engine = await retry_async(_create_engine, manager=database_retry_manager)
        logger.info("Database connection established successfully")
        return engine
    except Exception as e:
        logger.error(f"Failed to establish database connection: {e}", extra={
            "event": "db_connection_failed",
            "db_host": config.database.host,
            "db_port": config.database.port
        })
        raise ValueError(f"Database configuration error: {e}")

# Global Jinja environment
jinja_env = Environment(loader=FileSystemLoader(str(config.paths.templates_dir)))

async def generate_image_from_html(output_html_file: str, output_image_path: str, viewport_width: Optional[int] = None):
    """Launch Playwright, load the HTML file, and save a screenshot of it with retry logic."""
    from retry_utils import retry_async

    async def _generate_image():
        """Internal async image generation function."""
        async with async_playwright() as p:
            # Add timeout for browser launch
            browser = await asyncio.wait_for(
                p.chromium.launch(headless=True),
                timeout=config.image.browser_timeout
            )

            try:
                page = await browser.new_page()

                # Use config values if not specified
                width = viewport_width or config.image.width
                height = config.image.height or width  # Square aspect ratio for Instagram

                await page.set_viewport_size({"width": width, "height": height})
                await page.emulate_media(media='screen')

                # Load the rendered HTML file with timeout
                html_path = Path(output_html_file).absolute()
                await asyncio.wait_for(
                    page.goto(f'file://{html_path}'),
                    timeout=config.image.browser_timeout
                )

                # Ensure image output directory exists
                image_path = Path(output_image_path)
                image_path.parent.mkdir(parents=True, exist_ok=True)

                # Capture the screenshot of the page with timeout
                await asyncio.wait_for(
                    page.screenshot(
                        path=str(image_path),
                        type=config.image.format,
                        quality=config.image.quality,
                        full_page=True
                    ),
                    timeout=config.image.browser_timeout
                )

                return image_path

            finally:
                await browser.close()

    operation_context = log_operation_start(
        logger, "generate_image",
        _log_html_file=output_html_file,
        _log_image_file=output_image_path
    )

    try:
        # Execute with retry logic
        image_path = await retry_async(_generate_image, manager=playwright_retry_manager)

        log_operation_end(
            logger, operation_context, success=True,
            _log_file_size_mb=round(image_path.stat().st_size / (1024 * 1024), 2)
        )
        print(f"✓ Generated image: {output_image_path}")

    except Exception as e:
        log_error(logger, e, "generate_image", _log_html_file=output_html_file, _log_image_file=output_image_path)
        log_operation_end(logger, operation_context, success=False, _log_error=str(e))
        raise

async def fetch_data_top_24_coins(engine) -> pd.DataFrame:
    """Fetch data from the 'coins' table and return as a Pandas DataFrame with retry logic."""
    from retry_utils import retry_async

    def _fetch_data():
        """Internal synchronous data fetching function."""
        query_top_24 = """
          SELECT slug, cmc_rank, last_updated, symbol, price, percent_change24h, market_cap, last_updated
          FROM crypto_listings_latest_1000
          WHERE cmc_rank BETWEEN 1 AND 24
          """

        df = pd.read_sql_query(query_top_24, engine)
        df['market_cap'] = (df['market_cap'] / 1_000_000_000).round(2)
        df['price'] = (df['price']).round(2)
        df['percent_change24h'] = (df['percent_change24h']).round(2)

        # Get logos for the coins
        slugs = df['slug'].tolist()
        slugs_placeholder = ', '.join(f"'{slug}'" for slug in slugs)

        query_logos = f"""
        SELECT logo, slug FROM "FE_CC_INFO_URL"
        WHERE slug IN ({slugs_placeholder})
        """
        logos_df = pd.read_sql_query(query_logos, engine)
        df = pd.merge(df, logos_df, on='slug', how='left')
        df = df.sort_values(by='cmc_rank', ascending=True)

        return df

    operation_context = log_operation_start(
        logger, "fetch_crypto_data",
        _log_query_type="top_24_coins"
    )

    try:
        # Execute with retry logic
        df = await retry_async(_fetch_data, manager=database_retry_manager)

        log_operation_end(
            logger, operation_context, success=True,
            _log_record_count=len(df),
            _log_has_logos=df['logo'].notna().sum() > 0
        )

        return df

    except Exception as e:
        log_error(logger, e, "fetch_crypto_data", _log_query_type="top_24_coins")
        log_operation_end(logger, operation_context, success=False, _log_error=str(e))
        return pd.DataFrame()

def fetch_bitcoin_data(engine) -> Dict:
    """Fetch Bitcoin-specific data for Template 6."""
    query_btc = """
    SELECT * FROM crypto_listings_latest_1000
    WHERE symbol = 'BTC' LIMIT 1
    """
    try:
        btc_df = pd.read_sql_query(query_btc, engine)
        if btc_df.empty:
            return {}

        btc = btc_df.iloc[0].to_dict()
        btc['market_cap'] = f"{btc['market_cap'] / 1e9:.1f} T" if btc['market_cap'] else 'N/A'
        btc['volume24h'] = f"{btc['volume24h'] / 1e9:.1f} B" if btc['volume24h'] else 'N/A'
        return btc
    except Exception as e:
        print(f"Error fetching Bitcoin data: {e}")
        return {}

async def fetch_template_data(template_num: int, engine) -> Dict:
    """Fetch data for any template (1-19) with appropriate data structure."""
    try:
        # Get common timestamp data
        common_data = {
            'current_date': datetime.now(config.app.timezone).strftime(config.app.datetime_format),
            'current_time': datetime.now(config.app.timezone).strftime(config.app.time_format)
        }

        if template_num <= 5:
            # Templates 1-5: Multi-coin data with different slicing
            coins_data = await fetch_data_top_24_coins(engine)
            if coins_data.empty:
                return {}

            start_idx = (template_num - 1) * 24
            end_idx = start_idx + 24
            template_data = coins_data.iloc[start_idx:end_idx] if start_idx < len(coins_data) else coins_data.iloc[:24]

            common_data['snap'] = [row.to_dict() for _, row in template_data.iterrows()]
            return common_data

        elif template_num == 6:
            # Template 6: Bitcoin-specific data with AI analysis
            btc_data = fetch_bitcoin_data(engine)
            if not btc_data:
                return {}

            # Add Template 6 specific data structure
            common_data.update({
                'snap': [btc_data],
                'market_vibes': {
                    'overall_mood': 'Optimistic',
                    'emoji': '🚀',
                    'description': 'Strong momentum across major assets',
                    'social_sentiment': 7.8
                },
                'giants': [btc_data],  # Can add ETH, BNB later
                'catalysts': [
                    {
                        'event': 'Bitcoin ETF Decision',
                        'date': '2024-01-10',
                        'impact': 'High',
                        'probability': 85
                    }
                ]
            })
            return common_data

        elif template_num == 7:
            # Template 7: Top Gainers & Losers
            coins_data = await fetch_data_top_24_coins(engine)
            if coins_data.empty:
                return {}

            # Sort by percent_change24h for gainers and losers
            gainers = coins_data.nlargest(10, 'percent_change24h')
            losers = coins_data.nsmallest(10, 'percent_change24h')

            common_data.update({
                'top_gainers': [row.to_dict() for _, row in gainers.iterrows()],
                'top_losers': [row.to_dict() for _, row in losers.iterrows()]
            })
            return common_data

        elif template_num >= 8 and template_num <= 16:
            # Templates 8-16: Mock data for now (external APIs needed)
            return generate_mock_data_for_template(template_num, common_data)

        elif template_num >= 17 and template_num <= 19:
            # Templates 17-19: Trading performance data (mock for now)
            return generate_trading_mock_data(template_num, common_data)

        else:
            return {}

    except Exception as e:
        print(f"Error fetching data for template {template_num}: {e}")
        return {}

def generate_mock_data_for_template(template_num: int, base_data: Dict) -> Dict:
    """Generate mock data for templates 8-16 that require external APIs."""
    mock_data = base_data.copy()

    if template_num == 8:  # Breaking News
        mock_data['breaking_news'] = [
            {
                'headline': 'SEC Approves First Bitcoin ETF',
                'timestamp': '2024-01-09T14:30:00Z',
                'impact_rating': 'High',
                'affected_coins': ['BTC', 'ETH'],
                'social_buzz_score': 9.2,
                'source': 'Reuters',
                'category': 'Regulation'
            }
        ]
    elif template_num == 9:  # Liquidations
        mock_data.update({
            'total_liquidations_24h': '$847.2M',
            'long_liquidations': '$523.1M',
            'short_liquidations': '$324.1M',
            'long_short_ratio': 61.7
        })
    elif template_num == 10:  # Fear & Greed
        mock_data.update({
            'current_score': 67,
            'current_label': 'Greed',
            'trend_7d': '+12 points',
            'components': {
                'volatility': 15,
                'momentum': 25,
                'social_media': 20
            }
        })
    # Add more mock data for templates 11-16 as needed

    return mock_data

def generate_trading_mock_data(template_num: int, base_data: Dict) -> Dict:
    """Generate mock trading performance data for templates 17-19."""
    mock_data = base_data.copy()

    if template_num == 17:  # Trade History
        mock_data.update({
            'recent_trades': [
                {
                    'id': 'TRD_001',
                    'symbol': 'BTC',
                    'trade_type': 'LONG',
                    'entry_date': '2024-01-05',
                    'exit_date': '2024-01-08',
                    'entry_price': '$42,150.00',
                    'exit_price': '$44,280.00',
                    'quantity': '0.5 BTC',
                    'pnl_usd': '+$1,065.00',
                    'pnl_percentage': '+5.05%',
                    'duration': '3 days',
                    'status': 'WIN',
                    'risk_reward': '1:2.1'
                }
            ],
            'trade_summary': {
                'total_trades_shown': 10,
                'winning_trades': 7,
                'losing_trades': 3,
                'total_pnl': '+$3,247.80',
                'win_rate': '70%',
                'best_trade': '+$1,950.00 (ETH LONG)',
                'worst_trade': '-$420.00 (AVAX SHORT)'
            }
        })
    elif template_num == 18:  # Portfolio Dashboard
        mock_data.update({
            'portfolio_overview': {
                'total_value_usd': '$127,845.32',
                'value_change_7d': '+$8,247.19',
                'percentage_7d': '+6.9%',
                'percentage_30d': '+23.0%',
                'percentage_90d': '+55.4%'
            },
            'open_positions': [
                {
                    'symbol': 'BTC',
                    'position_size': '2.1 BTC',
                    'entry_avg': '$41,200.00',
                    'current_price': '$43,247.82',
                    'unrealized_pnl': '+$4,300.44',
                    'percentage': '+4.97%',
                    'allocation': '45.2%'
                }
            ],
            'portfolio_allocation': [
                {'symbol': 'BTC', 'percentage': 45.2, 'value': '$57,789.12'},
                {'symbol': 'ETH', 'percentage': 32.1, 'value': '$41,057.89'},
                {'symbol': 'SOL', 'percentage': 12.7, 'value': '$16,236.40'},
                {'symbol': 'CASH', 'percentage': 10.0, 'value': '$12,784.53'}
            ],
            'risk_metrics': {
                'max_drawdown': '-8.4%',
                'volatility_30d': '12.3%',
                'sharpe_ratio': 2.1,
                'beta_vs_btc': 0.87
            }
        })
    elif template_num == 19:  # Trading Statistics
        mock_data.update({
            'trading_statistics': {
                'overall_stats': {
                    'total_trades': 156,
                    'winning_trades': 109,
                    'losing_trades': 47,
                    'win_rate': '69.9%',
                    'total_pnl': '+$127,845.32',
                    'average_win': '+$1,847.23',
                    'average_loss': '-$642.18',
                    'profit_factor': 2.87
                },
                'long_vs_short': {
                    'long_trades': {
                        'count': 98,
                        'wins': 72,
                        'win_rate': '73.5%',
                        'total_pnl': '+$89,234.56'
                    },
                    'short_trades': {
                        'count': 58,
                        'wins': 37,
                        'win_rate': '63.8%',
                        'total_pnl': '+$38,610.76'
                    }
                },
                'monthly_performance': [
                    {'month': 'Dec 2024', 'return': '+18.7%', 'trades': 24},
                    {'month': 'Nov 2024', 'return': '+12.3%', 'trades': 19},
                    {'month': 'Oct 2024', 'return': '+8.9%', 'trades': 22}
                ],
                'best_assets': [
                    {'symbol': 'SOL', 'trades': 23, 'win_rate': '82.6%', 'total_pnl': '+$23,456.78'},
                    {'symbol': 'ETH', 'trades': 31, 'win_rate': '74.2%', 'total_pnl': '+$19,847.32'},
                    {'symbol': 'BTC', 'trades': 45, 'win_rate': '68.9%', 'total_pnl': '+$31,234.67'}
                ],
                'streak_analysis': {
                    'longest_winning_streak': 12,
                    'longest_losing_streak': 4,
                    'current_streak': '7 wins'
                },
                'risk_metrics': {
                    'average_risk_reward': '1:2.3',
                    'max_drawdown': '-12.4%',
                    'calmar_ratio': 3.2,
                    'sortino_ratio': 2.8
                }
            }
        })

    return mock_data

def get_template_name(template_num: int) -> str:
    """Get descriptive name for template output file."""
    template_names = {
        1: "market_overview",
        2: "top_cryptocurrencies",
        3: "ai_crypto_analysis",
        4: "portfolio_tracker",
        5: "trading_signals",
        6: "crypto_vibes",
        7: "top_gainers_losers",
        8: "breaking_news",
        9: "liquidations_dashboard",
        10: "fear_greed_index",
        11: "weekly_market_recap",
        12: "whale_alerts",
        13: "defi_tvl_rankings",
        14: "crypto_calendar",
        15: "layer2_activity",
        16: "meme_coin_tracker",
        17: "trade_history",
        18: "portfolio_dashboard",
        19: "trading_statistics"
    }
    return template_names.get(template_num, f"template_{template_num}")

async def render_template(template_num: int, data: Dict, output_dir: Optional[str] = None) -> Optional[str]:
    """Render HTML from template with data."""
    try:
        template_file = f"{template_num}.html"
        template = jinja_env.get_template(template_file)

        html_content = template.render(**data)

        # Use config output directory if not specified
        output_dir = Path(output_dir) if output_dir else config.paths.html_output_dir

        # Use descriptive naming for output files
        template_name = get_template_name(template_num)
        output_path = output_dir / f"{template_name}_output.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Copy corresponding CSS file to output directory
        await copy_css_to_output(template_num, output_dir)

        print(f"✓ Rendered template {template_num} ({template_name}): {output_path}")
        return str(output_path)

    except Exception as e:
        print(f"Error rendering template {template_num}: {e}")
        return None

async def copy_css_to_output(template_num: int, output_dir: Path):
    """Copy the corresponding CSS file from core_templates to output directory."""
    try:
        # Determine CSS filename based on template number
        if template_num == 1:
            css_filename = "style.css"
        else:
            css_filename = f"style{template_num}.css"

        source_css = config.paths.templates_dir / css_filename
        dest_css = output_dir / css_filename

        # Copy CSS file if it exists
        if source_css.exists():
            import shutil
            shutil.copy2(source_css, dest_css)
            print(f"✓ Copied CSS: {css_filename}")
        else:
            print(f"⚠ CSS file not found: {css_filename}")

    except Exception as e:
        print(f"Error copying CSS for template {template_num}: {e}")

async def convert_to_image(html_path: str, template_num: int):
    """Convert HTML file to Instagram-ready image."""
    template_name = get_template_name(template_num)
    image_path = str(config.paths.images_output_dir / f"{template_name}_output.{config.image.format}")
    await generate_image_from_html(html_path, image_path)

async def main():
    """Main CLI entry point for instapost content generation."""
    parser = argparse.ArgumentParser(description='Instagram content generator for crypto socials')
    parser.add_argument('--template', '-t', type=int, choices=list(range(1,20)), default=None,
                       help='Generate specific template (1-19). If not specified, generates all.')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be generated without actually running')
    parser.add_argument('--skip-generate', action='store_true',
                       help='Skip screenshot generation, only render HTML')
    parser.add_argument('--output-dir', default=None,
                       help='Custom output directory (overrides default)')

    args = parser.parse_args()

    # Set up correlation context for this run
    correlation_id = CorrelationContext.get_current_correlation_id() or str(uuid.uuid4())[:8]
    with CorrelationContext(correlation_id):
        session_context = log_operation_start(
            logger, "content_generation_session",
            _log_template_filter=args.template or "all",
            _log_dry_run=args.dry_run,
            _log_skip_generate=args.skip_generate,
            _log_custom_output_dir=args.output_dir is not None
        )

        try:
            # Ensure all directories exist
            config.paths.ensure_directories()

            logger.info("🚀 Starting Instagram content generation session", extra={
                "templates_dir": str(config.paths.templates_dir),
                "html_output_dir": str(config.paths.html_output_dir),
                "images_output_dir": str(config.paths.images_output_dir),
                "event": "session_start"
            })

            # Validate configuration
            config.validate_all()

            if args.dry_run:
                logger.info("DRY RUN MODE activated - no files will be written")
                log_operation_end(logger, session_context, success=True, _log_dry_run_completed=True)
                return

            # Get database connection
            try:
                engine = await get_gcp_engine()
                logger.info("Database connection established successfully")
            except ValueError as e:
                logger.error(f"Configuration error: {e}", extra={"event": "db_config_failure"})
                log_operation_end(logger, session_context, success=False, _log_error=str(e))
                sys.exit(1)

            templates_to_generate = [args.template] if args.template else list(range(1,20))
            templates_processed = 0
            templates_failed = 0

            for template_num in templates_to_generate:
                template_context = log_operation_start(
                    logger, f"generate_template_{template_num}",
                    _log_template_num=template_num
                )

                try:
                    logger.info(f"Processing Template {template_num}", extra={
                        "template_num": template_num,
                        "event": "template_processing_start"
                    })

                    # Fetch data based on template needs
                    data = await fetch_template_data(template_num, engine)
                    if not data:
                        logger.warning(f"Skipping Template {template_num}: No data available", extra={
                            "template_num": template_num,
                            "event": "template_skipped",
                            "reason": "no_data_available"
                        })
                        log_operation_end(logger, template_context, success=True, _log_skipped=True)
                        continue

                    # Render HTML
                    output_dir = Path(args.output_dir) if args.output_dir else None
                    html_path = await render_template(template_num, data, str(output_dir) if output_dir else None)
                    if not html_path:
                        log_operation_end(logger, template_context, success=False, _log_error="render_failed")
                        templates_failed += 1
                        continue

                    # Generate image if requested
                    if not args.skip_generate:
                        await convert_to_image(html_path, template_num)

                    log_operation_end(logger, template_context, success=True)
                    templates_processed += 1

                except Exception as e:
                    log_error(logger, e, f"generate_template_{template_num}", _log_template_num=template_num)
                    log_operation_end(logger, template_context, success=False, _log_error=str(e))
                    templates_failed += 1

            # Session completion
            logger.info("Content generation completed", extra={
                "templates_processed": templates_processed,
                "templates_failed": templates_failed,
                "templates_total": len(templates_to_generate),
                "event": "session_complete"
            })

            log_operation_end(
                logger, session_context, success=True,
                _log_templates_processed=templates_processed,
                _log_templates_failed=templates_failed,
                _log_total_templates=len(templates_to_generate)
            )

        except Exception as e:
            log_error(logger, e, "content_generation_session")
            log_operation_end(logger, session_context, success=False, _log_error=str(e))
            logger.info("Content generation aborted")
            sys.exit(1)