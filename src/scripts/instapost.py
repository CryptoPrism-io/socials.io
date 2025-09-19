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
        btc['market_cap'] = bmp f"{btc['market_cap'] / 1e9:.1f} T" if btc['market_cap'] else 'N/A'
        btc['volume24h'] = f"{btc['volume24h'] / 1e9:.1f} B" if btc['volume24h'] else 'N/A'
        return btc
    except Exception as e:
        print(f"Error fetching Bitcoin data: {e}")
        return {}

async def render_template(template_num: int, data: Dict, output_dir: Optional[str] = None) -> Optional[str]:
    """Render HTML from template with data."""
    try:
        template_file = f"{template_num}.html"
        template = jinja_env.get_template(template_file)

        html_content = template.render(**data)

        # Use config output directory if not specified
        output_dir = Path(output_dir) if output_dir else config.paths.html_output_dir
        output_path = output_dir / f"{template_num}_output.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✓ Rendered template {template_num}: {output_path}")
        return str(output_path)

    except Exception as e:
        print(f"Error rendering template {template_num}: {e}")
        return None

async def convert_to_image(html_path: str, template_num: int):
    """Convert HTML file to Instagram-ready image."""
    image_path = str(config.paths.get_image_output_path(template_num, config.image.format))
    await generate_image_from_html(html_path, image_path)

async def main():
    """Main CLI entry point for instapost content generation."""
    parser = argparse.ArgumentParser(description='Instagram content generator for crypto socials')
    parser.add_argument('--template', '-t', type=int, choices=[1,2,3,4,5,6], default=None,
                       help='Generate specific template (1-6). If not specified, generates all.')
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

            templates_to_generate = [args.template] if args.template else [1,2,3,4,5,6]
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
                    if template_num == 6:
                        # Bitcoin snapshot template
                        btc_data = fetch_bitcoin_data(engine)
                        if not btc_data:
                            logger.warning("Skipping Template 6: No Bitcoin data available", extra={
                                "template_num": template_num,
                                "event": "template_skipped",
                                "reason": "no_bitcoin_data"
                            })
                            log_operation_end(logger, template_context, success=True, _log_skipped=True)
                            continue
                        data = {
                            'snap': [btc_data],
                            'current_date': datetime.now(config.app.timezone).strftime(config.app.datetime_format),
                            'current_time': datetime.now(config.app.timezone).strftime(config.app.time_format)
                        }
                    else:
                        # Multi-coin templates
                        coins_data = await fetch_data_top_24_coins(engine)
                        if coins_data.empty:
                            logger.warning(f"Skipping Template {template_num}: No coin data available", extra={
                                "template_num": template_num,
                                "event": "template_skipped",
                                "reason": "no_coin_data"
                            })
                            log_operation_end(logger, template_context, success=True, _log_skipped=True)
                            continue

                        # Split data for different templates (simplified logic)
                        start_idx = 0 if template_num == 1 else (24 if template_num == 2 else (48 if template_num == 3 else (72 if template_num == 4 else (96 if template_num == 5 else 0))))
                        end_idx = start_idx + 24
                        template_data = coins_data.iloc[start_idx:end_idx]

                        data = {'snap': [row.to_dict() for _, row in template_data.iterrows()]}

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