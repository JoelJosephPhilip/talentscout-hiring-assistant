import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from src.llm import LLMFactory
from src.components import (
    StateManager, ConversationState, PhaseController, SentimentAnalyzer,
    PersonalizationEngine, UsageTracker, PrecomputedResponses
)
from src.ui.components import (
    render_header, render_progress, render_llm_provider_badge,
    render_llm_toggle, render_candidate_info_sidebar,
    render_typing_indicator, render_language_selector,
    render_theme_toggle, render_usage_stats,
    render_sentiment_sidebar, render_final_sentiment_report,
    render_sentiment_badge_realtime, get_custom_css, get_dark_mode_css
)
from src.i18n import get_translation, SUPPORTED_LANGUAGES


def initialize_session_state():
    """Initialize session state variables"""
    if "state_manager" not in st.session_state:
        st.session_state.state_manager = StateManager()
    
    if "llm" not in st.session_state:
        st.session_state.llm = None
    
    if "llm_provider" not in st.session_state:
        st.session_state.llm_provider = "auto"
    
    if "phase_controller" not in st.session_state:
        st.session_state.phase_controller = None
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "started" not in st.session_state:
        st.session_state.started = False
    
    if "llm_error" not in st.session_state:
        st.session_state.llm_error = None
    
    if "language" not in st.session_state:
        st.session_state.language = "en"
    
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    
    if "usage_tracker" not in st.session_state:
        st.session_state.usage_tracker = UsageTracker()
    
    if "sentiment_history" not in st.session_state:
        st.session_state.sentiment_history = []
    
    if "cache_hits" not in st.session_state:
        st.session_state.cache_hits = 0


def initialize_llm(preferred: str = "auto"):
    """Initialize LLM based on preference"""
    try:
        llm = LLMFactory.create_llm(preferred=preferred)
        provider_name = llm.get_provider_name()
        is_fallback = preferred == "auto" and "Ollama" in provider_name
        return llm, provider_name, is_fallback, None
    except Exception as e:
        return None, None, None, str(e)


