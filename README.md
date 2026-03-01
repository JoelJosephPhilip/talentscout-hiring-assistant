# TalentScout Hiring Assistant

[![Version](https://img.shields.io/badge/version-0.2.1-blue.svg)](https://github.com/JoelJosephPhilip/talentscout-hiring-assistant/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-green.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/tests-67%20passing-brightgreen.svg)](#testing)

An AI-powered recruitment chatbot for technology candidate screening, built with Streamlit and supporting both OpenAI GPT-4o and local Ollama (Llama 3.2) models.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Demo](#demo)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Deployment](#deployment)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Overview

TalentScout Hiring Assistant is an intelligent recruitment chatbot designed to streamline the initial screening process for technology candidates. It leverages Large Language Models (LLMs) to conduct natural, contextual conversations while collecting essential candidate information and assessing technical knowledge.

**Key Highlights:**
- Dual LLM support with automatic fallback
- Multi-language support (7 languages)
- Real-time sentiment analysis
- Comprehensive logging for analytics
- GDPR-compliant design

## Features

### Core Features
- **Intelligent Conversation Flow**: State-machine based conversation management
- **Dual LLM Support**: Works with OpenAI GPT-4o or local Ollama (Llama 3.2)
- **Auto-Detection**: Automatically detects available LLM and uses the best option
- **Information Gathering**: Collects 7 essential candidate fields
- **Technical Questions**: Generates 3-5 relevant questions per technology
- **Sentiment Analysis**: Real-time confidence and engagement tracking
- **Fallback Handling**: Graceful handling of unexpected inputs

### v0.2.1 Features
- **Multilingual Support**: English, Hindi, Spanish, French, German, Chinese, Malayalam
- **Dark Mode**: Full dark theme support with proper contrast
- **Comprehensive Logging**: Session logging for analytics and improvement
- **PII Anonymization**: GDPR-compliant data handling
- **API Usage Tracking**: Real-time token and cost monitoring
- **Response Caching**: Optimized performance for common queries

## Demo

<!-- Add screenshot placeholder -->
> 📸 Screenshots coming soon

**Screenshots:**
- Light mode interface
- Dark mode interface
- Sentiment analysis badges
- Multi-language selector

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip package manager
- (Optional) OpenAI API key for GPT-4o
- (Optional) Ollama for local LLM inference

### Option 1: Using OpenAI (Cloud)

```bash
# 1. Clone the repository
git clone https://github.com/JoelJosephPhilip/talentscout-hiring-assistant.git
cd talentscout-hiring-assistant

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 5. Run the application
streamlit run src/app.py
```

### Option 2: Using Ollama (Local - No API Key Required)

```bash
# 1. Install Ollama
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows: Download from https://ollama.com/download/windows

# 2. Pull the Llama 3.2 model
ollama pull llama3.2

# 3. Start Ollama server
ollama serve

# 4. Clone and setup (follow steps 1-3 from Option 1)

# 5. Run the application (no API key needed)
streamlit run src/app.py
```

### One-Command Setup (Windows)

```bash
run.bat
```

### One-Command Setup (macOS/Linux)

```bash
chmod +x run.sh && ./run.sh
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (optional) | - |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama model name | `llama3.2` |
| `LLM_PREFERRED` | Preferred LLM: `auto`, `openai`, `ollama` | `auto` |

### LLM Selection Priority

When `LLM_PREFERRED=auto` (default):
1. OpenAI GPT-4o if `OPENAI_API_KEY` is valid
2. Ollama/Llama 3.2 if server is running locally
3. Error if neither available

### Streamlit Configuration

Edit `.streamlit/config.toml` for custom settings:

```toml
[theme]
primaryColor = "#2B6CB0"
backgroundColor = "#F7FAFC"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#1A202C"
```

## Usage

### Starting a Screening Session

1. Open the app in your browser (http://localhost:8501)
2. Select your preferred language from the sidebar
3. Choose your preferred LLM provider
4. Click "Start Screening" to begin
5. Answer questions about your background
6. Provide your tech stack
7. Answer technical questions
8. Receive completion confirmation

### Candidate Information Collected

| Field | Description |
|-------|-------------|
| Full Name | Candidate's complete name |
| Email Address | Contact email |
| Phone Number | Contact phone with country code |
| Years of Experience | Total professional experience |
| Desired Position | Target job role |
| Current Location | City/Country |
| Tech Stack | Programming languages, frameworks, tools |

### Technical Questions

- 3-5 questions generated per declared technology
- Difficulty scales with years of experience:
  - **0-2 years**: Foundational concepts
  - **3-5 years**: Intermediate, practical scenarios
  - **6+ years**: Advanced, architecture-level

### Sentiment Analysis

Real-time sentiment tracking includes:
- Confidence score (0.0 - 1.0)
- Engagement level assessment
- Uncertainty phrase detection
- Overall candidate sentiment report

## Project Structure

```
talentscout-hiring-assistant/
├── src/
│   ├── llm/
│   │   ├── base.py              # BaseLLM abstract class
│   │   ├── gpt4o.py             # OpenAI GPT-4o implementation
│   │   ├── ollama_llm.py        # Ollama/Llama implementation
│   │   └── factory.py           # LLM Factory with auto-detect
│   ├── prompts/
│   │   └── templates.py         # Prompt templates
│   ├── components/
│   │   ├── state_manager.py     # Conversation state management
│   │   ├── phase_controller.py  # Conversation flow logic
│   │   ├── fallback_handler.py  # Input validation & fallbacks
│   │   ├── sentiment_analyzer.py# Sentiment analysis
│   │   ├── personalization.py   # Response personalization
│   │   ├── usage_tracker.py     # API usage tracking
│   │   └── cache_manager.py     # Response caching
│   ├── ui/
│   │   └── components.py        # Streamlit UI components
│   ├── i18n/
│   │   └── translations.py      # Multilingual support
│   ├── utils/
│   │   └── logger.py            # Comprehensive logging
│   └── app.py                   # Main application
├── tests/
│   ├── test_llm_factory.py
│   ├── test_fallback_handler.py
│   └── test_state_manager.py
├── logs/                        # Session logs (gitignored)
├── .streamlit/
│   └── config.toml              # Streamlit configuration
├── requirements.txt
├── .env.example
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

### Test Summary

| Module | Tests | Status |
|--------|-------|--------|
| LLM Factory | 12 | ✅ Passing |
| Fallback Handler | 44 | ✅ Passing |
| State Manager | 15 | ✅ Passing |
| **Total** | **71** | **67 passing, 4 skipped** |

## Deployment

### Streamlit Cloud (Recommended)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set main file: `src/app.py`
5. Add secrets (`OPENAI_API_KEY` if using OpenAI)
6. Deploy

### Docker

```dockerfile
# Dockerfile coming soon
```

### Local Production

```bash
streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0
```

## Documentation

| Document | Description |
|----------|-------------|
| [CHANGELOG.md](CHANGELOG.md) | Version history and release notes |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |
| [LICENSE](LICENSE) | MIT License |

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters
- Add docstrings for all public functions
- Write tests for new features

## Data Privacy

- No data stored permanently in demo mode
- Session state only (memory)
- PII anonymization configurable
- GDPR-compliant design
- Comprehensive logging with privacy controls

## Requirements Met

From the assignment requirements:

| Requirement | Status |
|------------|--------|
| Streamlit UI | ✅ |
| Greeting phase | ✅ |
| Information gathering (7 fields) | ✅ |
| Tech stack collection | ✅ |
| Technical questions (3-5 per tech) | ✅ |
| Context handling | ✅ |
| Fallback mechanism | ✅ |
| Exit conversation | ✅ |
| Sentiment analysis (bonus) | ✅ |
| Local LLM fallback (bonus) | ✅ |
| Custom UI styling (bonus) | ✅ |
| Multilingual support (bonus) | ✅ |
| Dark mode (bonus) | ✅ |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for GPT-4o API
- Ollama for local LLM inference
- Streamlit for the amazing framework
- All contributors and testers

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/JoelJosephPhilip">Joel Joseph Philip</a>
</p>

<p align="center">
  <a href="#talentscout-hiring-assistant">Back to Top</a>
</p>
