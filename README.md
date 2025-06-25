# LLM Auto Code Generation Tool 🐍

A powerful Python code generation tool that leverages Large Language Models (LLMs) to automatically generate, analyze, and improve Python code. The tool integrates static analysis with automated code generation to ensure high-quality, secure, and lint-free Python code.

## Features

- **Multi-LLM Support**: Supports OpenAI GPT models (GPT-4o-mini, GPT-3.5-turbo) and Google Gemini models (Gemini-1.5-flash, Gemini-2.0-flash)
- **Automated Code Generation**: Generate Python code from natural language descriptions
- **Static Analysis Integration**: Automatically runs Pylint and Bandit security analysis on generated code
- **Smart Error Correction**: Automatically attempts to fix detected issues through iterative LLM feedback
- **Web Interface**: User-friendly Streamlit web interface for easy interaction
- **Comprehensive Logging**: Detailed logging for debugging and analysis
- **API Key Management**: Secure handling of OpenAI and Google API keys

## Project Structure

```
llm-auto-codegen/
├── src/                    # Core source code
│   ├── main.py            # Main application logic
│   ├── llm_handler.py     # LLM integration and API handling
│   ├── code_parser.py     # Code extraction from LLM responses
│   └── utils.py           # Utility functions
├── analysis/              # Code analysis modules
│   ├── static_analyzer.py # Pylint and Bandit integration
│   └── dynamic_analyzer.py # Future dynamic analysis (placeholder)
├── dev/streamlit/         # Streamlit web application
│   └── app.py            # Main Streamlit app
├── config/               # Configuration files
│   └── .env             # Environment variables (API keys)
├── tests/               # Test suite
├── app_logs/            # Application logs
└── requirements.txt     # Python dependencies
```

## Prerequisites

- Python 3.8+ 
- Conda (recommended) 
- OpenAI API Key (for GPT models)
- Google API Key (for Gemini models)

## Installation

### Using Conda (Recommended)

1. **Clone the repository**:
```bash
git clone <repository-url>
cd llm-auto-codegen
```

2. **Create a new conda environment**:
```bash
conda create -n llm-codegen python=3.11
conda activate llm-codegen
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```


## Configuration

1. **Set up API Keys**:
Create a `.env` file in the `config/` directory:
```bash
# config/.env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Optional: LangSmith tracking
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT="llm-auto-codegen"
```

2. **Install static analysis tools** (if not already installed):
```bash
pip install pylint bandit
```

## Usage

### Running the Streamlit Web Application

1. **Navigate to the Streamlit app directory**:
```bash
cd dev/streamlit
```

2. **Run the Streamlit application**:
```bash
streamlit run app.py
```

3. **Access the application**:
Open your web browser and go to `http://localhost:8501`


## Features in Detail

### Code Generation
- Input natural language descriptions of desired functionality
- Supports multiple LLM providers (OpenAI GPT, Google Gemini)
- Configurable temperature and token limits
- Automatic code block extraction from LLM responses

### Static Analysis
- **Pylint Integration**: Checks for code quality, style, and potential errors
- **Bandit Security Analysis**: Identifies security vulnerabilities and issues
- **Automated Issue Reporting**: Clear, actionable feedback on detected problems

### Smart Error Correction
- Automatically retries code generation when issues are detected
- Provides detailed feedback to the LLM for iterative improvement
- Configurable retry attempts (default: 3 attempts)

### Web Interface Features
- **Model Selection**: Choose between different LLM models
- **API Key Management**: Secure input and storage of API credentials
- **Real-time Analysis**: Live feedback on code quality and security
- **Process Logging**: Detailed logs of the generation and analysis process
- **Code Export**: Easy copying of generated code

## Development


## API Keys

### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account and navigate to API Keys
3. Generate a new API key
4. Add it to your `.env` file

### Google API Key (for Gemini)
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create a project and enable the Generative AI API
3. Generate an API key
4. Add it to your `.env` file

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [LangChain](https://langchain.com/) for LLM integration
- [Streamlit](https://streamlit.io/) for the web interface
- [Pylint](https://pylint.org/) for code quality analysis
- [Bandit](https://bandit.readthedocs.io/) for security analysis