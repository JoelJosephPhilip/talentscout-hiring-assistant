# TalentScout Hiring Assistant

An AI-powered recruitment chatbot for technology candidate screening, built with Streamlit and supporting both OpenAI GPT-4o and local Ollama (Llama 3.2) models.

## Features

- **Intelligent Conversation Flow**: State-machine based conversation management
- **Dual LLM Support**: Works with OpenAI GPT-4o or local Ollama (Llama 3.2)
- **Auto-Detection**: Automatically detects available LLM and uses the best option
- **Information Gathering**: Collects 7 essential candidate fields
- **Technical Questions**: Generates 3-5 relevant questions per technology
- **Sentiment Analysis**: Analyzes candidate confidence and engagement
- **Fallback Handling**: Graceful handling of unexpected inputs
- **Modern UI**: Clean Streamlit interface with progress tracking

## Quick Start

### Option 1: Using OpenAI (Cloud)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/talentscout-hiring-assistant.git
cd talentscout-hiring-assistant
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

5. Run the application:
```bash
streamlit run src/app.py
```

### Option 2: Using Ollama (Local - No API Key Required)

1. Install Ollama:
```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows: Download from https://ollama.com/download/windows
```

2. Pull the Llama 3.2 model:
```bash
ollama pull llama3.2
```

3. Start Ollama server:
```bash
ollama serve
```

4. Follow steps 1-3 from Option 1 above

5. Run the application (no API key needed):
```bash
streamlit run src/app.py
```

## Project Structure

```
talentscout-hiring-assistant/
├── src/
│   ├── llm/
│   │   ├── base.py          # BaseLLM abstract class
│   │   ├── gpt4o.py         # OpenAI GPT-4o implementation
│   │   ├── ollama_llm.py    # Ollama/Llama implementation
│   │   └── factory.py       # LLM Factory with auto-detect
│   ├── prompts/
│   │   └── templates.py     # Prompt templates
│   ├── components/
│   │   ├── state_manager.py     # Conversation state management
│   │   ├── phase_controller.py  # Conversation flow logic
│   │   ├── fallback_handler.py  # Input validation & fallbacks
│   │   └── sentiment_analyzer.py# Sentiment analysis
│   ├── ui/
│   │   └── components.py    # Streamlit UI components
│   └── app.py               # Main application
├── tests/
│   ├── test_llm_factory.py
│   ├── test_fallback_handler.py
│   └── test_state_manager.py
├── docs/                    # Documentation files
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── requirements.txt
├── .env.example
└── README.md
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

## Usage

### Starting a Screening Session

1. Open the app in your browser (http://localhost:8501)
2. Click "Start Screening" to begin
3. Answer questions about your background
4. Provide your tech stack
5. Answer technical questions
6. Receive completion confirmation

### Candidate Information Collected

1. Full Name
2. Email Address
3. Phone Number
4. Years of Experience
5. Desired Position
6. Current Location
7. Tech Stack (programming languages, frameworks, tools)

### Technical Questions

- 3-5 questions generated per declared technology
- Difficulty scales with years of experience:
  - 0-2 years: Foundational concepts
  - 3-5 years: Intermediate, practical scenarios
  - 6+ years: Advanced, architecture-level

## Testing

Run all tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set main file: `src/app.py`
5. Add secrets (OPENAI_API_KEY if using OpenAI)
6. Deploy

### Local Production

```bash
streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0
```

## Prompt Engineering

The system uses carefully crafted prompts for each phase:

- **Greeting**: Warm welcome with process overview
- **Info Gathering**: One field at a time, validation
- **Tech Stack**: Confirmation and expansion
- **Question Generation**: Tailored to experience and tech stack
- **Sentiment Analysis**: Confidence and uncertainty detection
- **Exit**: Professional closing with next steps

See `src/prompts/templates.py` for all prompt templates.

## Data Privacy

- No data stored permanently in demo mode
- Session state only (memory)
- GDPR-compliant design
- PII handling documented in `docs/Security.md`

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

## License

MIT License

## Author

TalentScout Hiring Assistant - AI/ML Intern Assignment
