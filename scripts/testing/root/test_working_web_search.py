"""Test the actual working web search models for Bitcoin updates."""

import os
import sys
import json

# Add main directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'main'))

from content.openrouter_client import create_openrouter_client

def test_working_web_search():
    """Test the models that actually work for web search."""
    print("🌐 Testing Working Web Search Models for Bitcoin")
    print("=" * 60)

    client = create_openrouter_client()

    # Update the working models list
    working_models = [
        'perplexity/sonar-pro',
        'perplexity/sonar-reasoning-pro',
        'perplexity/sonar-deep-research',
        'perplexity/sonar',
        'openai/gpt-4o-search-preview',
        'openai/gpt-4o-mini-search-preview'
    ]

    bitcoin_prompt = """Search for current Bitcoin information and return ONLY a JSON response:

{
  "past_24h": ["Bitcoin event 1", "Bitcoin event 2", "Bitcoin event 3"],
  "next_24h": ["Thing to watch 1", "Thing to watch 2", "Thing to watch 3"]
}

Use real current data. Keep each item under 60 characters."""

    for model in working_models:
        print(f"\n🔬 Testing: {model}")
        print("-" * 40)

        try:
            # Test directly with the OpenRouter client
            result = client.chat_completion(
                prompt=bitcoin_prompt,
                model=model.split('/')[-1] if '/' in model else model,  # Extract model key
                max_tokens=300,
                temperature=0.1
            )

            if result['success']:
                content = result['content']
                print(f"✅ Success! Length: {len(content)}")

                if content.strip():
                    print(f"📝 Raw response:")
                    print(f"'{content}'")

                    # Try to parse JSON
                    if '{' in content and '}' in content:
                        try:
                            start = content.find('{')
                            end = content.rfind('}') + 1
                            json_part = content[start:end]
                            parsed = json.loads(json_part)

                            print(f"✅ JSON parsed successfully!")
                            print(f"📅 Past 24h: {parsed.get('past_24h', 'Not found')}")
                            print(f"🔮 Next 24h: {parsed.get('next_24h', 'Not found')}")

                        except json.JSONDecodeError as e:
                            print(f"❌ JSON parsing failed: {e}")
                    else:
                        print(f"⚠️ No JSON found in response")
                else:
                    print("⚠️ Empty response")
            else:
                print(f"❌ Failed: {result['error']}")

        except Exception as e:
            print(f"💥 Exception: {e}")

    # Test a simple direct request to the best working model
    print(f"\n" + "=" * 60)
    print("🎯 Direct Test with Best Model")
    print("-" * 40)

    simple_prompt = "What is Bitcoin's price right now? Give me one sentence."

    test_models = ['perplexity/sonar-pro', 'openai/gpt-4o-mini-search-preview']

    for model in test_models:
        print(f"\n🔍 Testing {model} with simple prompt:")

        try:
            import requests

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": simple_prompt}],
                    "max_tokens": 100
                },
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                print(f"✅ Success: {content}")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"💥 Exception: {e}")

    print(f"\n🎉 Working Web Search Test Complete!")

if __name__ == "__main__":
    test_working_web_search()