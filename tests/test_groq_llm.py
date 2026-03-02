"""
Tests for GroqLLM implementation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os

from src.llm.groq_llm import GroqLLM


class TestGroqLLM:
    """Tests for GroqLLM class"""

    def test_init_with_api_key(self):
        """Test initialization with API key"""
        with patch("src.llm.groq_llm.OpenAI") as mock_openai:
            llm = GroqLLM(api_key="test_api_key")
            assert llm.model == "llama-3.3-70b-versatile"
            assert llm.api_key == "test_api_key"
            mock_openai.assert_called_once()

    def test_init_without_api_key_raises_error(self):
        """Test initialization without API key raises ValueError"""
        with patch.dict(os.environ, {}, clear=True):
            with patch("src.llm.groq_llm.OpenAI"):
                with pytest.raises(ValueError, match="Groq API key required"):
                    GroqLLM(api_key=None)

    def test_custom_model(self):
        """Test initialization with custom model"""
        with patch("src.llm.groq_llm.OpenAI"):
            llm = GroqLLM(api_key="test_key", model="llama-3.1-8b-instant")
            assert llm.model == "llama-3.1-8b-instant"

    def test_custom_temperature(self):
        """Test initialization with custom temperature"""
        with patch("src.llm.groq_llm.OpenAI"):
            llm = GroqLLM(api_key="test_key", temperature=0.5)
            assert llm.temperature == 0.5

    def test_custom_max_tokens(self):
        """Test initialization with custom max_tokens"""
        with patch("src.llm.groq_llm.OpenAI"):
            llm = GroqLLM(api_key="test_key", max_tokens=1000)
            assert llm.max_tokens == 1000

    def test_uses_env_var_api_key(self):
        """Test that GROQ_API_KEY environment variable is used"""
        with patch.dict(os.environ, {"GROQ_API_KEY": "env_key"}):
            with patch("src.llm.groq_llm.OpenAI") as mock_openai:
                llm = GroqLLM()
                assert llm.api_key == "env_key"

    @patch("src.llm.groq_llm.OpenAI")
    def test_generate_response(self, mock_openai):
        """Test response generation"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        llm = GroqLLM(api_key="test_key")
        result = llm.generate_response("Hello")
        
        assert result == "Test response"
        mock_client.chat.completions.create.assert_called_once()

    @patch("src.llm.groq_llm.OpenAI")
    def test_generate_response_with_context(self, mock_openai):
        """Test response generation with context"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Response with context"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        llm = GroqLLM(api_key="test_key")
        context = {
            "system_prompt": "You are a helpful assistant",
            "conversation_history": [{"role": "user", "content": "Hi"}]
        }
        result = llm.generate_response("Hello", context=context)
        
        assert result == "Response with context"

    @patch("src.llm.groq_llm.OpenAI")
    def test_generate_questions(self, mock_openai):
        """Test question generation"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        import json
        questions_data = {
            "questions": [
                {
                    "technology": "Python",
                    "question": "What is a decorator?",
                    "difficulty": "intermediate",
                    "evaluation_criteria": ["Understands functions", "Knows @ syntax"]
                }
            ]
        }
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=json.dumps(questions_data)))]
        mock_client.chat.completions.create.return_value = mock_response
        
        llm = GroqLLM(api_key="test_key")
        result = llm.generate_questions(
            tech_stack=["Python"],
            position="Developer",
            years_experience=3
        )
        
        assert len(result) == 1
        assert result[0]["technology"] == "Python"

    @patch("src.llm.groq_llm.OpenAI")
    def test_analyze_sentiment(self, mock_openai):
        """Test sentiment analysis"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        import json
        sentiment_data = {
            "sentiment": "positive",
            "confidence_score": 0.85,
            "uncertainty_phrases": [],
            "enthusiasm": "high",
            "notes": "Confident response"
        }
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=json.dumps(sentiment_data)))]
        mock_client.chat.completions.create.return_value = mock_response
        
        llm = GroqLLM(api_key="test_key")
        result = llm.analyze_sentiment("I am very confident in my skills")
        
        assert result["sentiment"] == "positive"
        assert result["confidence_score"] == 0.85

    @patch("src.llm.groq_llm.OpenAI")
    def test_analyze_sentiment_json_error(self, mock_openai):
        """Test sentiment analysis handles JSON errors gracefully"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Invalid JSON"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        llm = GroqLLM(api_key="test_key")
        result = llm.analyze_sentiment("Test response")
        
        assert result["sentiment"] == "neutral"
        assert result["confidence_score"] == 0.5

    def test_get_provider_name(self):
        """Test provider name returns correct value"""
        with patch("src.llm.groq_llm.OpenAI"):
            llm = GroqLLM(api_key="test_key")
            assert llm.get_provider_name() == "Groq"

    def test_get_available_models(self):
        """Test available models list"""
        with patch("src.llm.groq_llm.OpenAI"):
            llm = GroqLLM(api_key="test_key")
            models = llm.get_available_models()
            
            assert len(models) == 4
            assert models[0]["id"] == "llama-3.3-70b-versatile"

    @patch("src.llm.groq_llm.OpenAI")
    def test_check_availability_success(self, mock_openai):
        """Test availability check when API is accessible"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.models.list.return_value = []
        
        llm = GroqLLM(api_key="test_key")
        assert llm.check_availability() == True

    @patch("src.llm.groq_llm.OpenAI")
    def test_check_availability_failure(self, mock_openai):
        """Test availability check when API is not accessible"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.models.list.side_effect = Exception("API Error")
        
        llm = GroqLLM(api_key="test_key")
        assert llm.check_availability() == False

    def test_import_error_without_openai(self):
        """Test that ImportError is raised when openai is not installed"""
        with patch.dict("sys.modules", {"openai": None}):
            with patch("src.llm.groq_llm.OpenAI", None):
                with pytest.raises(ImportError, match="openai package not installed"):
                    GroqLLM(api_key="test_key")
