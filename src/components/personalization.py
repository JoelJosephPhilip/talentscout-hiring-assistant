from typing import Optional


class PersonalizationEngine:
    """Handles personalized response generation based on candidate profile"""
    
    # Experience-based tone settings
    TONE_SETTINGS = {
        "junior": {
            "encouragement_level": "high",
            "technical_depth": "foundational",
            "formality": "friendly_casual",
            "response_style": "supportive and encouraging, use simpler language, explain concepts when needed",
            "greeting_style": "warm and welcoming, make them feel comfortable",
            "question_difficulty": "foundational concepts, practical examples"
        },
        "mid": {
            "encouragement_level": "medium",
            "technical_depth": "intermediate",
            "formality": "professional_friendly",
            "response_style": "balanced tone, professional but approachable",
            "greeting_style": "professional yet friendly",
            "question_difficulty": "intermediate scenarios, some architecture"
        },
        "senior": {
            "encouragement_level": "low",
            "technical_depth": "advanced",
            "formality": "professional",
            "response_style": "direct and professional, focus on technical depth",
            "greeting_style": "respectful and professional",
            "question_difficulty": "advanced architecture, design patterns, scalability"
        }
    }
    
    # Position-based focus areas
    POSITION_CONTEXTS = {
        "frontend": {
            "focus": "frontend development",
            "question_types": ["UI/UX", "browser rendering", "performance", "accessibility"],
            "keywords": ["frontend", "ui", "ux", "react", "vue", "angular", "css", "javascript"]
        },
        "backend": {
            "focus": "backend development",
            "question_types": ["APIs", "databases", "security", "scalability", "microservices"],
            "keywords": ["backend", "api", "server", "node", "django", "flask", "spring"]
        },
        "fullstack": {
            "focus": "full stack development",
            "question_types": ["both frontend and backend", "system design", "integration"],
            "keywords": ["full stack", "fullstack", "full-stack", "mean", "mern"]
        },
        "devops": {
            "focus": "devops and infrastructure",
            "question_types": ["CI/CD", "cloud", "monitoring", "automation", "containers"],
            "keywords": ["devops", "sre", "infrastructure", "aws", "azure", "kubernetes", "docker"]
        },
        "data": {
            "focus": "data engineering/science",
            "question_types": ["data pipelines", "ml models", "analytics", "visualization"],
            "keywords": ["data", "ml", "machine learning", "ai", "analytics", "spark", "hadoop"]
        },
        "mobile": {
            "focus": "mobile development",
            "question_types": ["mobile UI", "performance", "platform specifics", "cross-platform"],
            "keywords": ["mobile", "android", "ios", "react native", "flutter", "swift", "kotlin"]
        }
    }
    
    @staticmethod
    def get_experience_level(years: int) -> str:
        """Determine experience level category"""
        if years <= 2:
            return "junior"
        elif years <= 5:
            return "mid"
        else:
            return "senior"
    
    @staticmethod
    def get_tone_settings(years_experience: int, position: str = "") -> dict:
        """
        Get communication tone settings based on candidate profile.
        
        Args:
            years_experience: Years of professional experience
            position: Desired position (optional)
        
        Returns:
            Dictionary with tone settings
        """
        level = PersonalizationEngine.get_experience_level(years_experience)
        base_settings = PersonalizationEngine.TONE_SETTINGS[level].copy()
        
        # Add position context if available
        if position:
            position_context = PersonalizationEngine.get_position_context(position)
            base_settings["position_focus"] = position_context
        
        return base_settings
    
    @staticmethod
    def get_position_context(position: str) -> dict:
        """
        Get context based on position type.
        
        Args:
            position: Job position string
        
        Returns:
            Dictionary with position-specific settings
        """
        position_lower = position.lower()
        
        for role_type, context in PersonalizationEngine.POSITION_CONTEXTS.items():
            if any(keyword in position_lower for keyword in context["keywords"]):
                return context
        
        return {
            "focus": "general software development",
            "question_types": ["various technical areas"],
            "keywords": []
        }
    
    @staticmethod
    def personalize_prompt(base_prompt: str, candidate_info: dict, language: str = "en") -> str:
        """
        Inject personalization into prompt.
        
        Args:
            base_prompt: Original prompt template
            candidate_info: Dictionary with candidate details
            language: Current language code
        
        Returns:
            Personalized prompt
        """
        tone = PersonalizationEngine.get_tone_settings(
            candidate_info.get("years_experience", 0),
            candidate_info.get("desired_position", "")
        )
        
        name = candidate_info.get("full_name", "there")
        
        personalized_addition = f"""
PERSONALIZATION INSTRUCTIONS:
- Candidate Name: {name}
- Use their name naturally in responses (but not in every sentence)
- Experience Level: {candidate_info.get('years_experience', 0)} years ({PersonalizationEngine.get_experience_level(candidate_info.get('years_experience', 0))})
- Response Style: {tone['response_style']}
- Question Difficulty: {tone['question_difficulty']}
- Formality: {tone['formality'].replace('_', ' ')}
- Encouragement Level: {tone['encouragement_level']}
"""
        
        # Add position focus if available
        if "position_focus" in tone:
            pos_focus = tone["position_focus"]
            personalized_addition += f"""- Position Focus: {pos_focus['focus']}
- Question Types to Emphasize: {', '.join(pos_focus['question_types'])}
"""
        
        # Add language instruction if not English
        if language != "en":
            language_names = {
                "hi": "Hindi (हिंदी)",
                "es": "Spanish (Español)",
                "fr": "French (Français)",
                "de": "German (Deutsch)",
                "zh": "Chinese (中文)",
                "ml": "Malayalam (മലയാളം)"
            }
            personalized_addition += f"- Language: Respond in {language_names.get(language, language)}\n"
        
        return base_prompt + "\n" + personalized_addition
    
    @staticmethod
    def get_greeting_personalization(name: str, is_returning: bool = False, 
                                      last_visit: str = None) -> str:
        """
        Generate personalized greeting addition.
        
        Args:
            name: Candidate's name
            is_returning: Whether candidate has visited before
            last_visit: Date of last visit (if returning)
        
        Returns:
            Personalization string for greeting
        """
        if is_returning and last_visit:
            return f"Welcome back, {name}! We last saw you on {last_visit}. Great to have you here again!"
        elif name:
            return f"Make sure to greet {name} by name and make them feel welcome."
        return ""
    
    @staticmethod
    def get_question_count(years_experience: int) -> int:
        """
        Get recommended question count based on experience.
        
        Args:
            years_experience: Years of professional experience
        
        Returns:
            Recommended number of questions per technology
        """
        level = PersonalizationEngine.get_experience_level(years_experience)
        
        if level == "junior":
            return 3  # Fewer questions, more foundational
        elif level == "mid":
            return 4  # Balanced
        else:
            return 5  # More in-depth for seniors
    
    @staticmethod
    def get_encouragement_phrase(sentiment_score: float, name: str = None) -> str:
        """
        Get appropriate encouragement phrase based on sentiment.
        
        Args:
            sentiment_score: Current sentiment/confidence score
            name: Candidate's name (optional)
        
        Returns:
            Encouragement phrase
        """
        name_part = f", {name}" if name else ""
        
        if sentiment_score < 0.4:
            phrases = [
                f"Take your time{name_part}",
                f"No worries{name_part}",
                f"That's okay{name_part}",
                f"Feel free to think about it{name_part}"
            ]
        elif sentiment_score < 0.7:
            phrases = [
                f"Good answer{name_part}",
                f"Thanks for sharing{name_part}",
                f"That's helpful{name_part}",
                f"Great{name_part}"
            ]
        else:
            phrases = [
                f"Excellent answer{name_part}!",
                f"Great explanation{name_part}!",
                f"Thank you for the detailed response{name_part}!",
                f"Well said{name_part}!"
            ]
        
        import random
        return random.choice(phrases)
