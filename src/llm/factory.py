import os
from typing import Optional
from .base import BaseLLM
from .gpt4o import GPT4oLLM
from .ollama_llm import OllamaLLM


class LLMFactory:
    """Factory for creating appropriate LLM instance based on availability"""

    @staticmethod
    def create_llm(
        preferred: str = "auto",
        openai_key: Optional[str] = None,
        ollama_base_url: str = "http://localhost:11434",
        ollama_model: str = "llama3.2"
    ) -> BaseLLM:
        """
        Create LLM instance with priority:
        1. Manual override if preferred != "auto"
        2. GPT-4o if OPENAI_API_KEY is valid
        3. Ollama/Llama if server is running locally
        4. Raise error if no LLM available
        
        Args:
            preferred: "auto", "openai", or "ollama"
            openai_key: OpenAI API key (optional, uses env var if not provided)
            ollama_base_url: Ollama server URL
            ollama_model: Model name for Ollama
        
        Returns:
            BaseLLM instance
        
        Raises:
            RuntimeError: If no LLM is available
        """
        if preferred == "openai":
            return LLMFactory._create_openai(openai_key)
        
        if preferred == "ollama":
            return LLMFactory._create_ollama(ollama_base_url, ollama_model)
        
        # Auto-detect mode
        openai_key = openai_key or os.environ.get("OPENAI_API_KEY")
        
        # Try OpenAI first
        if openai_key:
            try:
                llm = GPT4oLLM(api_key=openai_key)
                if LLMFactory._validate_openai_key(llm):
                    return llm
            except Exception:
                pass
        
        # Fall back to Ollama
        if LLMFactory._check_ollama_available(ollama_base_url):
            return OllamaLLM(model=ollama_model, base_url=ollama_base_url)
        
        raise RuntimeError(
            "No LLM available. Set OPENAI_API_KEY environment variable "
            "or start Ollama server with 'ollama serve'."
        )

    @staticmethod
    def _create_openai(api_key: Optional[str]) -> GPT4oLLM:
        """Create GPT-4o LLM instance"""
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required for OpenAI provider")
        return GPT4oLLM(api_key=api_key)

    @staticmethod
    def _create_ollama(base_url: str, model: str) -> OllamaLLM:
        """Create Ollama LLM instance"""
        return OllamaLLM(model=model, base_url=base_url)

    @staticmethod
    def _validate_openai_key(llm: GPT4oLLM) -> bool:
        """Validate OpenAI API key by making a test call"""
        try:
            llm.client.models.list()
            return True
        except Exception:
            return False

    @staticmethod
    def _check_ollama_available(base_url: str) -> bool:
        """Check if Ollama server is running"""
        try:
            import requests
            response = requests.get(f"{base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    @staticmethod
    def get_available_providers() -> dict:
        """
        Check which providers are available.
        
        Returns:
            Dictionary with provider availability status
        """
        providers = {
            "openai": False,
            "ollama": False
        }
        
        # Check OpenAI
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            try:
                llm = GPT4oLLM(api_key=openai_key)
                providers["openai"] = LLMFactory._validate_openai_key(llm)
            except Exception:
                pass
        
        # Check Ollama
        ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        providers["ollama"] = LLMFactory._check_ollama_available(ollama_url)
        
        return providers
