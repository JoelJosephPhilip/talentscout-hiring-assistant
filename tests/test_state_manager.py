import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.components.state_manager import (
    StateManager, 
    ConversationState, 
    CandidateInfo,
    ConversationData,
    Question
)


class TestCandidateInfo:
    
    def test_empty_candidate_info(self):
        """Test empty candidate info"""
        info = CandidateInfo()
        assert info.is_complete() == False
        assert len(info.get_missing_fields()) == 7
    
    def test_partial_candidate_info(self):
        """Test partially filled candidate info"""
        info = CandidateInfo(
            full_name="John Doe",
            email="john@example.com"
        )
        assert info.is_complete() == False
        missing = info.get_missing_fields()
        assert "full_name" not in missing
        assert "email" not in missing
        assert "phone" in missing
    
    def test_complete_candidate_info(self):
        """Test complete candidate info"""
        info = CandidateInfo(
            full_name="John Doe",
            email="john@example.com",
            phone="555-1234",
            years_experience=5,
            desired_position="Developer",
            location="NYC",
            tech_stack=["Python", "Django"]
        )
        assert info.is_complete() == True
        assert len(info.get_missing_fields()) == 0
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        info = CandidateInfo(
            full_name="Jane",
            email="jane@test.com",
            phone="123456",
            years_experience=3,
            desired_position="Engineer",
            location="LA",
            tech_stack=["React"]
        )
        data = info.to_dict()
        assert data["full_name"] == "Jane"
        assert data["email"] == "jane@test.com"
        assert data["years_experience"] == 3
        assert "React" in data["tech_stack"]


class TestStateManager:
    
    def test_initial_state(self):
        """Test initial state is INIT"""
        sm = StateManager()
        assert sm.get_current_state() == ConversationState.INIT
    
    def test_transition_to_greeting(self):
        """Test transition from INIT to GREETING"""
        sm = StateManager()
        result = sm.transition("start")
        assert result == True
        assert sm.get_current_state() == ConversationState.GREETING
    
    def test_transition_greeting_to_info_gathering(self):
        """Test transition from GREETING to INFO_GATHERING"""
        sm = StateManager()
        sm.transition("start")
        result = sm.transition("greeting_complete")
        assert result == True
        assert sm.get_current_state() == ConversationState.INFO_GATHERING
    
    def test_transition_to_exit_anytime(self):
        """Test that exit can be triggered from any state"""
        sm = StateManager()
        sm.transition("start")
        sm.transition("greeting_complete")
        
        # Exit from INFO_GATHERING
        result = sm.transition("exit")
        assert result == True
        assert sm.get_current_state() == ConversationState.EXIT
    
    def test_invalid_transition(self):
        """Test invalid transition returns False"""
        sm = StateManager()
        result = sm.transition("invalid_trigger")
        assert result == False
        assert sm.get_current_state() == ConversationState.INIT
    
    def test_add_to_history(self):
        """Test adding to conversation history"""
        sm = StateManager()
        sm.add_to_history("user", "Hello")
        sm.add_to_history("assistant", "Hi there!")
        
        assert len(sm.data.conversation_history) == 2
        assert sm.data.total_turns == 2
    
    def test_update_candidate_info(self):
        """Test updating candidate info"""
        sm = StateManager()
        sm.update_candidate_info("full_name", "John Doe")
        sm.update_candidate_info("years_experience", 5)
        
        assert sm.data.candidate_info.full_name == "John Doe"
        assert sm.data.candidate_info.years_experience == 5
    
    def test_add_question(self):
        """Test adding questions"""
        sm = StateManager()
        q = Question(
            technology="Python",
            question_text="What is GIL?",
            difficulty="intermediate"
        )
        sm.add_question(q)
        
        assert len(sm.data.questions) == 1
        assert sm.data.questions[0].technology == "Python"
    
    def test_all_questions_answered(self):
        """Test checking if all questions answered"""
        sm = StateManager()
        q1 = Question(question_text="Q1", candidate_response="A1")
        q2 = Question(question_text="Q2", candidate_response=None)
        
        sm.add_question(q1)
        sm.add_question(q2)
        
        assert sm.all_questions_answered() == False
        
        q2.candidate_response = "A2"
        assert sm.all_questions_answered() == True
    
    def test_to_dict(self):
        """Test exporting to dictionary"""
        sm = StateManager()
        sm.transition("start")
        sm.update_candidate_info("full_name", "Test")
        
        data = sm.to_dict()
        assert "candidate_id" in data
        assert "candidate_info" in data
        assert data["candidate_info"]["full_name"] == "Test"
        assert "greeting" in data["conversation"]["state_history"]


class TestQuestion:
    
    def test_question_defaults(self):
        """Test question default values"""
        q = Question()
        assert q.question_id is not None
        assert q.technology == ""
        assert q.question_text == ""
        assert q.candidate_response is None
    
    def test_question_with_values(self):
        """Test question with custom values"""
        q = Question(
            technology="Python",
            question_text="Explain decorators",
            difficulty="intermediate",
            evaluation_criteria=["syntax", "use cases"]
        )
        assert q.technology == "Python"
        assert q.difficulty == "intermediate"
        assert len(q.evaluation_criteria) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
