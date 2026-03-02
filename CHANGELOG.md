# TalentScout Hiring Assistant - Changelog

All notable changes to this project will be documented in this file.

---

## [Version 0.3.0] - 2026-03-02

### Title: Groq API Integration + Interactive Setup Wizard

### Added

#### Groq API Support (FREE Tier)
- **New File**: `src/llm/groq_llm.py` - Groq LLM implementation class
- OpenAI-compatible API via Groq SDK
- Default model: `llama-3.3-70b-versatile` (best quality)
- Supported models:
  - `llama-3.3-70b-versatile` - Best quality (recommended)
  - `llama-3.1-8b-instant` - Fastest inference
  - `mixtral-8x7b-32768` - Alternative option
  - `gemma2-9b-it` - Lightweight option
- Free tier with generous rate limits
- Very fast inference on specialized hardware (LPUs)
- Green badge styling with lightning icon (⚡)

#### Interactive Setup Wizard
- **New File**: `setup_wizard.py` - First-time setup assistant
- Interactive CLI with 4 options:
  1. Groq API (FREE) - Fast cloud inference
  2. OpenAI GPT-4o (Paid) - Best quality
  3. Ollama (FREE) - Local inference
  4. Auto-detect - Try all options
- Automatic API key validation
- Secure `.env` file creation
- User-friendly instructions with links to get API keys
- Automatic Ollama installation via winget (Windows) or Homebrew (macOS)

#### Enhanced Launch Scripts
- **Updated**: `run.bat`
  - Automatic first-time setup detection
  - Runs `setup_wizard.py` if no configuration found
  - Creates virtual environment automatically
  - Installs dependencies automatically
  - Error handling and status messages
- **Updated**: `run.sh`
  - Same enhancements for macOS/Linux
  - Homebrew support for Ollama installation

#### Cloud Deployment Support
- API key input in sidebar for Streamlit Cloud
- Session-based key storage (secure, not persisted)
- No permanent storage of keys in cloud
- User-friendly instructions with links
- `render_api_key_input()` function for dynamic key entry

### Changed

- **Updated**: `src/llm/factory.py`
  - Added Groq provider support
  - Changed auto-detect priority: `Groq -> OpenAI -> Ollama`
  - Added `_create_groq()` method
  - Added `_validate_groq_key()` method
  - Updated `get_available_providers()` to include Groq

- **Updated**: `src/llm/__init__.py`
  - Export `GroqLLM` class

- **Updated**: `src/ui/components.py`
  - Added "Groq (Free/Fast)" provider option
  - Added green badge styling for Groq provider
  - Added `render_api_key_input()` function
  - Updated provider descriptions and help text

- **Updated**: `src/app.py`
  - Integrated cloud API key input in sidebar
  - Import `render_api_key_input` function

- **Updated**: `.env.example`
  - Added Groq configuration section
  - Added detailed comments for each option
  - Added model selection options
  - Added installation instructions

### Priority Order for Auto-Detect

```
1. Groq (GROQ_API_KEY) -> FREE, Fast
2. OpenAI (OPENAI_API_KEY) -> PAID, Quality  
3. Ollama (localhost:11434) -> FREE, Local
```

### User Experience Flow

#### First-Time Setup (Desktop)
```
1. User runs run.bat or run.sh
2. Setup wizard launches automatically
3. User selects option (1-4)
4. If API option: Enter key -> Validate -> Save to .env
5. If Ollama: winget installs Ollama -> pulls llama3.2
6. Application starts at localhost:8501
```

#### Cloud Deployment (Streamlit Cloud)
```
1. App loads in browser
2. No API key detected
3. Sidebar shows API key input
4. User enters Groq or OpenAI key
5. Key stored in session (not persisted)
6. App functions normally
```

### Requirements
- No new dependencies required (uses existing OpenAI SDK)

---

## [Version 0.2.1] - 2026-03-01

