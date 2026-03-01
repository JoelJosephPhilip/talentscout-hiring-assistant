import os
import json
from typing import Optional
from .base import BaseLLM

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class GPT4oLLM(BaseLLM):
    """GPT-4o implementation using OpenAI API"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o",
                 temperature: float = 0.7, max_tokens: int = 500):
        if OpenAI is None:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        super().__init__(model=model, temperature=temperature, max_tokens=max_tokens)
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)

    def generate_response(self, prompt: str, context: Optional[dict] = None) -> str:
        """Generate response using GPT-4o"""
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

    def generate_questions(self, tech_stack: list, position: str,
                          years_experience: int, questions_per_tech: int = 3) -> list:
        """Generate technical questions using GPT-4o"""
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
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            all_questions.extend(result.get("questions", []))
        
        return all_questions

    def analyze_sentiment(self, response: str) -> dict:
        """Analyze sentiment using GPT-4o"""
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
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        return json.loads(result.choices[0].message.content)