def main():
    st.set_page_config(
        page_title="TalentScout Hiring Assistant",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Get current language and theme
    language = st.session_state.language
    theme = st.session_state.theme
    
    # Apply CSS based on theme
    if theme == "dark":
        st.markdown(get_dark_mode_css(), unsafe_allow_html=True)
    else:
        st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Render header
    render_header(language)
    
    # Sidebar
    with st.sidebar:
        # Language selector
        selected_language = render_language_selector(language)
        if selected_language != language:
            st.session_state.language = selected_language
            st.rerun()
        
        # Theme toggle
        selected_theme = render_theme_toggle()
        if selected_theme != theme:
            st.session_state.theme = selected_theme
            st.rerun()
        
        st.markdown("---")
        
        # LLM provider toggle
        preferred_provider = render_llm_toggle()
        
        st.markdown("---")
        
        # Candidate info
        if st.session_state.state_manager.data.candidate_info:
            render_candidate_info_sidebar(
                st.session_state.state_manager.data.candidate_info.to_dict(),
                language
            )
        
        st.markdown("---")
        
        # Sentiment sidebar
        render_sentiment_sidebar(st.session_state.sentiment_history, language)
        
        st.markdown("---")
        
        # Usage stats
        render_usage_stats(st.session_state.usage_tracker)
        
        st.markdown("---")
        
        # Stats
        st.markdown(f"### {get_translation('sidebar_stats', language)}")
        st.caption(f"Messages: {len(st.session_state.messages)}")
        if st.session_state.state_manager.data.questions:
            answered = sum(1 for q in st.session_state.state_manager.data.questions if q.candidate_response)
            st.caption(f"Questions: {answered}/{len(st.session_state.state_manager.data.questions)}")
    
    # Main chat area
    if not st.session_state.started:
        # Welcome screen
        st.markdown(f"""
        ### {get_translation('welcome_title', language)}
        
        {get_translation('welcome_message', language)}
        
        {get_translation('welcome_steps', language)}
        
        This usually takes about 10-15 minutes. Ready to begin?
        """)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            start_button = st.button(get_translation('start_button', language), use_container_width=True)
            
            if start_button:
                # Initialize LLM
                llm, provider_name, is_fallback, error = initialize_llm(preferred_provider)
                
                if error:
                    st.error(f"⚠️ {error}")
                    st.info(get_translation('error_no_llm', language))
                else:
                    st.session_state.llm = llm
                    st.session_state.llm_provider = provider_name
                    st.session_state.is_fallback = is_fallback
                    st.session_state.state_manager.set_llm_provider(provider_name)
                    
                    # Initialize phase controller
                    st.session_state.phase_controller = PhaseController(
                        llm=llm,
                        state_manager=st.session_state.state_manager
                    )
                    
                    # Generate greeting with personalization
                    greeting = st.session_state.phase_controller._start_greeting()
                    st.session_state.messages.append({"role": "assistant", "content": greeting})
                    st.session_state.started = True
                    st.rerun()
    
    else:
        # Show LLM provider badge
        render_llm_provider_badge(
            st.session_state.llm_provider,
            st.session_state.get("is_fallback", False)
        )
        
        # Show progress
        phases = ["init", "greeting", "info_gathering", "tech_declaration", "questioning", "sentiment_check", "exit"]
        render_progress(
            st.session_state.state_manager.get_current_state().value,
            phases,
            language
        )
        
        # Display chat messages
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Show sentiment badge for user messages (after first few)
                if message["role"] == "user" and i > 1 and i < len(st.session_state.messages) - 1:
                    # Check if we have sentiment data for this message
                    if i // 2 < len(st.session_state.sentiment_history):
                        sentiment_data = st.session_state.sentiment_history[i // 2]
                        render_sentiment_badge_realtime(sentiment_data)
        
        # Check if conversation ended
        current_state = st.session_state.state_manager.get_current_state()
        if current_state == ConversationState.EXIT:
            st.markdown("---")
            st.success(get_translation('screening_complete', language))
            
            # Final sentiment report
            if st.session_state.sentiment_history:
                analyzer = SentimentAnalyzer(st.session_state.llm)
                responses = [
                    st.session_state.messages[i]["content"] 
                    for i in range(1, len(st.session_state.messages), 2)
                    if i < len(st.session_state.messages)
                ]
                final_sentiment = analyzer.get_overall_assessment(responses)
                render_final_sentiment_report(final_sentiment, language)
            
            st.info(get_translation('next_steps', language))
            
            if st.button(get_translation('new_session', language)):
                # Clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
            return
        
        # Chat input
        if prompt := st.chat_input(get_translation('message_placeholder', language)):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process and get response with timing
            start_time = time.time()
            
            with st.chat_message("assistant"):
                # Show typing indicator
                typing_placeholder = st.empty()
                typing_placeholder.markdown("""
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: #4A5568;">🤖 Thinking</span>
                    <span>●●●</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Process input
                response = st.session_state.phase_controller.process_input(prompt)
                
                # Clear typing indicator and show response
                typing_placeholder.empty()
                st.markdown(response)
                
                # Analyze sentiment for user's input
                if st.session_state.llm and prompt:
                    try:
                        analyzer = SentimentAnalyzer(st.session_state.llm)
                        sentiment = analyzer.analyze(prompt)
                        st.session_state.sentiment_history.append(sentiment)
                        render_sentiment_badge_realtime(sentiment)
                    except Exception:
                        pass
                
                # Log usage
                response_time = (time.time() - start_time) * 1000
                st.session_state.usage_tracker.log_request(
                    provider=st.session_state.llm_provider,
                    model="gpt-4o" if "GPT" in st.session_state.llm_provider else "llama3.2",
                    input_tokens=len(prompt.split()),
                    output_tokens=len(response.split()),
                    phase=current_state.value,
                    response_time_ms=response_time
                )
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()


if __name__ == "__main__":
    main()
