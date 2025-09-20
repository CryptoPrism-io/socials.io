"""
Dynamic Text Highlighting Utility
Automatically highlights important keywords in AI-generated market content
"""

import re

def auto_highlight_market_text(text):
    """
    Automatically highlights important market keywords in text

    Args:
        text (str): Plain text content from AI generation

    Returns:
        str: HTML text with span tags for highlighting
    """

    # Define keyword categories with their patterns and CSS classes
    keyword_categories = [
        # Price patterns - $123, $1.23K, $45M, etc.
        {
            'pattern': r'\$[\d,]+(?:\.\d+)?[KMBTkmbt]?',
            'class': 'price-highlight'
        },

        # Bullish/Positive indicators
        {
            'pattern': r'\b(strength|bullish|growth|strong|exceptional|robust|healthy|positive|gains|breakout|surge|rally|momentum|bullish)\b',
            'class': 'highlight-bullish'
        },

        # Institutional terms
        {
            'pattern': r'\b(institutional|ETF|ETFs|inflows|outflows|funds|investment|investments)\b',
            'class': 'institutional-highlight'
        },

        # Volume/Money terms (when followed by money-related context)
        {
            'pattern': r'\b\$?\d+[KMBTkmbt]?\+?\b(?=.*(?:inflow|outflow|volume|trading|liquidity))',
            'class': 'volume-highlight'
        },

        # Technical analysis terms
        {
            'pattern': r'\b(on-chain|metrics|indicators|analysis|technical|support|resistance|levels?)\b',
            'class': 'key-metric'
        },

        # Whale activity
        {
            'pattern': r'\b(whale|whales|accumulation|large\s+holders?|major\s+players?)\b',
            'class': 'whale-activity'
        },

        # Resistance/Support levels
        {
            'pattern': r'\b(psychological\s+(?:level|barrier|resistance)|resistance\s+(?:level|zone)|support\s+(?:level|zone))\b',
            'class': 'resistance-level'
        },

        # Critical points
        {
            'pattern': r'\b(critical|crucial|key|important|significant|major|inflection\s+point|turning\s+point)\b',
            'class': 'critical-point'
        },

        # Risk factors
        {
            'pattern': r'\b(options?\s+expiry|expiration|volatility|risk|uncertainty|caution)\b',
            'class': 'risk-factor'
        },

        # Market catalysts
        {
            'pattern': r'\b(catalyst|correlation|market\s+open|macro|sentiment|factors?|drivers?)\b',
            'class': 'market-catalyst'
        },

        # Network/fundamentals
        {
            'pattern': r'\b(network\s+(?:activity|growth|health)|fundamentals?|adoption|usage)\b',
            'class': 'positive-indicator'
        }
    ]

    highlighted_text = text

    # Apply highlighting for each category
    for category in keyword_categories:
        pattern = category['pattern']
        css_class = category['class']

        # Use case-insensitive matching
        highlighted_text = re.sub(
            pattern,
            lambda m: f'<span class="{css_class}">{m.group()}</span>',
            highlighted_text,
            flags=re.IGNORECASE
        )

    return highlighted_text

def wrap_in_news_structure(highlighted_text, title="AI Market Recap"):
    """
    Wraps highlighted text in the proper HTML structure for the news section

    Args:
        highlighted_text (str): Text with highlighting spans
        title (str): Section title

    Returns:
        str: Complete HTML structure for the news section
    """

    return f'''
        <!-- Bitcoin Market Recap Section -->
        <div class="bitcoin-news-section">
            <div class="news-card unified">
                <div class="news-title">{title}</div>
                <div class="news-content">
                    <div class="news-paragraph" id="market-recap-text">
                        {highlighted_text}
                    </div>
                </div>
            </div>
        </div>
    '''

# Example usage for testing
if __name__ == "__main__":
    sample_text = """
    Bitcoin demonstrates exceptional strength at $117,301 with institutional inflows
    reaching $200M+ across major ETFs. On-chain metrics reveal healthy network growth
    while whale accumulation continues. The $120,000 psychological barrier represents
    a critical inflection point. Weekly options expiry remains a key catalyst to monitor.
    """

    highlighted = auto_highlight_market_text(sample_text)
    print("Highlighted text:")
    print(highlighted)