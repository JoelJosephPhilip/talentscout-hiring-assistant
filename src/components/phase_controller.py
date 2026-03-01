from typing import Optional
from .state_manager import StateManager, ConversationState, Question
from .fallback_handler import FallbackHandler, FallbackType
from ..llm.base import BaseLLM
from ..prompts import templates as prompts


class PhaseController:
    """Orchestrates phase-specific logic for conversation flow"""

    FIELD_ORDER = [
        "full_name",
        "email",
        "phone",
        "years_experience",
        "desired_position",
        "location",
        "tech_stack"
    ]

    FIELD_PROMPTS = {
        "full_name": "Let's start with your name. What's your full name?",
        "email": "Great! What's your email address?",
        "phone": "Thanks! And your phone number?",
        "years_experience": "How many years of professional experience do you have?",
        "desired_position": "What position are you applying for?",
        "location": "Where are you currently located?",
        "tech_stack": "Finally, what technologies are you proficient in? Please list programming languages, frameworks, databases, and tools."
    }

    def __init__(self, llm: BaseLLM, state_manager: StateManager):
        self.llm = llm
        self.state = state_manager
        self.fallback_handler = FallbackHandler()
        self.current_question_idx = 0
        self._questions_generated = False

    def process_input(self, user_input: str) -> str:
        """
        Process user input based on current phase.
        
        Args:
            user_input: User's message
        
        Returns:
            Bot's response
        """
        current_state = self.state.get_current_state()

        if current_state == ConversationState.GREETING:
            return self._handle_greeting(user_input)
        elif current_state == ConversationState.INFO_GATHERING:
            return self._handle_info_gathering(user_input)
        elif current_state == ConversationState.TECH_DECLARATION:
            return self._handle_tech_declaration(user_input)
        elif current_state == ConversationState.QUESTIONING:
            return self._handle_questioning(user_input)
        elif current_state == ConversationState.SENTIMENT_CHECK:
            return self._handle_sentiment_check()
        elif current_state == ConversationState.EXIT:
            return self._handle_exit()
        else:
            return self._start_greeting()

    def _start_greeting(self) -> str:
        """Generate and return greeting message"""
        self.state.transition("start")
        context = {
            "system_prompt": prompts.MASTER_SYSTEM_PROMPT.format(
                phase="GREETING",
                collected_data="{}"
            )
        }
        greeting = self.llm.generate_response(
            prompts.GREETING_PROMPT.strip(),
            context
        )
        self.state.add_to_history("assistant", greeting)
        return greeting

    def _handle_greeting(self, user_input: str) -> str:
        """Handle greeting phase"""
        self.state.add_to_history("user", user_input)
        
        # Check for exit
        fallback_type, _ = self.fallback_handler.classify_input(
            user_input, "full_name", "greeting"
        )
        
        if fallback_type == FallbackType.EXIT:
            self.state.transition("exit")
            self.state.set_exit_type("early")
            return self._handle_exit()

        # Transition to info gathering
        self.state.transition("greeting_complete")
        return self._ask_next_field()

    def _handle_info_gathering(self, user_input: str) -> str:
        """Handle information gathering phase"""
        self.state.add_to_history("user", user_input)
        
        # Get next missing field
        missing_fields = self.state.data.candidate_info.get_missing_fields()
        
        if not missing_fields:
            self.state.transition("all_fields_collected")
            return self._confirm_tech_stack()

        current_field = missing_fields[0]
        
        # Validate input
        fallback_type, fallback_msg = self.fallback_handler.classify_input(
            user_input, current_field, "info_gathering"
        )

        if fallback_type == FallbackType.EXIT:
            self.state.transition("exit")
            self.state.set_exit_type("early")
            return self._handle_exit()

        if fallback_type == FallbackType.HOSTILE:
            self.state.add_to_history("assistant", fallback_msg)
            return fallback_msg

        if fallback_type == FallbackType.QUESTION:
            response = fallback_msg + " " + self._ask_next_field()
            self.state.add_to_history("assistant", response)
            return response

        if fallback_type not in [FallbackType.NONE, FallbackType.QUESTION]:
            self.state.add_to_history("assistant", fallback_msg)
            return fallback_msg

        # Valid input - store it
        self._store_field(current_field, user_input)
        
        # Check if all fields collected
        missing_fields = self.state.data.candidate_info.get_missing_fields()
        if not missing_fields:
            self.state.transition("all_fields_collected")
            return self._confirm_tech_stack()
        
        return self._ask_next_field()

    def _handle_tech_declaration(self, user_input: str) -> str:
        """Handle tech stack confirmation"""
        self.state.add_to_history("user", user_input)
        
        # Accept confirmation responses like "yes", "no", "ok", "correct"
        user_lower = user_input.lower().strip()
        confirmation_words = ["yes", "no", "ok", "okay", "correct", "right", 
                            "yeah", "yep", "sure", "fine", "good", "perfect"]
        
        # Only exit if it's a clear exit signal
        if user_lower in ["bye", "quit", "exit", "stop", "goodbye"]:
            self.state.transition("exit")
            self.state.set_exit_type("early")
            return self._handle_exit()

        # Accept any response and transition to questioning
        self.state.transition("tech_stack_confirmed")
        return self._start_questioning()

    def _handle_questioning(self, user_input: str) -> str:
        """Handle technical questioning phase"""
        self.state.add_to_history("user", user_input)
        
        # Check for exit
        fallback_type, _ = self.fallback_handler.classify_input(
            user_input, "technical_response", "questioning"
        )
        
        if fallback_type == FallbackType.EXIT:
            self.state.transition("exit")
            self.state.set_exit_type("early")
            return self._handle_exit()

        # Store answer to current question
        questions = self.state.data.questions
        if self.current_question_idx < len(questions):
            questions[self.current_question_idx].candidate_response = user_input
            from datetime import datetime
            questions[self.current_question_idx].response_timestamp = datetime.now()
            self.current_question_idx += 1

        # Check if all questions answered
        if self.current_question_idx >= len(questions):
            self.state.transition("all_questions_answered")
            return self._handle_sentiment_check()

        # Ask next question
        next_question = questions[self.current_question_idx]
        response = f"Great answer! Next question about {next_question.technology}:\n\n{next_question.question_text}"
        self.state.add_to_history("assistant", response)
        return response

    def _handle_sentiment_check(self) -> str:
        """Analyze overall sentiment and transition to exit"""
        self.state.transition("analysis_complete")
        return self._handle_exit()

    def _handle_exit(self) -> str:
        """Generate exit message"""
        context = {
            "system_prompt": prompts.MASTER_SYSTEM_PROMPT.format(
                phase="EXIT",
                collected_data=str(self.state.data.candidate_info.to_dict())
            )
        }
        
        name = self.state.data.candidate_info.full_name or "there"
        status = "complete" if self.state.data.candidate_info.is_complete() else "partial"
        
        exit_msg = self.llm.generate_response(
            prompts.EXIT_PROMPT.format(name=name, status=status),
            context
        )
        
        self.state.add_to_history("assistant", exit_msg)
        return exit_msg

    def _ask_next_field(self) -> str:
        """Ask for the next missing field"""
        missing_fields = self.state.data.candidate_info.get_missing_fields()
        if not missing_fields:
            return self._confirm_tech_stack()
        
        next_field = missing_fields[0]
        prompt = self.FIELD_PROMPTS.get(next_field, f"What is your {next_field}?")
        self.state.add_to_history("assistant", prompt)
        return prompt

    def _store_field(self, field_name: str, value: str):
        """Store a field value in candidate info"""
        if field_name == "years_experience":
            try:
                value = int(value.strip())
            except ValueError:
                value = 0
        elif field_name == "tech_stack":
            import re
            value = [t.strip() for t in re.split(r'[,，\s]+', value) if t.strip()]
        
        self.state.update_candidate_info(field_name, value)

    def _confirm_tech_stack(self) -> str:
        """Confirm tech stack with candidate"""
        tech_stack = self.state.data.candidate_info.tech_stack
        if tech_stack:
            tech_list = ", ".join(tech_stack)
        else:
            tech_list = "no technologies listed"
        
        response = f"Thank you for sharing! I've recorded the following: {tech_list}. Is this correct, or would you like to add anything?"
        self.state.add_to_history("assistant", response)
        return response

    def _start_questioning(self) -> str:
        """Generate questions and start questioning phase"""
        if not self._questions_generated:
            self._generate_questions()
            self._questions_generated = True
        
        questions = self.state.data.questions
        if not questions:
            return self._handle_exit()
        
        first_question = questions[0]
        response = f"Excellent! Let's begin the technical assessment.\n\nFirst question about {first_question.technology}:\n\n{first_question.question_text}"
        self.state.add_to_history("assistant", response)
        return response

    def _generate_questions(self):
        """Generate technical questions using LLM"""
        candidate = self.state.data.candidate_info
        
        questions_data = self.llm.generate_questions(
            tech_stack=candidate.tech_stack,
            position=candidate.desired_position or "Software Developer",
            years_experience=candidate.years_experience or 0,
            questions_per_tech=3
        )
        
        for q_data in questions_data:
            question = Question(
                technology=q_data.get("technology", "General"),
                question_text=q_data.get("question", ""),
                difficulty=q_data.get("difficulty", "intermediate"),
                evaluation_criteria=q_data.get("evaluation_criteria", [])
            )
            self.state.add_question(question)

    def get_progress(self) -> dict:
        """Get current progress information"""
        missing = len(self.state.data.candidate_info.get_missing_fields())
        total_fields = len(self.FIELD_ORDER)
        
        return {
            "phase": self.state.get_current_state().value,
            "fields_collected": total_fields - missing,
            "total_fields": total_fields,
            "questions_answered": self.current_question_idx,
            "total_questions": len(self.state.data.questions)
        }
