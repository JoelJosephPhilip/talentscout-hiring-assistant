import os
import json
from typing import Optional
from .base import BaseLLM

try:
    import ollama
except ImportError:
    ollama = None


class OllamaLLM(BaseLLM):
    """Ollama/Llama implementation for local inference"""

    def __init__(self, model: str = "llama3.2", base_url: Optional[str] = None,
                 temperature: float = 0.7, max_tokens: int = 500):
        if ollama is None:
            raise ImportError("ollama package not installed. Run: pip install ollama")
        
        super().__init__(model=model, temperature=temperature, max_tokens=max_tokens)
        self.base_url = base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.client = ollama.Client(host=self.base_url)

    def generate_response(self, prompt: str, context: Optional[dict] = None) -> str:
        """Generate response using local Ollama model"""
        messages = []
        
        if context and context.get("system_prompt"):
            messages.append({"role": "system", "content": context["system_prompt"]})
        
        if context and context.get("conversation_history"):
            messages.extend(context["conversation_history"])
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat(
            model=self.model,
            messages=messages,
            options={
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        )
        
        return response["message"]["content"]

    def generate_questions(self, tech_stack: list, position: str,
                          years_experience: int, questions_per_tech: int = 3) -> list:
        """Generate technical questions using local model"""
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
2. Difficulty should match {years_experience} years of experience
3. Mix of theoretical and practical questions

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

            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                format="json"
            )
            
            result = json.loads(response["message"]["content"])
            all_questions.extend(result.get("questions", []))
        
        return all_questions

    def analyze_sentiment(self, response: str) -> dict:
        """Analyze sentiment using local model"""
        prompt = f"""Analyze the sentiment and confidence level in the candidate's response.

CANDIDATE RESPONSE: {response}

OUTPUT FORMAT (JSON):
{{
    "sentiment": "<positive|neutral|negative>",
    "confidence_score": <float 0.0-1.0>,
    "uncertainty_phrases": ["..."],
    "enthusiasm": "<low|medium|high>",
    "notes": "<brief observation>"
}}"""

        result = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at analyzing text sentiment. Output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            format="json"
        )
        
        return json.loads(result["message"]["content"])

    def check_availability(self) -> bool:
        """Check if the Ollama server is available and model is pulled"""
        try:
            models = self.client.list()
            return any(self.model in m.get("model", "") for m in models.get("models", []))
        except Exception:
            return False
