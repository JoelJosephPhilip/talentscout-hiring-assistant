import streamlit as st


def render_header():
    """Render the chat header with branding"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1A365D 0%, #2B6CB0 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    ">
        <h1 style="font-size: 1.75rem; font-weight: 700; margin: 0;">
            TalentScout Hiring Assistant
        </h1>
        <p style="font-size: 0.95rem; opacity: 0.9; margin: 0.5rem 0 0 0;">
            AI-powered candidate screening for technology positions
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_progress(current_phase: str, phases: list):
    """Render progress indicator"""
    phase_names = {
        "init": "Starting",
        "greeting": "Welcome",
        "info_gathering": "Information",
        "tech_declaration": "Tech Stack",
        "questioning": "Questions",
        "sentiment_check": "Analysis",
        "exit": "Complete"
    }
    
    try:
        current_index = phases.index(current_phase)
    except ValueError:
        current_index = 0
    
    progress_pct = (current_index + 1) / len(phases) * 100
    
    st.markdown(f"""
    <div style="
        background-color: #F7FAFC;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    ">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="font-weight: 600; color: #2D3748;">
                Phase: {phase_names.get(current_phase, current_phase)}
            </span>
            <span style="color: #4A5568;">
                {current_index + 1} of {len(phases)}
            </span>
        </div>
        <div style="
            height: 8px;
            background-color: #E2E8F0;
            border-radius: 4px;
            overflow: hidden;
        ">
            <div style="
                height: 100%;
                width: {progress_pct}%;
                background: linear-gradient(90deg, #2B6CB0 0%, #4299E1 100%);
                border-radius: 4px;
                transition: width 0.3s ease;
            "></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_llm_provider_badge(provider: str, is_fallback: bool = False):
    """Render LLM provider indicator badge"""
    if "GPT" in provider or "openai" in provider.lower():
        icon = "☁️"
        bg_color = "#EBF8FF"
        text_color = "#2B6CB0"
        border_color = "#90CDF4"
        tooltip = "Using OpenAI GPT-4o (cloud)"
    else:
        icon = "🖥️"
        bg_color = "#F0FFF4"
        text_color = "#276749"
        border_color = "#9AE6B4"
        tooltip = "Using Ollama Local Model"
    
    fallback_indicator = " (fallback)" if is_fallback else ""
    
    st.markdown(f"""
    <div style="
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 500;
        background-color: {bg_color};
        color: {text_color};
        border: 1px solid {border_color};
        margin-bottom: 1rem;
    " title="{tooltip}">
        {icon} {provider}{fallback_indicator}
    </div>
    """, unsafe_allow_html=True)


def render_sentiment_badge(score: float):
    """Render sentiment/confidence badge"""
    if score >= 0.7:
        label = "Confident"
        bg_color = "#C6F6D5"
        text_color = "#276749"
        icon = "✓"
    elif score >= 0.4:
        label = "Moderate"
        bg_color = "#FEFCBF"
        text_color = "#975A16"
        icon = "~"
    else:
        label = "Uncertain"
        bg_color = "#FED7D7"
        text_color = "#C53030"
        icon = "?"
    
    return f"""
    <span style="
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 500;
        background-color: {bg_color};
        color: {text_color};
    ">
        {icon} {label}
    </span>
    """


def render_llm_toggle():
    """Render LLM provider toggle in sidebar"""
    st.sidebar.markdown("### ⚙️ Settings")
    st.sidebar.markdown("**LLM Provider**")
    
    provider_options = ["Auto-detect", "OpenAI GPT-4o", "Ollama (local)"]
    
    selected = st.sidebar.radio(
        "Select LLM Provider",
        provider_options,
        index=0,
        help="Auto-detect uses OpenAI if API key is valid, otherwise Ollama",
        label_visibility="collapsed"
    )
    
    provider_map = {
        "Auto-detect": "auto",
        "OpenAI GPT-4o": "openai",
        "Ollama (local)": "ollama"
    }
    
    # Show status info
    if selected == "Ollama (local)":
        st.sidebar.caption("🖥️ Running locally - No API costs")
    elif selected == "OpenAI GPT-4o":
        st.sidebar.caption("☁️ Cloud-based - API costs apply")
    else:
        st.sidebar.caption("🔄 Will auto-detect best option")
    
    return provider_map[selected]


def render_candidate_info_sidebar(candidate_info):
    """Render candidate info in sidebar"""
    st.sidebar.markdown("### 📋 Candidate Info")
    
    if not candidate_info:
        st.sidebar.info("No information collected yet.")
        return
    
    fields = [
        ("Name", candidate_info.get("full_name")),
        ("Email", candidate_info.get("email")),
        ("Phone", candidate_info.get("phone")),
        ("Experience", f"{candidate_info.get('years_experience')} years" if candidate_info.get("years_experience") else None),
        ("Position", candidate_info.get("desired_position")),
        ("Location", candidate_info.get("location")),
        ("Tech Stack", ", ".join(candidate_info.get("tech_stack", [])) if candidate_info.get("tech_stack") else None)
    ]
    
    for label, value in fields:
        if value:
            st.sidebar.markdown(f"**{label}:** {value}")


def render_question_progress(current: int, total: int):
    """Render question progress"""
    if total == 0:
        return
    
    st.markdown(f"""
    <div style="
        background-color: #F7FAFC;
        border-radius: 8px;
        padding: 0.75rem;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    ">
        <strong>Question {current + 1}</strong> of {total}
    </div>
    """, unsafe_allow_html=True)


def render_typing_indicator():
    """Render a typing indicator"""
    st.markdown("""
    <div style="
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem;
        background-color: #F7FAFC;
        border-radius: 12px;
        width: fit-content;
    ">
        <span style="color: #4A5568;">Assistant is thinking</span>
        <span class="typing-dots">
            <span style="animation: blink 1s infinite;">●</span>
            <span style="animation: blink 1s infinite 0.2s;">●</span>
            <span style="animation: blink 1s infinite 0.4s;">●</span>
        </span>
    </div>
    <style>
        @keyframes blink {
            0%, 50% { opacity: 0; }
            51%, 100% { opacity: 1; }
        }
    </style>
    """, unsafe_allow_html=True)


def get_custom_css():
    """Return custom CSS styles"""
    return """
    <style>
        /* Main app styling */
        .stApp {
            background-color: #F7FAFC;
        }
        
        /* Chat messages */
        .stChatMessage {
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }
        
        /* Bot messages */
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatar"]) {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }
        
        /* User messages */
        [data-testid="stChatMessage"]:not(:has([data-testid="stChatMessageAvatar"])) {
            background-color: #EBF8FF;
            border: 1px solid #BEE3F8;
        }
        
        /* Input styling */
        .stChatInput textarea {
            border-radius: 12px;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }
        
        /* Button styling */
        .stButton button {
            background-color: #2B6CB0;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        
        .stButton button:hover {
            background-color: #1A365D;
            transform: translateY(-1px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
    </style>
    """
