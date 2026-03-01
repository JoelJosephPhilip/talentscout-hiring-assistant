from enum import Enum
from typing import Optional
from dataclasses import dataclass, field
import uuid
from datetime import datetime


class ConversationState(Enum):
    INIT = "init"
    GREETING = "greeting"
    INFO_GATHERING = "info_gathering"
    TECH_DECLARATION = "tech_declaration"
    QUESTIONING = "questioning"
    SENTIMENT_CHECK = "sentiment_check"
    EXIT = "exit"


@dataclass
class CandidateInfo:
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    years_experience: Optional[int] = None
    desired_position: Optional[str] = None
    location: Optional[str] = None
    tech_stack: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "years_experience": self.years_experience,
            "desired_position": self.desired_position,
            "location": self.location,
            "tech_stack": self.tech_stack
        }

    def is_complete(self) -> bool:
        return all([
            self.full_name,
            self.email,
            self.phone is not None,
            self.years_experience is not None,
            self.desired_position,
            self.location,
            len(self.tech_stack) > 0
        ])

    def get_missing_fields(self) -> list:
        missing = []
        if not self.full_name:
            missing.append("full_name")
        if not self.email:
            missing.append("email")
        if not self.phone:
            missing.append("phone")
        if self.years_experience is None:
            missing.append("years_experience")
        if not self.desired_position:
            missing.append("desired_position")
        if not self.location:
            missing.append("location")
        if not self.tech_stack:
            missing.append("tech_stack")
        return missing


@dataclass
class Question:
    question_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    technology: str = ""
    question_text: str = ""
    difficulty: str = "intermediate"
    evaluation_criteria: list = field(default_factory=list)
    candidate_response: Optional[str] = None
    response_timestamp: Optional[datetime] = None


@dataclass
class SentimentData:
    overall_confidence_score: float = 0.0
    sentiment_label: str = "neutral"
    uncertainty_indicators: list = field(default_factory=list)
    enthusiasm: str = "medium"
    notes: str = ""


@dataclass
class ConversationData:
    candidate_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    candidate_info: CandidateInfo = field(default_factory=CandidateInfo)
    questions: list = field(default_factory=list)
    sentiment_data: SentimentData = field(default_factory=SentimentData)
    state_history: list = field(default_factory=list)
    conversation_history: list = field(default_factory=list)
    total_turns: int = 0
    exit_type: str = "normal"
    llm_provider: str = ""


class StateManager:
    """Manages conversation state and transitions"""

    STATE_TRANSITIONS = {
        ConversationState.INIT: {
            "start": ConversationState.GREETING
        },
        ConversationState.GREETING: {
            "greeting_complete": ConversationState.INFO_GATHERING,
            "exit": ConversationState.EXIT
        },
        ConversationState.INFO_GATHERING: {
            "all_fields_collected": ConversationState.TECH_DECLARATION,
            "exit": ConversationState.EXIT
        },
        ConversationState.TECH_DECLARATION: {
            "tech_stack_confirmed": ConversationState.QUESTIONING,
            "exit": ConversationState.EXIT
        },
        ConversationState.QUESTIONING: {
            "all_questions_answered": ConversationState.SENTIMENT_CHECK,
            "exit": ConversationState.EXIT
        },
        ConversationState.SENTIMENT_CHECK: {
            "analysis_complete": ConversationState.EXIT
        },
        ConversationState.EXIT: {}
    }

    def __init__(self):
        self.current_state = ConversationState.INIT
        self.data = ConversationData()

    def transition(self, trigger: str) -> bool:
        """
        Transition to next state based on trigger.
        
        Args:
            trigger: The event that triggers transition
        
        Returns:
            True if transition was successful, False otherwise
        """
        if trigger == "exit":
            self.current_state = ConversationState.EXIT
            self.data.state_history.append(self.current_state.value)
            return True

        allowed_transitions = self.STATE_TRANSITIONS.get(self.current_state, {})
        next_state = allowed_transitions.get(trigger)

        if next_state:
            self.current_state = next_state
            self.data.state_history.append(self.current_state.value)
            return True
        
        return False

    def get_current_state(self) -> ConversationState:
        """Get current conversation state"""
        return self.current_state

    def add_to_history(self, role: str, message: str):
        """Add message to conversation history"""
        self.data.conversation_history.append({
            "role": role,
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        self.data.total_turns += 1

    def update_candidate_info(self, field_name: str, value):
        """Update a specific field in candidate info"""
        if hasattr(self.data.candidate_info, field_name):
            setattr(self.data.candidate_info, field_name, value)

    def add_question(self, question: Question):
        """Add a question to the assessment"""
        self.data.questions.append(question)

    def get_current_question_index(self) -> int:
        """Get the index of the current unanswered question"""
        for i, q in enumerate(self.data.questions):
            if q.candidate_response is None:
                return i
        return len(self.data.questions)

    def all_questions_answered(self) -> bool:
        """Check if all questions have been answered"""
        return all(q.candidate_response is not None for q in self.data.questions)

    def set_sentiment_data(self, sentiment_data: dict):
        """Update sentiment analysis data"""
        self.data.sentiment_data.overall_confidence_score = sentiment_data.get("confidence_score", 0.0)
        self.data.sentiment_data.sentiment_label = sentiment_data.get("sentiment", "neutral")
        self.data.sentiment_data.uncertainty_indicators = sentiment_data.get("uncertainty_phrases", [])
        self.data.sentiment_data.enthusiasm = sentiment_data.get("enthusiasm", "medium")
        self.data.sentiment_data.notes = sentiment_data.get("notes", "")

    def set_exit_type(self, exit_type: str):
        """Set the exit type (normal, early, error)"""
        self.data.exit_type = exit_type

    def set_llm_provider(self, provider: str):
        """Set the LLM provider used"""
        self.data.llm_provider = provider

    def to_dict(self) -> dict:
        """Export all data as dictionary"""
        return {
            "candidate_id": self.data.candidate_id,
            "timestamp": self.data.timestamp.isoformat(),
            "candidate_info": self.data.candidate_info.to_dict(),
            "questions": [
                {
                    "question_id": q.question_id,
                    "technology": q.technology,
                    "question_text": q.question_text,
                    "difficulty": q.difficulty,
                    "candidate_response": q.candidate_response,
                    "response_timestamp": q.response_timestamp.isoformat() if q.response_timestamp else None
                }
                for q in self.data.questions
            ],
            "sentiment_analysis": {
                "overall_confidence_score": self.data.sentiment_data.overall_confidence_score,
                "sentiment_label": self.data.sentiment_data.sentiment_label,
                "uncertainty_indicators": self.data.sentiment_data.uncertainty_indicators,
                "enthusiasm": self.data.sentiment_data.enthusiasm,
                "notes": self.data.sentiment_data.notes
            },
            "conversation": {
                "state_history": self.data.state_history,
                "conversation_history": self.data.conversation_history,
                "total_turns": self.data.total_turns,
                "exit_type": self.data.exit_type,
                "llm_provider": self.data.llm_provider
            }
        }
