import streamlit as st
import time
from typing import Dict, List, Optional


def render_header(language: str = "en"):
    """Render the chat header with branding"""
    from src.i18n import get_translation
    
    title = get_translation("welcome_title", language)
    subtitle = get_translation("welcome_message", language)
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1A365D 0%, #2B6CB0 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    ">
        <h1 style="font-size: 1.75rem; font-weight: 700; margin: 0;">
            🎯 TalentScout Hiring Assistant
        </h1>
        <p style="font-size: 0.95rem; opacity: 0.9; margin: 0.5rem 0 0 0;">
            {subtitle}
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_progress(current_phase: str, phases: list, language: str = "en"):
    """Render progress indicator with animation"""
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
    <div class="progress-container" style="
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
            <div class="progress-fill" style="
                height: 100%;
                width: {progress_pct}%;
                background: linear-gradient(90deg, #2B6CB0 0%, #4299E1 100%);
                border-radius: 4px;
                transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
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
        animation: fadeIn 0.3s ease-out;
    " title="{tooltip}">
        {icon} {provider}{fallback_indicator}
    </div>
    """, unsafe_allow_html=True)


def render_sentiment_badge_realtime(sentiment_data: dict):
    """Render sentiment badge with animation after each candidate response"""
    score = sentiment_data.get("confidence_score", 0.5)
    sentiment = sentiment_data.get("sentiment", "neutral")
    enthusiasm = sentiment_data.get("enthusiasm", "medium")
    
    if score >= 0.7:
        emoji = "😊"
        label = "Confident"
        bg_color = "#C6F6D5"
        text_color = "#276749"
        animation = "pulse"
    elif score >= 0.4:
        emoji = "😐"
        label = "Moderate"
        bg_color = "#FEFCBF"
        text_color = "#975A16"
        animation = "fadeIn"
    else:
        emoji = "😟"
        label = "Uncertain"
        bg_color = "#FED7D7"
        text_color = "#C53030"
        animation = "fadeIn"
    
    st.markdown(f"""
    <div class="sentiment-badge sentiment-{animation}" style="
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        background-color: {bg_color};
        color: {text_color};
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    ">
        {emoji} {label} <span style="opacity: 0.7; font-size: 0.8rem;">(Score: {score:.2f})</span>
    </div>
    """, unsafe_allow_html=True)


def render_sentiment_sidebar(sentiment_history: list, language: str = "en"):
    """Render running sentiment summary in sidebar"""
    from src.i18n import get_translation
    
    st.sidebar.markdown(f"### {get_translation('sidebar_sentiment', language)}")
    
    if not sentiment_history:
        st.sidebar.info("No responses analyzed yet.")
        return
    
    # Calculate averages
    avg_confidence = sum(s.get("confidence_score", 0.5) for s in sentiment_history) / len(sentiment_history)
    
    # Sentiment distribution
    sentiments = [s.get("sentiment", "neutral") for s in sentiment_history]
    positive_pct = sentiments.count("positive") / len(sentiments) * 100
    neutral_pct = sentiments.count("neutral") / len(sentiments) * 100
    negative_pct = sentiments.count("negative") / len(sentiments) * 100
    
    # Display metrics
    st.sidebar.metric(
        get_translation("sentiment_overall", language),
        f"{avg_confidence:.0%}"
    )
    
    # Mini sentiment chart
    st.sidebar.markdown(f"""
    <div style="display: flex; gap: 2px; height: 20px; border-radius: 4px; overflow: hidden; margin-top: 0.5rem;">
        <div style="width: {positive_pct:.1f}%; background: #48BB78;" title="Positive: {positive_pct:.1f}%"></div>
        <div style="width: {neutral_pct:.1f}%; background: #ECC94B;" title="Neutral: {neutral_pct:.1f}%"></div>
        <div style="width: {negative_pct:.1f}%; background: #F56565;" title="Negative: {negative_pct:.1f}%"></div>
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; margin-top: 4px; color: #4A5568;">
        <span>😊 {positive_pct:.0f}%</span>
        <span>😐 {neutral_pct:.0f}%</span>
        <span>😟 {negative_pct:.0f}%</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.caption(f"📈 {len(sentiment_history)} {get_translation('sentiment_responses', language).lower()}")


def render_final_sentiment_report(sentiment_data: dict, language: str = "en"):
    """Render comprehensive sentiment report at conversation end"""
    from src.i18n import get_translation
    
    st.markdown("---")
    st.markdown(f"### 📊 Candidate Sentiment Report")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Overall Confidence",
            f"{sentiment_data.get('overall_confidence', 0.5):.0%}"
        )
    
    with col2:
        sentiment = sentiment_data.get('overall_sentiment', 'neutral')
        emoji_map = {"positive": "😊", "neutral": "😐", "negative": "😟"}
        st.metric(
            "Overall Sentiment",
            f"{emoji_map.get(sentiment, '😐')} {sentiment.title()}"
        )
    
    with col3:
        st.metric(
            get_translation("sentiment_responses", language),
            sentiment_data.get('response_count', 0)
        )
    
    # Uncertainty indicators
    uncertainty = sentiment_data.get('uncertainty_phrases', [])
    if uncertainty:
        with st.expander(f"⚠️ Uncertainty Indicators ({len(uncertainty)})"):
            for phrase in set(uncertainty):
                st.caption(f"• \"{phrase}\"")
    
    # Assessment summary
    st.info(f"📋 {sentiment_data.get('assessment_summary', 'Analysis complete.')}")