### Fixed
#### Dark Theme Optimization
- Fixed text contrast issues in dark mode (text was unreadable on dark backgrounds)
- Fixed header gradient colors to work properly in dark mode
- Fixed progress container background colors
- Fixed chat input textarea styling in dark mode
- Fixed chat message bubble backgrounds and text colors
- Fixed sidebar styling (background, borders, text colors)
- Fixed metric cards styling in dark mode
- Fixed radio buttons and selectbox styling
- Fixed expanders styling in dark mode
- Fixed info/warning/success boxes styling
- Fixed sentiment badges and LLM provider badges in dark mode
- Added comprehensive CSS selectors targeting Streamlit's data-testid attributes
- Ensured all text elements have proper contrast (#E2E8F0 or lighter)

### Added
#### Comprehensive Logging System
- `src/utils/logger.py` - Full-featured logging module
- `SessionLogger` class for tracking complete conversation sessions
- `LogManager` class for managing multiple sessions and analysis
- `LogConfig` dataclass for configurable logging behavior
- Configurable PII handling (anonymized by default for GDPR compliance)

#### Log Structure
```
logs/
├── sessions/          # Individual session logs (JSON)
│   └── session_20260301_143022_a1b2c3.json
├── daily/             # Daily aggregated summaries
│   └── 2026-03-01.json
└── errors/            # Error-specific logs
    └── errors_2026-03-01.json
```

#### Session Log Contents
Each session log captures:
- **Session metadata**: ID, timestamps, configuration
- **Candidate info**: Name, email, position, experience (anonymized)
- **Conversation turns**: Full dialogue with:
  - User input and LLM response
  - Phase information
  - Response time (ms)
  - Token usage
  - Sentiment analysis per turn
  - Prompt template used
  - Fallback triggers
  - Cache hit status
- **UI events**: Theme changes, language changes, session start/end
- **Errors**: Type, message, stack trace, context
- **Metrics**: Duration, turns, avg response time, sentiment trend, cache hits
- **Assessment**: Overall sentiment, confidence score, uncertainty phrases

#### Log Use Cases
| Goal | How to Use Logs |
|------|-----------------|
| Debug UI issues | Check `ui_events` for theme/language changes |
| Fix conversation bugs | Analyze conversation turns by phase |
| Improve prompts | Review `prompt_template_used` + responses |
| Train models | Extract conversation patterns from sessions |
| Analyze sentiment trends | Use `sentiment_trend` array |
| Performance tuning | Check `response_time_ms`, `cache_hits` |
| Error tracking | Review `errors/` directory |

#### Configuration
Logging is configurable via `LogConfig`:
```python
LogConfig(
    include_pii=False,        # Anonymize PII (GDPR compliant)
    log_to_console=True,      # Print logs to console
    log_llm_responses=True,   # Log LLM responses
    log_sentiment=True,       # Log sentiment analysis
    log_ui_events=True,       # Log UI interactions
    log_performance=True      # Log performance metrics
)
```

### Changed
- Updated `src/app.py` to integrate logging throughout the conversation flow
- Enhanced error handling with structured error logging
- Added logging for UI events (theme change, language change, session start/end)
- Updated imports to include new logging utilities

---

## [Version 0.2] - 2026-03-01

### Added

#### Multilingual Support (7 Languages)
- Language selector dropdown in sidebar
- Support for: English, Hindi, Spanish, French, German, Chinese, Malayalam
- Language-specific prompt templates
- Auto-detect candidate language and respond in same language

#### Sentiment Analysis Integration
- Real-time sentiment badges after each candidate response
- Sidebar sentiment summary with running confidence score
- Final sentiment report at conversation end
- Confidence trend visualization
- Uncertainty phrase detection and reporting

#### Personalized Responses
- Name-based personalization throughout conversation
- Experience-based tone adjustment (junior/mid/senior)
- Position-based question focusing (frontend/backend/devops)
- Session history for returning candidates

#### UI Enhancements
- Animated typing indicator with dots
- Smooth message fade-in animations
- Dark mode toggle
- API usage statistics display (requests, tokens, cost)
- Enhanced progress indicators
- Improved sidebar layout

#### Performance Optimization
- Response caching for common queries
- Streaming responses for faster perceived speed
- Precomputed common responses
- Request batching for question generation
- LLM call optimization

### Changed
- Updated prompt templates to support language parameter
- Enhanced state manager with sentiment tracking
- Improved phase controller with personalization integration
- Updated UI components with animations

### Dependencies Added
- langdetect>=1.0.9
- plotly>=5.18.0

---

## [Version 0.1] - 2026-03-01

### Added

#### Core LLM Layer
- `BaseLLM` abstract class for model-agnostic LLM integration
- `GPT4oLLM` implementation using OpenAI API
- `OllamaLLM` implementation for local Llama 3.2 inference
- `LLMFactory` with auto-detection and manual override

#### Conversation Management
- State-machine architecture (`StateManager`)
- Phase controller for conversation flow
- Candidate information data model (7 fields)
- Question tracking and response storage

#### Prompt Engineering
- Master system prompt with role definition
- Phase-specific prompt templates
- Technical question generation prompts
- Sentiment analysis prompts
- Fallback and exit prompts

#### Fallback Handling
- Input validation for all field types
- Exit keyword detection
- Hostile content detection
- Invalid input graceful recovery

#### Sentiment Analysis
- Rule-based sentiment detection
- LLM-based sentiment analysis
- Uncertainty phrase extraction
- Overall assessment generation

#### Streamlit UI
- Custom CSS styling
- Progress indicators
- LLM provider badge
- Candidate info sidebar
- Chat interface with message history

#### Testing
- 67 unit tests
- Test coverage for LLM factory
- Test coverage for fallback handler
- Test coverage for state manager

#### Configuration
- Streamlit config.toml with theme settings
- Environment variables template
- Requirements.txt
- Run scripts (run.bat, run.sh)

#### Documentation
- README.md with setup instructions
- Architecture documentation
- Security and GDPR compliance notes

---

## Version Comparison

| Feature | v0.1 | v0.2 | v0.2.1 |
|---------|------|------|--------|
| Dual LLM Support | ✅ | ✅ | ✅ |
| State Machine | ✅ | ✅ | ✅ |
| 7-Field Collection | ✅ | ✅ | ✅ |
| Technical Questions | ✅ | ✅ | ✅ |
| Fallback Handling | ✅ | ✅ | ✅ |
| Multilingual | ❌ | ✅ (7 languages) | ✅ (7 languages) |
| Sentiment Display | ❌ | ✅ (3 modes) | ✅ (3 modes) |
| Personalization | ❌ | ✅ (4 types) | ✅ (4 types) |
| Dark Mode | ❌ | ✅ (glitchy) | ✅ (fixed) |
| API Usage Stats | ❌ | ✅ | ✅ |
| Response Caching | ❌ | ✅ | ✅ |
| Streaming | ❌ | ✅ | ✅ |
| Animations | ❌ | ✅ | ✅ |
| Comprehensive Logging | ❌ | ❌ | ✅ |
| PII Anonymization | ❌ | ❌ | ✅ |
| Error Tracking | ❌ | ❌ | ✅ |

---

## Upcoming Features (Planned)

### Version 0.3 (Future)
- Voice input support
- Resume parsing
- Interview scheduling integration
- Advanced analytics dashboard
- Team collaboration features
