"""
Groq LLM Implementation

Groq provides fast inference with OpenAI-compatible API.
Uses the same OpenAI SDK but with different base URL.
Free tier available with generous rate limits.

Get your free API key at: https://console.groq.com
"""

import os
import json
from typing import Optional, List, Dict
from .base import BaseLLM

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class GroqLLM(BaseLLM):
    """Groq implementation using OpenAI-compatible API"""
    
    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    BASE_URL = "https://api.groq.com/openai/v1"
    
    AVAILABLE_MODELS = [
        {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B (Versatile)", "description": "Best quality"},
        {"id": "llama-3.1-8b-instant", "name": "Llama 3.1 8B (Instant)", "description": "Fastest"},
        {"id": "mixtral-8x7b-32768", "name": "Mixtral 8x7B", "description": "Alternative"},
        {"id": "gemma2-9b-it", "name": "Gemma 2 9B", "description": "Lightweight"},
    ]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
        max_tokens: int = 500
    ):
        """
        Initialize Groq LLM.
        
        Args:
            api_key: Groq API key (optional, uses GROQ_API_KEY env var)
            model: Model name (default: llama-3.3-70b-versatile)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
        """
        if OpenAI is None:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        super().__init__(model=model, temperature=temperature, max_tokens=max_tokens)
        
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Groq API key required. "
                "Set GROQ_API_KEY environment variable or pass api_key parameter. "
                "Get your free key at: https://console.groq.com"
            )
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.BASE_URL
        )
    
    def generate_response(self, prompt: str, context: Optional[dict] = None) -> str:
        """
        Generate response using Groq.
        
        Args:
            prompt: User input prompt
            context: Optional context with system_prompt and conversation_history
        
        Returns:
            Generated response string
        """
        messages = []
        
        if context and context.get("system_prompt"):
            messages.append({"role": "system", "content": context["system_prompt"]})
        
        if context and context.get("conversation_history"):
            messages.extend(context["conversation_history"])
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        return response.choices[0].message.content
    
    def generate_questions(
        self,
        tech_stack: list,
        position: str,
        years_experience: int,
        questions_per_tech: int = 3
    ) -> list:
        """
        Generate technical questions using Groq.
        
        Args:
            tech_stack: List of technologies to generate questions for
            position: Candidate's desired position
            years_experience: Candidate's years of experience
            questions_per_tech: Number of questions per technology
        
        Returns:
            List of question dictionaries
        """
        all_questions = []
        
        for tech in tech_stack:
            prompt = f"""You are a technical interviewer for a technology recruitment agency.

CANDIDATE PROFILE:
- Position: {position}
- Experience: {years_experience} years
- Tech Stack: {', '.join(tech_stack)}

TASK: Generate {questions_per_tech} technical interview questions for {tech}.

REQUIREMENTS:
1. Questions must be relevant to {tech}
2. Difficulty should match {years_experience} years of experience:
   - 0-2 years: Foundational concepts
   - 3-5 years: Intermediate, practical scenarios
   - 6+ years: Advanced, architecture-level
3. Mix of theoretical and practical questions
4. Questions should take 2-3 minutes to answer verbally

OUTPUT FORMAT (JSON):
{{
    "questions": [
        {{
            "technology": "{tech}",
            "question": "...",
            "difficulty": "beginner|intermediate|advanced",
            "evaluation_criteria": ["..."]
        }}
    ]
}}

Generate questions for: {tech}"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            try:
                result = json.loads(response.choices[0].message.content)
                all_questions.extend(result.get("questions", []))
            except json.JSONDecodeError:
                pass
        
        return all_questions
    
    def analyze_sentiment(self, response: str) -> dict:
        """
        Analyze sentiment using Groq.
        
        Args:
            response: Candidate's response text
        
        Returns:
            Dictionary with sentiment metrics
        """
        prompt = f"""Analyze the sentiment and confidence level in the candidate's response.

CANDIDATE RESPONSE: {response}

ANALYZE FOR:
1. Overall sentiment (positive/neutral/negative)
2. Confidence level (0.0-1.0)
3. Uncertainty indicators (specific phrases)
4. Enthusiasm level (low/medium/high)

OUTPUT FORMAT (JSON):
{{
    "sentiment": "<positive|neutral|negative>",
    "confidence_score": <float 0.0-1.0>,
    "uncertainty_phrases": ["...", "..."],
    "enthusiasm": "<low|medium|high>",
    "notes": "<brief observation for interviewer>"
}}

Be conservative - only flag genuine uncertainty signals."""
        
        result = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at analyzing text sentiment. Output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        try:
            return json.loads(result.choices[0].message.content)
        except json.JSONDecodeError:
            return {
                "sentiment": "neutral",
                "confidence_score": 0.5,
                "uncertainty_phrases": [],
                "enthusiasm": "medium",
                "notes": "Unable to analyze sentiment"
            }
    
    def get_provider_name(self) -> str:
        """Return the provider name for this LLM instance"""
        return "Groq"
    
    def get_available_models(self) -> List[Dict[str, str]]:
        """Get list of available Groq models"""
        return self.AVAILABLE_MODELS
    
    def check_availability(self) -> bool:
        """Check if the Groq API is accessible"""
        try:
            self.client.models.list()
            return True
        except Exception:
            return False