def render_usage_stats(usage_tracker):
    """Render API usage statistics in sidebar"""
    summary = usage_tracker.get_summary()
    
    st.sidebar.markdown("### 📡 API Usage")
    
    # Total requests
    st.sidebar.metric("Total Requests", summary["total_requests"])
    
    # Tokens used
    st.sidebar.metric("Tokens Used", f"{summary['total_tokens']:,}")
    
    # Estimated cost
    if summary["total_cost"] > 0:
        st.sidebar.metric("Est. Cost", f"${summary['total_cost']:.4f}")
    
    # Provider breakdown
    if summary["requests_by_provider"]:
        st.sidebar.caption("By Provider:")
        for provider, count in summary["requests_by_provider"].items():
            st.sidebar.caption(f"• {provider}: {count} requests")
    
    # Average response time
    if summary.get("avg_response_time_ms", 0) > 0:
        st.sidebar.caption(f"⚡ Avg Response: {summary['avg_response_time_ms']:.0f}ms")


def render_language_selector(language: str = "en"):
    """Render language selection dropdown"""
    from src.i18n import SUPPORTED_LANGUAGES
    
    st.sidebar.markdown("### 🌐 Language")
    
    # Create reverse mapping
    lang_options = {v: k for k, v in SUPPORTED_LANGUAGES.items()}
    
    selected = st.sidebar.selectbox(
        "Select Language",
        options=list(lang_options.keys()),
        index=list(lang_options.values()).index(language) if language in lang_options.values() else 0,
        label_visibility="collapsed"
    )
    
    return lang_options[selected]


def render_theme_toggle():
    """Render dark/light mode toggle"""
    st.sidebar.markdown("### 🎨 Theme")
    
    theme = st.sidebar.radio(
        "Theme",
        ["☀️ Light", "🌙 Dark"],
        index=0,
        label_visibility="collapsed"
    )
    
    return "dark" if "Dark" in theme else "light"


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


def render_typing_indicator():
    """Render animated typing indicator"""
    st.markdown("""
    <div class="typing-container" style="
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem 1.5rem;
        background: linear-gradient(135deg, #F7FAFC 0%, #EDF2F7 100%);
        border-radius: 18px;
        width: fit-content;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    ">
        <div class="typing-avatar" style="
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, #2B6CB0 0%, #4299E1 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1rem;
        ">🤖</div>
        <div class="typing-content">
            <span style="color: #4A5568; font-size: 0.9rem;">Assistant is thinking</span>
            <div class="typing-dots" style="display: inline-flex; gap: 4px; margin-left: 8px;">
                <span class="dot" style="animation: bounce 1.4s infinite ease-in-out both;">●</span>
                <span class="dot" style="animation: bounce 1.4s infinite ease-in-out 0.16s;">●</span>
                <span class="dot" style="animation: bounce 1.4s infinite ease-in-out 0.32s;">●</span>
            </div>
        </div>
    </div>
    <style>
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
            40% { transform: scale(1); opacity: 1; }
        }
        .dot { font-size: 8px; color: #2B6CB0; }
    </style>
    """, unsafe_allow_html=True)


def render_candidate_info_sidebar(candidate_info, language: str = "en"):
    """Render candidate info in sidebar"""
    from src.i18n import get_translation
    
    st.sidebar.markdown(f"### {get_translation('sidebar_candidate_info', language)}")
    
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


def get_custom_css():
    """Return custom CSS styles with animations"""
    return """
    <style>
    /* Main app styling */
    .stApp {
        background-color: #F7FAFC;
    }
    
    /* Chat messages with animation */
    .stChatMessage {
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        animation: messageFadeIn 0.4s ease-out;
    }
    
    /* Message animations */
    @keyframes messageFadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .sentiment-pulse {
        animation: pulse 0.5s ease-out;
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
    
    /* Progress bar smooth transition */
    .progress-fill {
        transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Sentiment badge animations */
    .sentiment-badge {
        animation: fadeIn 0.3s ease-out;
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 0.75rem;
        border: 1px solid #E2E8F0;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #F7FAFC;
        border-radius: 8px;
    }
    </style>
    """


def get_dark_mode_css():
    """Return dark mode CSS styles"""
    return """
    <style>
    .stApp {
        background-color: #1A202C;
        color: #E2E8F0;
    }
    
    .stChatMessage {
        background-color: #2D3748 !important;
        border-color: #4A5568 !important;
        color: #E2E8F0 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1A202C !important;
        border-right-color: #4A5568 !important;
    }
    
    .stButton button {
        background-color: #4299E1;
        color: white;
    }
    
    .stButton button:hover {
        background-color: #2B6CB0;
    }
    
    .stChatInput textarea {
        background-color: #2D3748;
        color: #E2E8F0;
        border-color: #4A5568;
    }
    
    [data-testid="stMetric"] {
        background-color: #2D3748;
        border-color: #4A5568;
    }
    
    .stMarkdown, .stCaption {
        color: #E2E8F0 !important;
    }
    
    div[data-testid="stVerticalBlock"] > div {
        background-color: transparent !important;
    }
    </style>
    """
