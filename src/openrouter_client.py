"""
OpenRouter API Client
Handles communication with OpenRouter for LLM and Vision capabilities
"""

import os
import httpx
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class OpenRouterClient:
    """Client for interacting with OpenRouter API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.app_name = os.getenv("OPENROUTER_APP_NAME", "HB-Pattern-Chatbot")
        self.site_url = os.getenv("OPENROUTER_SITE_URL", "http://localhost:8000")
        self.base_url = "https://openrouter.ai/api/v1"
        
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found in environment variables. "
                "Please add it to your .env file."
            )
        
        # Default models
        self.default_chat_model = "meta-llama/llama-3.1-8b-instruct"
        self.default_vision_model = "openai/gpt-4-vision-preview"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for OpenRouter API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": self.site_url,
            "X-Title": self.app_name,
            "Content-Type": "application/json"
        }
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Send chat completion request to OpenRouter
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to Llama 3.1)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            AI response text
        """
        if model is None:
            model = self.default_chat_model
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Extract message from response
                return data["choices"][0]["message"]["content"]
                
            except httpx.HTTPStatusError as e:
                error_detail = e.response.json() if e.response.text else str(e)
                raise Exception(f"OpenRouter API error: {error_detail}")
            except Exception as e:
                raise Exception(f"Request failed: {str(e)}")
    
    async def analyze_image(
        self,
        image_base64: str,
        prompt: str,
        model: Optional[str] = None
    ) -> str:
        """
        Analyze image using Vision API
        
        Args:
            image_base64: Base64 encoded image
            prompt: Analysis prompt
            model: Vision model to use (defaults to GPT-4V)
            
        Returns:
            Image analysis text
        """
        if model is None:
            model = self.default_vision_model
        
        # Construct message with image
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 500
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:  # Longer timeout for vision
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload
                )
                
                response.raise_for_status()
                data = response.json()
                
                return data["choices"][0]["message"]["content"]
                
            except httpx.HTTPStatusError as e:
                error_detail = e.response.json() if e.response.text else str(e)
                raise Exception(f"OpenRouter Vision API error: {error_detail}")
            except Exception as e:
                raise Exception(f"Vision request failed: {str(e)}")
    
    async def test_connection(self) -> bool:
        """
        Test connection to OpenRouter API
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_messages = [
                {"role": "user", "content": "Hello, testing connection."}
            ]
            
            response = await self.chat_completion(
                messages=test_messages,
                max_tokens=10
            )
            
            return bool(response)
            
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


# Test function
async def test_client():
    """Test the OpenRouter client"""
    client = OpenRouterClient()
    
    print("Testing OpenRouter connection...")
    
    # Test 1: Simple chat
    try:
        response = await client.chat_completion(
            messages=[
                {"role": "user", "content": "What is HbE disease? Answer in one sentence."}
            ],
            max_tokens=100
        )
        print(f"✅ Chat test passed: {response[:100]}...")
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
    
    # Test 2: Connection test
    try:
        connected = await client.test_connection()
        print(f"✅ Connection test: {'Passed' if connected else 'Failed'}")
    except Exception as e:
        print(f"❌ Connection test failed: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_client())

