import os
from typing import Optional
from .base import BaseLLM
from .gpt4o import GPT4oLLM
from .ollama_llm import OllamaLLM
from .groq_llm import GroqLLM


class LLMFactory:
    """Factory for creating appropriate LLM instance based on availability"""
    
    @staticmethod
    def create_llm(
        preferred: str = "auto",
        groq_key: Optional[str] = None,
        openai_key: Optional[str] = None,
        ollama_base_url: str = "http://localhost:11434",
        ollama_model: str = "llama3.2",
        groq_model: str = "llama-3.3-70b-versatile"
    ) -> BaseLLM:
        """
        Create LLM instance with priority: Groq → OpenAI → Ollama
        
        Args:
            preferred: "auto", "groq", "openai", or "ollama"
            groq_key: Groq API key (optional, uses GROQ_API_KEY env var)
            openai_key: OpenAI API key (optional, uses OPENAI_API_KEY env var)
            ollama_base_url: Ollama server URL
            ollama_model: Model name for Ollama
            groq_model: Model name for Groq
        
        Returns:
            BaseLLM instance
        
        Raises:
            RuntimeError: If no LLM is available
        """
        if preferred == "groq":
            return LLMFactory._create_groq(groq_key, groq_model)
        
        if preferred == "openai":
            return LLMFactory._create_openai(openai_key)
        
        if preferred == "ollama":
            return LLMFactory._create_ollama(ollama_base_url, ollama_model)
        
        # Auto-detect mode: Groq → OpenAI → Ollama
        groq_key = groq_key or os.environ.get("GROQ_API_KEY")
        if groq_key:
            try:
                llm = GroqLLM(api_key=groq_key, model=groq_model)
                if LLMFactory._validate_groq_key(llm):
                    return llm
            except Exception:
                pass
        
        openai_key = openai_key or os.environ.get("OPENAI_API_KEY")
        if openai_key:
            try:
                llm = GPT4oLLM(api_key=openai_key)
                if LLMFactory._validate_openai_key(llm):
                    return llm
            except Exception:
                pass
        
        if LLMFactory._check_ollama_available(ollama_base_url):
            return OllamaLLM(model=ollama_model, base_url=ollama_base_url)
        
        raise RuntimeError(
            "No LLM available. Set GROQ_API_KEY or OPENAI_API_KEY environment variable, "
            "or start Ollama server with 'ollama serve'. "
            "Run setup_wizard.py for guided setup."
        )
    
    @staticmethod
    def _create_groq(api_key: Optional[str], model: str) -> GroqLLM:
        """Create Groq LLM instance"""
        api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "Groq API key required. "
                "Set GROQ_API_KEY environment variable or pass groq_key parameter. "
                "Get your free key at: https://console.groq.com"
            )
        return GroqLLM(api_key=api_key, model=model)
    
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
    def _validate_groq_key(llm: GroqLLM) -> bool:
        """Validate Groq API key by making a test call"""
        try:
            llm.client.models.list()
            return True
        except Exception:
            return False
    
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
            "groq": False,
            "openai": False,
            "ollama": False
        }
        
        # Check Groq
        groq_key = os.environ.get("GROQ_API_KEY")
        if groq_key:
            try:
                llm = GroqLLM(api_key=groq_key)
                providers["groq"] = LLMFactory._validate_groq_key(llm)
            except Exception:
                pass
        
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
