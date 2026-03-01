from datetime import datetime
from typing import Optional, List, Dict
import json
from pathlib import Path


class UsageTracker:
    """Track LLM API usage and costs"""
    
    # Approximate costs per 1K tokens (as of 2024)
    COST_PER_1K_TOKENS = {
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "llama3.2": {"input": 0.0, "output": 0.0},  # Local model, no cost
        "ollama": {"input": 0.0, "output": 0.0}
    }
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize usage tracker.
        
        Args:
            storage_path: Path to store usage data (optional)
        """
        self.requests: List[Dict] = []
        self.total_tokens = 0
        self.total_cost = 0.0
        self.storage_path = Path(storage_path) if storage_path else None
        self.start_time = datetime.now()
    
    def log_request(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        phase: str = "unknown",
        response_time_ms: Optional[float] = None
    ):
        """
        Log an API request.
        
        Args:
            provider: LLM provider name
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            phase: Conversation phase
            response_time_ms: Response time in milliseconds
        """
        total_tokens = input_tokens + output_tokens
        
        # Calculate cost
        cost = self._calculate_cost(model, input_tokens, output_tokens)
        
        request_data = {
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "cost": cost,
            "phase": phase,
            "response_time_ms": response_time_ms
        }
        
        self.requests.append(request_data)
        self.total_tokens += total_tokens
        self.total_cost += cost
        
        # Save if storage path is set
        if self.storage_path:
            self._save_to_storage()
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a request"""
        model_key = model.lower()
        if "gpt-4o-mini" in model_key:
            rates = self.COST_PER_1K_TOKENS["gpt-4o-mini"]
        elif "gpt-4o" in model_key or "gpt-4" in model_key:
            rates = self.COST_PER_1K_TOKENS["gpt-4o"]
        else:
            rates = self.COST_PER_1K_TOKENS.get(model_key, {"input": 0, "output": 0})
        
        input_cost = (input_tokens / 1000) * rates["input"]
        output_cost = (output_tokens / 1000) * rates["output"]
        
        return round(input_cost + output_cost, 6)
    
    def get_summary(self) -> Dict:
        """
        Get usage summary.
        
        Returns:
            Dictionary with usage statistics
        """
        if not self.requests:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "input_tokens": 0,
                "output_tokens": 0,
                "requests_by_provider": {},
                "requests_by_phase": {},
                "avg_response_time_ms": 0,
                "session_duration_seconds": 0
            }
        
        # Calculate statistics
        input_tokens = sum(r["input_tokens"] for r in self.requests)
        output_tokens = sum(r["output_tokens"] for r in self.requests)
        
        # Count by provider
        by_provider = {}
        for req in self.requests:
            provider = req["provider"]
            by_provider[provider] = by_provider.get(provider, 0) + 1
        
        # Count by phase
        by_phase = {}
        for req in self.requests:
            phase = req.get("phase", "unknown")
            by_phase[phase] = by_phase.get(phase, 0) + 1
        
        # Average response time
        response_times = [r["response_time_ms"] for r in self.requests if r.get("response_time_ms")]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Session duration
        duration = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "total_requests": len(self.requests),
            "total_tokens": self.total_tokens,
            "total_cost": round(self.total_cost, 4),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "requests_by_provider": by_provider,
            "requests_by_phase": by_phase,
            "avg_response_time_ms": round(avg_response_time, 1),
            "session_duration_seconds": round(duration, 0)
        }
    
    def get_formatted_summary(self) -> str:
        """Get human-readable usage summary"""
        summary = self.get_summary()
        
        lines = [
            f"📊 **API Usage Summary**",
            f"- Total Requests: {summary['total_requests']}",
            f"- Total Tokens: {summary['total_tokens']:,}",
            f"- Input Tokens: {summary['input_tokens']:,}",
            f"- Output Tokens: {summary['output_tokens']:,}",
        ]
        
        if summary['total_cost'] > 0:
            lines.append(f"- Est. Cost: ${summary['total_cost']:.4f}")
        
        if summary['avg_response_time_ms'] > 0:
            lines.append(f"- Avg Response Time: {summary['avg_response_time_ms']:.0f}ms")
        
        return "\n".join(lines)
    
    def _save_to_storage(self):
        """Save usage data to storage"""
        if not self.storage_path:
            return
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "requests": self.requests,
            "summary": self.get_summary()
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def reset(self):
        """Reset all tracking data"""
        self.requests = []
        self.total_tokens = 0
        self.total_cost = 0.0
        self.start_time = datetime.now()


class TokenCounter:
    """Helper class to estimate token counts"""
    
    # Approximate characters per token (varies by language)
    CHARS_PER_TOKEN = {
        "en": 4,  # English
        "hi": 3,  # Hindi (more tokens for Devanagari)
        "es": 4,
        "fr": 4,
        "de": 4,
        "zh": 2,  # Chinese (fewer chars per token)
        "ml": 3   # Malayalam
    }
    
    @staticmethod
    def estimate_tokens(text: str, language: str = "en") -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Text to estimate
            language: Language code
        
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        
        chars_per_token = TokenCounter.CHARS_PER_TOKEN.get(language, 4)
        return max(1, len(text) // chars_per_token)
    
    @staticmethod
    def estimate_messages_tokens(messages: List[Dict], language: str = "en") -> int:
        """
        Estimate total tokens for a list of messages.
        
        Args:
            messages: List of message dictionaries with 'content' key
            language: Language code
        
        Returns:
            Estimated total token count
        """
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            total += TokenCounter.estimate_tokens(content, language)
            # Add overhead for role, formatting
            total += 4
        return total
