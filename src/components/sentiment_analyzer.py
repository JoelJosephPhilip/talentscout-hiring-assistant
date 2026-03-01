from typing import Optional
from ..llm.base import BaseLLM


class SentimentAnalyzer:
    """Analyzes candidate sentiment during conversation"""

    UNCERTAINTY_PHRASES = [
        "i think", "i believe", "maybe", "perhaps", "probably",
        "i'm not sure", "i guess", "sort of", "kind of",
        "i suppose", "possibly", "might be", "could be"
    ]

    CONFIDENT_PHRASES = [
        "definitely", "absolutely", "certainly", "exactly",
        "clearly", "obviously", "without a doubt", "i know"
    ]

    def __init__(self, llm: BaseLLM):
        self.llm = llm

    def analyze(self, text: str) -> dict:
        """
        Analyze sentiment of a response.
        
        Args:
            text: Candidate's response text
        
        Returns:
            Dictionary with sentiment metrics
        """
        # Use LLM for detailed analysis
        llm_result = self._analyze_with_llm(text)
        
        # Enhance with rule-based analysis
        rule_based = self._analyze_with_rules(text)
        
        # Combine results
        return {
            "sentiment": llm_result.get("sentiment", rule_based["sentiment"]),
            "confidence_score": self._average_confidence(
                llm_result.get("confidence_score", 0.5),
                rule_based["confidence_score"]
            ),
            "uncertainty_phrases": self._extract_uncertainty_phrases(text),
            "enthusiasm": llm_result.get("enthusiasm", rule_based["enthusiasm"]),
            "notes": llm_result.get("notes", ""),
            "response_length": len(text.split()),
            "has_hedging": rule_based["has_hedging"]
        }

    def _analyze_with_llm(self, text: str) -> dict:
        """Use LLM for sentiment analysis"""
        try:
            return self.llm.analyze_sentiment(text)
        except Exception:
            return {
                "sentiment": "neutral",
                "confidence_score": 0.5,
                "uncertainty_phrases": [],
                "enthusiasm": "medium",
                "notes": ""
            }

    def _analyze_with_rules(self, text: str) -> dict:
        """Rule-based sentiment analysis"""
        text_lower = text.lower()
        words = text_lower.split()
        
        # Count indicators
        uncertainty_count = sum(1 for phrase in self.UNCERTAINTY_PHRASES if phrase in text_lower)
        confident_count = sum(1 for phrase in self.CONFIDENT_PHRASES if phrase in text_lower)
        
        # Calculate confidence score
        total_indicators = uncertainty_count + confident_count
        if total_indicators > 0:
            confidence_score = confident_count / total_indicators
        else:
            confidence_score = 0.5  # Neutral
        
        # Determine sentiment
        if confidence_score >= 0.7:
            sentiment = "positive"
        elif confidence_score >= 0.4:
            sentiment = "neutral"
        else:
            sentiment = "negative"
        
        # Determine enthusiasm based on response length and punctuation
        word_count = len(words)
        exclamation_count = text.count('!')
        
        if word_count > 50 and exclamation_count > 1:
            enthusiasm = "high"
        elif word_count < 20 or uncertainty_count > 2:
            enthusiasm = "low"
        else:
            enthusiasm = "medium"
        
        return {
            "sentiment": sentiment,
            "confidence_score": confidence_score,
            "enthusiasm": enthusiasm,
            "has_hedging": uncertainty_count > 0
        }

    def _extract_uncertainty_phrases(self, text: str) -> list:
        """Extract uncertainty phrases from text"""
        text_lower = text.lower()
        found = []
        for phrase in self.UNCERTAINTY_PHRASES:
            if phrase in text_lower:
                found.append(phrase)
        return found

    def _average_confidence(self, llm_score: float, rule_score: float) -> float:
        """Average LLM and rule-based confidence scores"""
        return round((llm_score + rule_score) / 2, 2)

    def get_overall_assessment(self, responses: list) -> dict:
        """
        Get overall sentiment assessment for multiple responses.
        
        Args:
            responses: List of response texts
        
        Returns:
            Overall sentiment metrics
        """
        if not responses:
            return {
                "overall_confidence": 0.5,
                "overall_sentiment": "neutral",
                "total_uncertainty_indicators": 0,
                "enthusiasm_trend": "unknown",
                "assessment_summary": "No responses to analyze."
            }
        
        # Analyze each response
        analyses = [self.analyze(r) for r in responses]
        
        # Calculate overall metrics
        avg_confidence = sum(a["confidence_score"] for a in analyses) / len(analyses)
        
        # Count sentiments
        sentiments = [a["sentiment"] for a in analyses]
        positive_count = sentiments.count("positive")
        negative_count = sentiments.count("negative")
        
        if positive_count > negative_count:
            overall_sentiment = "positive"
        elif negative_count > positive_count:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"
        
        # Collect all uncertainty phrases
        all_uncertainty = []
        for a in analyses:
            all_uncertainty.extend(a.get("uncertainty_phrases", []))
        
        # Determine enthusiasm trend
        enthusiasms = [a["enthusiasm"] for a in analyses]
        if enthusiasms.count("high") > len(enthusiasms) / 2:
            enthusiasm_trend = "high"
        elif enthusiasms.count("low") > len(enthusiasms) / 2:
            enthusiasm_trend = "low"
        else:
            enthusiasm_trend = "medium"
        
        # Generate summary
        if avg_confidence >= 0.7:
            summary = "Candidate demonstrates strong confidence and knowledge."
        elif avg_confidence >= 0.5:
            summary = "Candidate shows moderate confidence with some areas of uncertainty."
        else:
            summary = "Candidate displays notable uncertainty. Recommend follow-up interview."
        
        return {
            "overall_confidence": round(avg_confidence, 2),
            "overall_sentiment": overall_sentiment,
            "total_uncertainty_indicators": len(all_uncertainty),
            "uncertainty_phrases": list(set(all_uncertainty)),
            "enthusiasm_trend": enthusiasm_trend,
            "assessment_summary": summary,
            "response_count": len(responses)
        }
