from enum import Enum
from typing import Tuple
import re


class FallbackType(Enum):
    NONE = "none"
    OFF_TOPIC = "off_topic"
    INCOMPLETE = "incomplete"
    INVALID_FORMAT = "invalid"
    UNCLEAR = "unclear"
    HOSTILE = "hostile"
    EXIT = "exit"
    QUESTION = "question"


class FallbackHandler:
    """Handles unexpected user inputs with graceful fallbacks"""

    EXIT_KEYWORDS = [
        "bye", "goodbye", "quit", "exit", "stop", "end",
        "no thanks", "not interested", "nevermind", "cancel",
        "no thank you", "not now", "maybe later"
    ]

    HOSTILE_KEYWORDS = [
        "stupid", "idiot", "useless", "hate", "waste of time",
        "terrible", "awful", "worst"
    ]

    def __init__(self):
        pass

    def classify_input(
        self,
        user_input: str,
        expected_type: str,
        current_phase: str
    ) -> Tuple[FallbackType, str]:
        """
        Classify user input and determine fallback type.
        
        Args:
            user_input: The user's message
            expected_type: Expected input type (email, phone, etc.)
            current_phase: Current conversation phase
        
        Returns:
            Tuple of (fallback_type, response_message)
        """
        user_lower = user_input.lower().strip()

        # Check for exit keywords - use exact match for short inputs
        if len(user_lower) <= 5:
            # For very short inputs, check exact match
            exact_exit_words = ["bye", "quit", "exit", "stop", "end", "cancel"]
            if user_lower in exact_exit_words:
                return FallbackType.EXIT, self._generate_exit_response()
        else:
            # For longer inputs, check if exit phrase is contained
            exit_phrases = ["goodbye", "no thanks", "not interested", "nevermind", 
                           "no thank you", "not now", "maybe later"]
            if any(phrase in user_lower for phrase in exit_phrases):
                return FallbackType.EXIT, self._generate_exit_response()

        # Check for hostile content
        if any(keyword in user_lower for keyword in self.HOSTILE_KEYWORDS):
            return FallbackType.HOSTILE, self._generate_hostile_response()

        # Check if user is asking a question
        if user_input.strip().endswith('?'):
            return FallbackType.QUESTION, self._handle_question(user_input, current_phase)

        # Validate based on expected type
        validation_result = self._validate_input(user_input, expected_type)

        if validation_result == "valid":
            return FallbackType.NONE, ""
        elif validation_result == "incomplete":
            return FallbackType.INCOMPLETE, self._generate_incomplete_response(expected_type)
        else:
            return FallbackType.INVALID_FORMAT, self._generate_invalid_response(expected_type)

    def _validate_input(self, user_input: str, expected_type: str) -> str:
        """Validate input against expected type"""
        validators = {
            "full_name": self._validate_name,
            "email": self._validate_email,
            "phone": self._validate_phone,
            "years_experience": self._validate_experience,
            "desired_position": self._validate_position,
            "location": self._validate_location,
            "tech_stack": self._validate_tech_stack,
            "technical_response": self._validate_technical_response
        }

        validator = validators.get(expected_type, lambda x: "valid")
        return validator(user_input)

    def _validate_name(self, name: str) -> str:
        if len(name.strip()) < 2:
            return "incomplete"
        if not name.replace(' ', '').replace('-', '').replace("'", '').isalpha():
            return "invalid"
        return "valid"

    def _validate_email(self, email: str) -> str:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if '@' not in email:
            return "incomplete"
        if not re.match(pattern, email):
            return "invalid"
        return "valid"

    def _validate_phone(self, phone: str) -> str:
        cleaned = re.sub(r'[^0-9+]', '', phone)
        if len(cleaned) < 7:
            return "incomplete"
        if len(cleaned) > 15:
            return "invalid"
        return "valid"

    def _validate_experience(self, exp: str) -> str:
        try:
            years = int(exp.strip())
            if years < 0:
                return "invalid"
            if years > 50:
                return "invalid"
            return "valid"
        except ValueError:
            return "invalid"

    def _validate_position(self, position: str) -> str:
        if len(position.strip()) < 2:
            return "incomplete"
        return "valid"

    def _validate_location(self, location: str) -> str:
        if len(location.strip()) < 2:
            return "incomplete"
        return "valid"

    def _validate_tech_stack(self, tech_stack: str) -> str:
        technologies = [t.strip() for t in re.split(r'[,，\s]+', tech_stack) if t.strip()]
        if len(technologies) < 1:
            return "incomplete"
        return "valid"

    def _validate_technical_response(self, response: str) -> str:
        if len(response.strip()) < 10:
            return "incomplete"
        return "valid"

    def _generate_exit_response(self) -> str:
        return "I understand. Thank you for your time! Feel free to return whenever you're ready to continue your application."

    def _generate_hostile_response(self) -> str:
        return "I'm here to help with your application. Let's keep our conversation professional. Would you like to continue with the screening?"

    def _handle_question(self, question: str, phase: str) -> str:
        return "I appreciate your question! I'll do my best to answer briefly, but my main focus is helping with your screening. Let me address that and then we can continue."

    def _generate_incomplete_response(self, expected_type: str) -> str:
        messages = {
            "full_name": "Could you please provide your full name?",
            "email": "It looks like your email might be incomplete. Could you double-check it?",
            "phone": "Could you provide your complete phone number?",
            "years_experience": "Could you specify how many years of experience you have?",
            "desired_position": "What position are you applying for?",
            "location": "Where are you currently located?",
            "tech_stack": "Could you tell me which technologies you're proficient in?",
            "technical_response": "Could you elaborate a bit more on your answer?"
        }
        return messages.get(expected_type, "Could you provide more details?")

    def _generate_invalid_response(self, expected_type: str) -> str:
        messages = {
            "email": "That doesn't look like a valid email address. Please use a format like 'name@example.com'.",
            "phone": "Please provide a valid phone number (e.g., +1-555-123-4567).",
            "years_experience": "Please enter a number between 0 and 50 for years of experience.",
            "full_name": "Names should only contain letters, spaces, and hyphens. Could you re-enter your name?"
        }
        return messages.get(expected_type, "That doesn't seem right. Could you try again?")
