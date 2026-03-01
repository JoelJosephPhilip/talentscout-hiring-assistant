import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from src.llm import LLMFactory
from src.components import StateManager, ConversationState, PhaseController, SentimentAnalyzer
from src.ui.components import (
    render_header,
    render_progress,
    render_llm_provider_badge,
    render_llm_toggle,
    render_candidate_info_sidebar,
    render_question_progress,
    get_custom_css
)


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
    
    # Apply custom CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Sidebar
    with st.sidebar:
        preferred_provider = render_llm_toggle()
        
        st.markdown("---")
        
        # Show candidate info if available
        if st.session_state.state_manager.data.candidate_info:
            render_candidate_info_sidebar(
                st.session_state.state_manager.data.candidate_info.to_dict()
            )
        
        st.markdown("---")
        
        # Show conversation stats
        st.markdown("### 📊 Stats")
        st.caption(f"Messages: {len(st.session_state.messages)}")
        if st.session_state.state_manager.data.questions:
            answered = sum(1 for q in st.session_state.state_manager.data.questions if q.candidate_response)
            st.caption(f"Questions: {answered}/{len(st.session_state.state_manager.data.questions)}")
    
    # Main chat area
    if not st.session_state.started:
        st.markdown("""
        ### Welcome to TalentScout! 🎯
        
        I'm an AI-powered hiring assistant that will help screen your application for technology positions.
        
        Here's what we'll do:
        1. Collect your basic information
        2. Review your tech stack
        3. Ask some technical questions
        
        This usually takes about 10-15 minutes. Ready to begin?
        """)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Start Screening", use_container_width=True):
                # Initialize LLM
                llm, provider_name, is_fallback, error = initialize_llm(preferred_provider)
                
                if error:
                    st.error(f"⚠️ {error}")
                    st.info("Please set your OPENAI_API_KEY environment variable or start Ollama server.")
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
                    
                    # Generate greeting
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
            phases
        )
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Check if conversation ended
        current_state = st.session_state.state_manager.get_current_state()
        if current_state == ConversationState.EXIT:
            st.markdown("---")
            st.success("✅ Screening complete! Thank you for your time.")
            
            if st.button("🔄 Start New Session"):
                # Clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
            return
        
        # Chat input
        if prompt := st.chat_input("Type your message..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process and get response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.phase_controller.process_input(prompt)
                    st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()


if __name__ == "__main__":
    main()
