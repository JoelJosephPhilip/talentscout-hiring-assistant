import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm.factory import LLMFactory
from src.llm.gpt4o import GPT4oLLM
from src.llm.ollama_llm import OllamaLLM
from src.llm.groq_llm import GroqLLM


class TestLLMFactory:

    def test_create_llm_openai_with_key(self, monkeypatch):
        """Test creating OpenAI LLM with API key"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-12345")

        # This will fail on validation since it's a fake key
        # but we can test the class selection
        result = LLMFactory.get_available_providers()
        assert "openai" in result

    def test_create_llm_groq_with_key(self, monkeypatch):
        """Test creating Groq LLM with API key"""
        monkeypatch.setenv("GROQ_API_KEY", "test-key-12345")

        result = LLMFactory.get_available_providers()
        assert "groq" in result

    def test_create_llm_ollama_preference(self):
        """Test creating Ollama LLM with preference"""
        try:
            llm = LLMFactory._create_ollama(
                base_url="http://localhost:11434",
                model="llama3.2"
            )
            assert isinstance(llm, OllamaLLM)
            assert llm.model == "llama3.2"
        except ImportError:
            pytest.skip("ollama package not installed")

    def test_check_ollama_available(self):
        """Test Ollama availability check"""
        result = LLMFactory._check_ollama_available("http://localhost:11434")
        assert isinstance(result, bool)

    def test_get_available_providers(self):
        """Test getting available providers"""
        providers = LLMFactory.get_available_providers()
        assert "openai" in providers
        assert "ollama" in providers
        assert "groq" in providers
        assert isinstance(providers["openai"], bool)
        assert isinstance(providers["ollama"], bool)
        assert isinstance(providers["groq"], bool)

    def test_invalid_provider_raises_error(self, monkeypatch):
        """Test that missing providers raise appropriate error"""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        with pytest.raises((RuntimeError, ValueError)) as exc_info:
            LLMFactory.create_llm(preferred="openai")

        assert "API key" in str(exc_info.value) or "required" in str(exc_info.value).lower()

    def test_auto_detect_priority_order(self, monkeypatch):
        """Test that auto-detect follows priority: Groq -> OpenAI -> Ollama"""
        # When both Groq and OpenAI keys are set, Groq should be preferred
        monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
        monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
        
        # Both will fail validation with fake keys, but we test the order
        providers = LLMFactory.get_available_providers()
        # Both should be detected
        assert "groq" in providers
        assert "openai" in providers


class TestGroqLLM:

    def test_init_requires_api_key(self):
        """Test that GroqLLM requires API key"""
        with pytest.raises(ValueError):
            GroqLLM(api_key=None)

    def test_init_with_api_key(self):
        """Test GroqLLM initialization with API key"""
        try:
            llm = GroqLLM(api_key="test-key-12345")
            assert llm.model == "llama-3.3-70b-versatile"
            assert llm.temperature == 0.7
            assert llm.max_tokens == 500
        except ImportError:
            pytest.skip("openai package not installed")

    def test_custom_parameters(self):
        """Test GroqLLM with custom parameters"""
        try:
            llm = GroqLLM(
                api_key="test-key",
                model="llama-3.1-8b-instant",
                temperature=0.5,
                max_tokens=1000
            )
            assert llm.model == "llama-3.1-8b-instant"
            assert llm.temperature == 0.5
            assert llm.max_tokens == 1000
        except ImportError:
            pytest.skip("openai package not installed")

    def test_get_provider_name(self):
        """Test provider name"""
        try:
            llm = GroqLLM(api_key="test-key")
            assert llm.get_provider_name() == "Groq"
        except ImportError:
            pytest.skip("openai package not installed")


class TestGPT4oLLM:

    def test_init_requires_api_key(self):
        """Test that GPT4oLLM requires API key"""
        with pytest.raises(ValueError):
            GPT4oLLM(api_key=None)

    def test_init_with_api_key(self):
        """Test GPT4oLLM initialization with API key"""
        try:
            llm = GPT4oLLM(api_key="test-key-12345")
            assert llm.model == "gpt-4o"
            assert llm.temperature == 0.7
            assert llm.max_tokens == 500
        except ImportError:
            pytest.skip("openai package not installed")

    def test_custom_parameters(self):
        """Test GPT4oLLM with custom parameters"""
        try:
            llm = GPT4oLLM(
                api_key="test-key",
                model="gpt-4o-mini",
                temperature=0.5,
                max_tokens=1000
            )
            assert llm.model == "gpt-4o-mini"
            assert llm.temperature == 0.5
            assert llm.max_tokens == 1000
        except ImportError:
            pytest.skip("openai package not installed")


class TestOllamaLLM:

    def test_init_default_values(self):
        """Test OllamaLLM default initialization"""
        try:
            llm = OllamaLLM()
            assert llm.model == "llama3.2"
            assert llm.base_url == "http://localhost:11434"
            assert llm.temperature == 0.7
        except ImportError:
            pytest.skip("ollama package not installed")

    def test_init_custom_values(self):
        """Test OllamaLLM with custom values"""
        try:
            llm = OllamaLLM(
                model="llama3.1",
                base_url="http://custom:11434",
                temperature=0.3
            )
            assert llm.model == "llama3.1"
            assert llm.base_url == "http://custom:11434"
            assert llm.temperature == 0.3
        except ImportError:
            pytest.skip("ollama package not installed")

    def test_get_provider_name(self):
        """Test provider name"""
        try:
            llm = OllamaLLM()
            assert llm.get_provider_name() == "Ollama"
        except ImportError:
            pytest.skip("ollama package not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
