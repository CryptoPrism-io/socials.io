import imgkit

def generate_html_for_image(coin_data):
    """
    Generates HTML for displaying coin data, which can then be converted into an image using imgkit.

    Args:
        coin_data: A dictionary containing coin data (e.g., {'name': 'BTC', 'price': 99956.82, 'percentage_change': -0.31, 'market_cap': '1.98 T'})
    """
    
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Top Coins Display</title>
    <style>
        .TopCoins1 {
            width: 690px;
            height: 200px;
            padding: 24px 6px 24px 7px;
            background: rgba(0, 0, 0, 0.88);
            box-shadow: 0px 6.62px 6.62px rgba(0, 0, 0, 0.25);
            border-radius: 41.37px;
            border: 1.65px #92ffff solid;
            backdrop-filter: blur(19.86px);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .LogoSymbolPrice {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
        }

        .Logo {
            width: 128px;
            height: 128px;
        }

        .SymbolPercentage {
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: center;
            gap: 10px;
        }

        .Symbol {
            text-align: center;
            color: white;
            font-size: 64px;
            text-transform: capitalize;
            line-height: 30px;
            letter-spacing: 7.68px;
            word-wrap: break-word;
        }

        .Pct1dColour {
            text-align: center;
            color: #ff726d;
            font-size: 52px;
            font-weight: 500;
            text-transform: capitalize;
            line-height: 20px;
            word-wrap: break-word;
        }

        .PriceMcap {
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: flex-end;
            gap: 10px;
        }

        .PriceUsd {
            height: 70px;
            text-align: right;
            color: #c7c7c7;
            font-size: 56px;
            text-transform: capitalize;
            line-height: 20px;
            word-wrap: break-word;
        }

        .McapUnits {
            height: 52px;
            text-align: right;
            color: rgba(255, 255, 255, 0.67);
            font-size: 44px;
            text-transform: capitalize;
            line-height: 20px;
            letter-spacing: 2.2px;
            word-wrap: break-word;
        }
    </style>
</head>
<body>
    <div class="TopCoins1">
        <div class="LogoSymbolPrice">
            <img class="Logo" src="https://via.placeholder.com/128x128" />
            <div class="SymbolPercentage">
                <div class="Symbol">{symbol}</div>
                <div class="Pct1dColour">{percentage_change}%</div>
            </div>
        </div>
        <div class="PriceMcap">
            <div class="PriceUsd">{price}</div>
            <div class="McapUnits">{market_cap}</div>
        </div>
    </div>
</body>
</html>
    """

    # Construct HTML content with coin data
    html_content = html_template.format(
        symbol=coin_data['name'],
        price=coin_data['price'],
        percentage_change=coin_data['percentage_change'],
        market_cap=coin_data['market_cap'],
    )

    return html_content


# Example coin data
coin_data = {
    'name': 'BTC',
    'price': '$99956.82',
    'percentage_change': '-0.31',
    'market_cap': '$1.98 T'
}

# Generate the HTML string
html_for_image = generate_html_for_image(coin_data)

# Use imgkit to generate the image from the HTML string
config = imgkit.config(wkhtmltoimage='/path/to/wkhtmltoimage')  # Replace with the actual path if needed

imgkit.from_string(html_for_image, 'aligned.jpg', config=config)

print("Image created successfully.")
