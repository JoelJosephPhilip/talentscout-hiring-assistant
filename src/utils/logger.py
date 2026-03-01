"""
Comprehensive Logging System for TalentScout Hiring Assistant.

This module provides detailed logging for:
- Debugging and troubleshooting
- Model improvement and training
- Prompt optimization
- UI/UX issue resolution
- Performance analysis

Log Structure:
- logs/sessions/    - Individual session logs (JSON)
- logs/daily/       - Daily aggregated logs (JSON)
- logs/errors/      - Error-specific logs (JSON)
"""

import json
import uuid
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class LogConfig:
    """Configuration for logging behavior."""
    log_dir: str = "logs"
    include_pii: bool = False
    log_to_console: bool = True
    log_llm_responses: bool = True
    log_prompt_templates: bool = True
    log_sentiment: bool = True
    log_ui_events: bool = True
    log_performance: bool = True
    max_session_files: int = 1000
    session_rotation_hours: int = 24


@dataclass
class ConversationTurn:
    """Single turn in conversation."""
    turn: int
    timestamp: str
    phase: str
    user_input: str
    llm_response: str
    response_time_ms: float
    tokens_used: Dict[str, int] = field(default_factory=dict)
    sentiment: Optional[Dict[str, Any]] = None
    fallback_triggered: Optional[str] = None
    prompt_template_used: Optional[str] = None
    cache_hit: bool = False


@dataclass
class UIEvent:
    """UI-related event."""
    timestamp: str
    event_type: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorLog:
    """Error log entry."""
    timestamp: str
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


def anonymize_pii(text: str, pii_type: str = "generic") -> str:
    """
    Anonymize PII in text by replacing with hash-based identifier.
    
    Args:
        text: Text containing potential PII
        pii_type: Type of PII (email, name, phone, etc.)
    
    Returns:
        Anonymized text with [ANONYMIZED:hash] format
    """
    if not text:
        return text
    
    hash_val = hashlib.sha256(text.encode()).hexdigest()[:8]
    return f"[ANONYMIZED:{pii_type}:{hash_val}]"


