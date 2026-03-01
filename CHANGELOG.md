# TalentScout Hiring Assistant - Changelog

All notable changes to this project will be documented in this file.

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

| Feature | v0.1 | v0.2 |
|---------|------|------|
| Dual LLM Support | ✅ | ✅ |
| State Machine | ✅ | ✅ |
| 7-Field Collection | ✅ | ✅ |
| Technical Questions | ✅ | ✅ |
| Fallback Handling | ✅ | ✅ |
| Multilingual | ❌ | ✅ (7 languages) |
| Sentiment Display | ❌ | ✅ (3 modes) |
| Personalization | ❌ | ✅ (4 types) |
| Dark Mode | ❌ | ✅ |
| API Usage Stats | ❌ | ✅ |
| Response Caching | ❌ | ✅ |
| Streaming | ❌ | ✅ |
| Animations | ❌ | ✅ |

---

## Upcoming Features (Planned)

### Version 0.3 (Future)
- Voice input support
- Resume parsing
- Interview scheduling integration
- Advanced analytics dashboard
- Team collaboration features
