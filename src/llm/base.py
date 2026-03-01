from abc import ABC, abstractmethod
from typing import Optional


class BaseLLM(ABC):
    """Abstract base class for LLM integrations"""

    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 500):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    def generate_response(self, prompt: str, context: Optional[dict] = None) -> str:
        """
        Generate a response given prompt and context.
        
        Args:
            prompt: The user input prompt
            context: Optional context including system_prompt, conversation_history, etc.
        
        Returns:
            Generated response string
        """
        pass

    @abstractmethod
    def generate_questions(self, tech_stack: list, position: str, 
                          years_experience: int, questions_per_tech: int = 3) -> list:
        """
        Generate technical questions for given tech stack.
        
        Args:
            tech_stack: List of technologies to generate questions for
            position: Candidate's desired position
            years_experience: Candidate's years of experience
            questions_per_tech: Number of questions to generate per technology
        
        Returns:
            List of question dictionaries with 'technology', 'question', 'difficulty'
        """
        pass

    @abstractmethod
    def analyze_sentiment(self, response: str) -> dict:
        """
        Analyze sentiment of candidate response.
        
        Args:
            response: Candidate's response text
        
        Returns:
            Dictionary with sentiment metrics
        """
        pass

    def get_provider_name(self) -> str:
        """Return the provider name for this LLM instance"""
        return self.__class__.__name__.replace("LLM", "")