class SessionLogger:
    """
    Comprehensive session logger for TalentScout.
    
    Logs all aspects of a hiring conversation session including:
    - Conversation turns with full context
    - LLM responses and prompts used
    - Sentiment analysis results
    - UI events and interactions
    - Performance metrics
    - Errors and warnings
    """
    
    def __init__(self, config: Optional[LogConfig] = None):
        self.config = config or LogConfig()
        self.session_id = self._generate_session_id()
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        
        self._init_session_data()
        self._init_directories()
        self._lock = threading.Lock()
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:6]
        return f"{timestamp}_{unique_id}"
    
    def _init_session_data(self):
        """Initialize session data structure."""
        self.session_data = {
            "session_id": self.session_id,
            "timestamp_start": self.start_time.isoformat(),
            "timestamp_end": None,
            "config": {
                "language": "en",
                "theme": "light",
                "llm_provider": None,
                "model": None,
                "include_pii": self.config.include_pii
            },
            "candidate_info": {
                "name": None,
                "email": None,
                "phone": None,
                "position": None,
                "experience": None,
                "location": None,
                "tech_stack": []
            },
            "conversation": [],
            "ui_events": [],
            "errors": [],
            "metrics": {
                "total_duration_seconds": None,
                "total_turns": 0,
                "total_tokens": {"input": 0, "output": 0},
                "avg_response_time_ms": 0,
                "sentiment_trend": [],
                "cache_hits": 0,
                "fallback_count": 0
            },
            "assessment": {
                "overall_sentiment": None,
                "confidence_score": None,
                "uncertainty_phrases": [],
                "tech_questions_answered": 0,
                "tech_questions_total": 0
            }
        }
    
    def _init_directories(self):
        """Initialize log directories."""
        base_path = Path(self.config.log_dir)
        
        self.session_dir = base_path / "sessions"
        self.daily_dir = base_path / "daily"
        self.error_dir = base_path / "errors"
        
        for dir_path in [self.session_dir, self.daily_dir, self.error_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def set_config(self, key: str, value: Any):
        """Set a configuration value."""
        with self._lock:
            if key in self.session_data["config"]:
                self.session_data["config"][key] = value
                self._log_to_console(f"Config set: {key}={value}", LogLevel.DEBUG)
    
    def update_candidate_info(self, field: str, value: Any):
        """
        Update candidate information.
        
        Args:
            field: Field name (name, email, phone, position, experience, location, tech_stack)
            value: Field value
        """
        with self._lock:
            if field in self.session_data["candidate_info"]:
                if self.config.include_pii:
                    self.session_data["candidate_info"][field] = value
                else:
                    pii_types = {
                        "name": "name",
                        "email": "email",
                        "phone": "phone"
                    }
                    if field in pii_types:
                        self.session_data["candidate_info"][field] = anonymize_pii(str(value), pii_types[field])
                    else:
                        self.session_data["candidate_info"][field] = value
                
                self._log_to_console(f"Candidate info updated: {field}", LogLevel.DEBUG)
    
    def log_conversation_turn(
        self,
        user_input: str,
        llm_response: str,
        phase: str,
        response_time_ms: float,
        tokens: Optional[Dict[str, int]] = None,
        sentiment: Optional[Dict[str, Any]] = None,
        prompt_template: Optional[str] = None,
        fallback_type: Optional[str] = None,
        cache_hit: bool = False
    ):
        """
        Log a complete conversation turn.
        
        Args:
            user_input: User's message
            llm_response: LLM's response
            phase: Current conversation phase
            response_time_ms: Response time in milliseconds
            tokens: Token counts {input: n, output: m}
            sentiment: Sentiment analysis result
            prompt_template: Name of prompt template used
            fallback_type: Type of fallback if triggered
            cache_hit: Whether response came from cache
        """
        with self._lock:
            turn_num = len(self.session_data["conversation"]) + 1
            
            user_display = user_input
            if not self.config.include_pii:
                pii_fields = {
                    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
                    "phone": r"[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}"
                }
            
            turn = ConversationTurn(
                turn=turn_num,
                timestamp=datetime.now().isoformat(),
                phase=phase,
                user_input=user_input if self.config.include_pii else self._anonymize_input(user_input),
                llm_response=llm_response if self.config.log_llm_responses else "[REDACTED]",
                response_time_ms=response_time_ms,
                tokens_used=tokens or {},
                sentiment=sentiment if self.config.log_sentiment else None,
                prompt_template_used=prompt_template if self.config.log_prompt_templates else None,
                fallback_triggered=fallback_type,
                cache_hit=cache_hit
            )
            
            self.session_data["conversation"].append(asdict(turn))
            
            self.session_data["metrics"]["total_turns"] = turn_num
            if tokens:
                self.session_data["metrics"]["total_tokens"]["input"] += tokens.get("input", 0)
                self.session_data["metrics"]["total_tokens"]["output"] += tokens.get("output", 0)
            if cache_hit:
                self.session_data["metrics"]["cache_hits"] += 1
            if fallback_type:
                self.session_data["metrics"]["fallback_count"] += 1
            if sentiment and "confidence_score" in sentiment:
                self.session_data["metrics"]["sentiment_trend"].append(sentiment["confidence_score"])
            
            self._log_to_console(f"Turn {turn_num} logged (phase: {phase}, time: {response_time_ms:.0f}ms)", LogLevel.INFO)
    
    def _anonymize_input(self, text: str) -> str:
        """Anonymize potential PII in input text."""
        import re
        
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        phone_pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
        
        def replace_email(m):
            return anonymize_pii(m.group(), "email")
        
        def replace_phone(m):
            return anonymize_pii(m.group(), "phone")
        
        text = re.sub(email_pattern, replace_email, text)
        text = re.sub(phone_pattern, replace_phone, text)
        
        return text
    
    def log_ui_event(self, event_type: str, details: Optional[Dict[str, Any]] = None):
        """
        Log a UI event.
        
        Args:
            event_type: Type of UI event (theme_change, language_change, scroll, click, etc.)
            details: Additional details about the event
        """
        if not self.config.log_ui_events:
            return
        
        with self._lock:
            event = UIEvent(
                timestamp=datetime.now().isoformat(),
                event_type=event_type,
                details=details or {}
            )
            self.session_data["ui_events"].append(asdict(event))
            self._log_to_console(f"UI event: {event_type}", LogLevel.DEBUG)
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Log an error.
        
        Args:
            error_type: Type/class of error
            error_message: Error message
            stack_trace: Full stack trace if available
            context: Additional context (phase, input, etc.)
        """
        with self._lock:
            error = ErrorLog(
                timestamp=datetime.now().isoformat(),
                error_type=error_type,
                error_message=error_message,
                stack_trace=stack_trace,
                context=context or {}
            )
            self.session_data["errors"].append(asdict(error))
            self._log_to_console(f"ERROR: {error_type}: {error_message}", LogLevel.ERROR)
            
            self._write_error_log(error)
    
    def update_assessment(self, field: str, value: Any):
        """Update assessment data."""
        with self._lock:
            if field in self.session_data["assessment"]:
                self.session_data["assessment"][field] = value
    
    def finalize_session(self) -> str:
        """
        Finalize and save the session log.
        
        Returns:
            Path to the saved session file
        """
        with self._lock:
            self.end_time = datetime.now()
            self.session_data["timestamp_end"] = self.end_time.isoformat()
            
            duration = (self.end_time - self.start_time).total_seconds()
            self.session_data["metrics"]["total_duration_seconds"] = round(duration, 2)
            
            turns = self.session_data["conversation"]
            if turns:
                total_time = sum(t["response_time_ms"] for t in turns)
                self.session_data["metrics"]["avg_response_time_ms"] = round(total_time / len(turns), 2)
            
            session_file = self._write_session_log()
            self._write_daily_summary()
            
            self._log_to_console(f"Session finalized: {self.session_id}", LogLevel.INFO)
            
            return session_file
    
    def _write_session_log(self) -> str:
        """Write session log to file."""
        filename = f"session_{self.session_id}.json"
        filepath = self.session_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.session_data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def _write_error_log(self, error: ErrorLog):
        """Write error to dedicated error log file."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"errors_{date_str}.json"
        filepath = self.error_dir / filename
        
        errors = []
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    errors = json.load(f)
                except json.JSONDecodeError:
                    errors = []
        
        errors.append(asdict(error))
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(errors, f, indent=2, ensure_ascii=False)
    
    def _write_daily_summary(self):
        """Write/update daily summary file."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}.json"
        filepath = self.daily_dir / filename
        
        daily_data = {
            "date": date_str,
            "sessions": []
        }
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    daily_data = json.load(f)
                except json.JSONDecodeError:
                    pass
        
        session_summary = {
            "session_id": self.session_id,
            "duration_seconds": self.session_data["metrics"]["total_duration_seconds"],
            "turns": self.session_data["metrics"]["total_turns"],
            "sentiment_avg": round(
                sum(self.session_data["metrics"]["sentiment_trend"]) / len(self.session_data["metrics"]["sentiment_trend"]), 2
            ) if self.session_data["metrics"]["sentiment_trend"] else None,
            "error_count": len(self.session_data["errors"]),
            "llm_provider": self.session_data["config"]["llm_provider"],
            "language": self.session_data["config"]["language"]
        }
        
        daily_data["sessions"].append(session_summary)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(daily_data, f, indent=2, ensure_ascii=False)
    
    def _log_to_console(self, message: str, level: LogLevel):
        """Log to console if enabled."""
        if self.config.log_to_console:
            timestamp = datetime.now().strftime("%H:%M:%S")
            level_str = f"[{level.value.upper()}]"
            print(f"[TalentScout Logger] {timestamp} {level_str} {message}")
    
    def get_session_data(self) -> Dict[str, Any]:
        """Get current session data (for debugging)."""
        with self._lock:
            return json.loads(json.dumps(self.session_data))


class LogManager:
    """
    Manager for handling multiple logging sessions and utilities.
    """
    
    def __init__(self, config: Optional[LogConfig] = None):
        self.config = config or LogConfig()
        self.active_sessions: Dict[str, SessionLogger] = {}
    
    def create_session(self) -> SessionLogger:
        """Create a new logging session."""
        logger = SessionLogger(self.config)
        self.active_sessions[logger.session_id] = logger
        return logger
    
    def get_session(self, session_id: str) -> Optional[SessionLogger]:
        """Get an active session by ID."""
        return self.active_sessions.get(session_id)
    
    def close_session(self, session_id: str) -> Optional[str]:
        """Close and save a session."""
        session = self.active_sessions.pop(session_id, None)
        if session:
            return session.finalize_session()
        return None
    
    def load_session(self, filepath: str) -> Dict[str, Any]:
        """Load a session log from file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def analyze_daily_logs(self, date_str: str) -> Dict[str, Any]:
        """
        Analyze all sessions from a specific date.
        
        Args:
            date_str: Date in YYYY-MM-DD format
        
        Returns:
            Analysis summary
        """
        daily_file = self.config.log_dir + f"/daily/{date_str}.json"
        
        if not Path(daily_file).exists():
            return {"error": f"No logs found for {date_str}"}
        
        with open(daily_file, 'r', encoding='utf-8') as f:
            daily_data = json.load(f)
        
        sessions = daily_data.get("sessions", [])
        
        if not sessions:
            return {"error": f"No sessions logged for {date_str}"}
        
        total_duration = sum(s.get("duration_seconds", 0) or 0 for s in sessions)
        total_turns = sum(s.get("turns", 0) for s in sessions)
        sentiments = [s.get("sentiment_avg") for s in sessions if s.get("sentiment_avg")]
        
        return {
            "date": date_str,
            "total_sessions": len(sessions),
            "total_duration_hours": round(total_duration / 3600, 2),
            "total_turns": total_turns,
            "avg_sentiment": round(sum(sentiments) / len(sentiments), 2) if sentiments else None,
            "error_rate": sum(1 for s in sessions if s.get("error_count", 0) > 0) / len(sessions),
            "language_distribution": self._count_by_field(sessions, "language"),
            "provider_distribution": self._count_by_field(sessions, "llm_provider")
        }
    
    def _count_by_field(self, sessions: List[Dict], field: str) -> Dict[str, int]:
        """Count sessions by a field value."""
        counts = {}
        for session in sessions:
            value = session.get(field, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts
    
    def search_logs(
        self,
        query: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        min_sentiment: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search through session logs.
        
        Args:
            query: Text to search for in conversations
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            min_sentiment: Minimum average sentiment
        
        Returns:
            List of matching sessions
        """
        results = []
        session_dir = Path(self.config.log_dir) / "sessions"
        
        for log_file in session_dir.glob("*.json"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if query:
                    found = False
                    for turn in data.get("conversation", []):
                        if query.lower() in turn.get("user_input", "").lower():
                            found = True
                            break
                        if query.lower() in turn.get("llm_response", "").lower():
                            found = True
                            break
                    if not found:
                        continue
                
                session_date = data.get("timestamp_start", "")[:10]
                
                if start_date and session_date < start_date:
                    continue
                if end_date and session_date > end_date:
                    continue
                
                sentiment_trend = data.get("metrics", {}).get("sentiment_trend", [])
                avg_sentiment = sum(sentiment_trend) / len(sentiment_trend) if sentiment_trend else 0
                
                if min_sentiment and avg_sentiment < min_sentiment:
                    continue
                
                results.append({
                    "session_id": data.get("session_id"),
                    "date": session_date,
                    "avg_sentiment": round(avg_sentiment, 2),
                    "turns": data.get("metrics", {}).get("total_turns", 0),
                    "error_count": len(data.get("errors", []))
                })
            
            except (json.JSONDecodeError, KeyError):
                continue
        
        return results
