import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.components.fallback_handler import FallbackHandler, FallbackType


class TestFallbackHandler:
    
    @pytest.fixture
    def handler(self):
        return FallbackHandler()
    
    # === Exit Keywords Tests ===
    @pytest.mark.parametrize("input_text", [
        "bye",
        "Goodbye!",
        "quit",
        "I want to exit",
        "stop this",
        "No thanks, bye",
        "cancel"
    ])
    def test_exit_keywords_detected(self, handler, input_text):
        fallback_type, _ = handler.classify_input(input_text, "email", "info_gathering")
        assert fallback_type == FallbackType.EXIT
    
    # === Hostile Content Tests ===
    @pytest.mark.parametrize("input_text", [
        "This is stupid",
        "You're an idiot",
        "What a waste of time",
        "This is terrible",
        "I hate this"
    ])
    def test_hostile_detection(self, handler, input_text):
        fallback_type, _ = handler.classify_input(input_text, "email", "info_gathering")
        assert fallback_type == FallbackType.HOSTILE
    
    # === Email Validation Tests ===
    @pytest.mark.parametrize("email,expected", [
        ("valid@email.com", FallbackType.NONE),
        ("invalid-email", FallbackType.INCOMPLETE),  # No @ sign = incomplete
        ("missing@domain", FallbackType.INVALID_FORMAT),
        ("@nodomain.com", FallbackType.INVALID_FORMAT),
        ("valid+alias@email.co.uk", FallbackType.NONE),
        ("test.user@example.org", FallbackType.NONE),
    ])
    def test_email_validation(self, handler, email, expected):
        fallback_type, _ = handler.classify_input(email, "email", "info_gathering")
        assert fallback_type == expected
    
    # === Phone Validation Tests ===
    @pytest.mark.parametrize("phone,expected", [
        ("+1-555-123-4567", FallbackType.NONE),
        ("5551234567", FallbackType.NONE),
        ("+44 20 1234 5678", FallbackType.NONE),
        ("123", FallbackType.INCOMPLETE),
        ("a", FallbackType.INCOMPLETE),
    ])
    def test_phone_validation(self, handler, phone, expected):
        fallback_type, _ = handler.classify_input(phone, "phone", "info_gathering")
        assert fallback_type == expected
    
    # === Experience Validation Tests ===
    @pytest.mark.parametrize("exp,expected", [
        ("5", FallbackType.NONE),
        ("0", FallbackType.NONE),
        ("25", FallbackType.NONE),
        ("-5", FallbackType.INVALID_FORMAT),
        ("100", FallbackType.INVALID_FORMAT),
        ("five", FallbackType.INVALID_FORMAT),
    ])
    def test_experience_validation(self, handler, exp, expected):
        fallback_type, _ = handler.classify_input(exp, "years_experience", "info_gathering")
        assert fallback_type == expected
    
    # === Name Validation Tests ===
    @pytest.mark.parametrize("name,expected", [
        ("John Doe", FallbackType.NONE),
        ("Jane", FallbackType.NONE),
        ("Mary-Jane", FallbackType.NONE),
        ("O'Brien", FallbackType.NONE),
        ("J", FallbackType.INCOMPLETE),
        ("", FallbackType.INCOMPLETE),
        ("123John", FallbackType.INVALID_FORMAT),
    ])
    def test_name_validation(self, handler, name, expected):
        fallback_type, _ = handler.classify_input(name, "full_name", "info_gathering")
        assert fallback_type == expected
    
    # === Tech Stack Validation Tests ===
    @pytest.mark.parametrize("tech,expected", [
        ("Python", FallbackType.NONE),
        ("Python, Django, React", FallbackType.NONE),
        ("Python Django PostgreSQL", FallbackType.NONE),
        ("", FallbackType.INCOMPLETE),
    ])
    def test_tech_stack_validation(self, handler, tech, expected):
        fallback_type, _ = handler.classify_input(tech, "tech_stack", "info_gathering")
        assert fallback_type == expected
    
    # === Question Detection Tests ===
    def test_question_detection(self, handler):
        fallback_type, _ = handler.classify_input(
            "What is this about?",
            "email",
            "info_gathering"
        )
        assert fallback_type == FallbackType.QUESTION
    
    # === Response Generation Tests ===
    def test_exit_response(self, handler):
        _, response = handler.classify_input("bye", "email", "info_gathering")
        assert "thank" in response.lower()
    
    def test_hostile_response(self, handler):
        _, response = handler.classify_input("this is stupid", "email", "info_gathering")
        assert "professional" in response.lower()
    
    def test_incomplete_response(self, handler):
        _, response = handler.classify_input("", "full_name", "info_gathering")
        assert "name" in response.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
