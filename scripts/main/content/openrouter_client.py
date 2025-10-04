"""OpenRouter API client module with model selection and error handling."""

import os
import json
import requests
from typing import Dict, List, Optional

class OpenRouterClient:
    """OpenRouter API client with model selection and fallback handling."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenRouter client."""
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

        # Available models (web search model prioritized)
        self.models = {
            # Primary web search model (most cost-effective)
            'web-search': 'openai/gpt-4o-mini-search-preview',
            # Backup web search models
            'perplexity-sonar-pro': 'perplexity/sonar-pro',
            'perplexity-sonar-deep': 'perplexity/sonar-deep-research',
            # Standard models (fallback)
            'gpt-4o-mini': 'openai/gpt-4o-mini',
            'claude-haiku': 'anthropic/claude-3-haiku',
            'gemma-2-9b': 'google/gemma-2-9b-it:free',
            'llama-3.3-8b': 'meta-llama/llama-3.3-8b-instruct:free',
            'deepseek-r1': 'deepseek/deepseek-r1:free'
        }

        # Models with web search capabilities
        self.web_search_models = {
            'web-search', 'perplexity-sonar-pro', 'perplexity-sonar-deep'
        }

    def chat_completion(self,
                       prompt: str,
                       model: str = 'gpt-4o-mini',
                       max_tokens: int = 500,
                       temperature: float = 0.7,
                       system_prompt: Optional[str] = None) -> Dict:
        """
        Make a chat completion request to OpenRouter.

        Args:
            prompt: User prompt
            model: Model to use (key from self.models)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_prompt: Optional system prompt

        Returns:
            Dict with response data or error info
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'No OpenRouter API key provided',
                'content': None
            }

        # Get full model name
        model_name = self.models.get(model, self.models['gpt-4o-mini'])

        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Prepare request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'content': data["choices"][0]["message"]["content"].strip(),
                    'model_used': model_name,
                    'usage': data.get('usage', {})
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'content': None
                }

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout',
                'content': None
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Request failed: {str(e)}",
                'content': None
            }
        except (KeyError, json.JSONDecodeError) as e:
            return {
                'success': False,
                'error': f"Response parsing failed: {str(e)}",
                'content': None
            }

    def generate_with_fallback(self,
                              prompt: str,
                              preferred_models: List[str] = None,
                              use_web_search: bool = False,
                              **kwargs) -> Dict:
        """
        Generate response with model fallback.

        Args:
            prompt: User prompt
            preferred_models: List of models to try in order
            use_web_search: Whether to prioritize web search models
            **kwargs: Additional arguments for chat_completion

        Returns:
            Dict with response data
        """
        if preferred_models is None:
            if use_web_search:
                # Prioritize web search models for current information
                preferred_models = ['web-search', 'perplexity-sonar-pro', 'perplexity-sonar-deep']
            else:
                preferred_models = ['gpt-4o-mini', 'claude-haiku', 'gemma-2-9b', 'llama-3.3-8b']

        for model in preferred_models:
            if model not in self.models:
                continue

            result = self.chat_completion(prompt, model=model, **kwargs)

            if result['success']:
                web_search_indicator = "🌐" if model in self.web_search_models else "🤖"
                print(f"✅ {web_search_indicator} Generated using {model}")
                return result
            else:
                print(f"⚠️ {model} failed: {result['error']}")

        return {
            'success': False,
            'error': 'All models failed',
            'content': None
        }

    def generate_with_web_search(self,
                                prompt: str,
                                preferred_models: List[str] = None,
                                **kwargs) -> Dict:
        """
        Generate response specifically using web search enabled models.

        Args:
            prompt: User prompt
            preferred_models: List of web search models to try
            **kwargs: Additional arguments for chat_completion

        Returns:
            Dict with response data
        """
        if preferred_models is None:
            preferred_models = ['web-search', 'perplexity-sonar-pro', 'perplexity-sonar-deep']

        # Filter to only web search models
        web_search_models = [m for m in preferred_models if m in self.web_search_models]

        if not web_search_models:
            return {
                'success': False,
                'error': 'No web search models available',
                'content': None
            }

        return self.generate_with_fallback(
            prompt=prompt,
            preferred_models=web_search_models,
            use_web_search=True,
            **kwargs
        )

    def list_available_models(self) -> Dict[str, str]:
        """Get list of available models."""
        return self.models.copy()

# Factory function
def create_openrouter_client() -> OpenRouterClient:
    """Create and return an OpenRouter client."""
    return OpenRouterClient()