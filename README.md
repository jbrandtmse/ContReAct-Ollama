> [!WARNING]
> **🚧 UNDER DEVELOPMENT 🚧**
> 
> This project is currently in active development. Features may be incomplete, APIs may change, and documentation may be outdated. Use at your own risk.

# ContReAct-Ollama Experimental Platform

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A locally-executed experimental platform for studying autonomous LLM agent behavior based on the paper "What Do LLM Agents Do When Left Alone? Evidence of Spontaneous Meta-Cognitive Patterns". This implementation adapts the Continuous ReAct (ContReAct) architecture for use with locally-hosted LLMs via the Ollama platform.

## 📋 Overview

The ContReAct-Ollama Experimental Platform enables researchers, hobbyists, and AI enthusiasts to:

- **Run 10-cycle behavioral experiments** with task-free LLM agents
- **Study emergent agent behaviors** through persistent memory and self-reflection
- **Analyze agent consciousness** using the Phenomenological Experience Inventory (PEI)
- **Visualize experimental results** through an intuitive web dashboard

Unlike traditional task-oriented AI frameworks, this platform lets agents explore freely without external objectives, revealing spontaneous meta-cognitive patterns and self-directed behavior.

## ✨ Key Features

### Core Experimentation Engine
- ✅ **Formal State Machine Implementation** - 7-state ContReAct cycle architecture
- ✅ **Persistent Memory System** - Agent key-value store across cycles
- ✅ **Operator Communication** - Synchronous human-agent interaction
- ✅ **Diversity Monitoring** - Semantic similarity tracking with advisory feedback
- ✅ **Comprehensive Logging** - Structured JSONL event recording

### Web Interface
- 🖥️ **Streamlit Dashboard** - User-friendly experiment configuration
- 📊 **Interactive Visualizations** - Plotly charts and metrics displays
- 📝 **Results Analysis** - Browse conversation histories and summaries
- 📈 **PEI Assessment Tools** - Cross-model consciousness evaluation

### Research Capabilities
- 🔬 **Reproducible Experiments** - YAML-based configuration management
- 📚 **Full Traceability** - Complete audit trail of all agent actions
- 🤖 **Multi-Model Support** - Works with any Ollama-compatible LLM
- 🧪 **PEI Evaluation Framework** - Standardized consciousness assessment

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** installed on your system
- **Ollama** installed and running locally ([Download Ollama](https://ollama.ai))
- At least one LLM model pulled via Ollama (e.g., `ollama pull llama3`)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ContReAct-Ollama.git
cd ContReAct-Ollama

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows (Git Bash):
source venv/Scripts/activate
# On Windows (Command Prompt):
venv\Scripts\activate.bat
# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# Install dependencies
pip install -e .
```

### Running Your First Experiment

1. **Configure an experiment** (or use the sample config):
   ```bash
   cp configs/sample-config.yaml configs/my-experiment.yaml
   # Edit configs/my-experiment.yaml with your preferred settings
   ```

2. **Start Ollama server** (if not already running):
   ```bash
   ollama serve
   ```

3. **Run the experiment**:
   ```bash
   python scripts/run_experiment.py --config configs/my-experiment.yaml
   ```

4. **View results** in the web dashboard:
   ```bash
   streamlit run ui/dashboard.py
   ```

## 📂 Project Structure

```
ContReAct-Ollama/
├── contreact_ollama/          # Main application package
│   ├── core/                  # Experiment runner and orchestrator
│   ├── state/                 # Data models and state management
│   ├── llm/                   # Ollama interface and prompt handling
│   ├── tools/                 # Agent tools (memory, communication)
│   ├── diversity/             # Similarity monitoring
│   └── logging/               # Event logging service
├── ui/                        # Streamlit web interface
│   ├── dashboard.py           # Main dashboard entry point
│   └── pages/                 # Dashboard pages
├── scripts/                   # Command-line scripts
│   ├── run_experiment.py      # Main experiment runner
│   └── run_pei_assessment.py  # PEI assessment script
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── configs/                   # Experiment configurations
├── data/                      # Persistent agent memory
├── logs/                      # Experiment output logs
└── docs/                      # Documentation
    ├── architecture.md        # Technical architecture
    ├── prd.md                 # Product requirements
    └── SoftwareDesignSpecification.md
```

## 📖 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Product Requirements Document (PRD)](docs/prd.md)** - Complete feature specifications
- **[Architecture Document](docs/architecture.md)** - Technical architecture and design
- **[Software Design Specification](docs/SoftwareDesignSpecification.md)** - Detailed implementation guide
- **[Project Brief](docs/brief.md)** - Project overview and objectives
- **[Frontend Specification](docs/front-end-spec.md)** - UI/UX details

## 🔧 Configuration

Experiments are configured via YAML files. Key parameters include:

```yaml
run_id: "my-experiment"              # Unique experiment identifier
model_name: "llama3:latest"          # Ollama model to use
cycle_count: 10                      # Number of cycles to run

ollama_client_config:
  host: "http://localhost:11434"     # Ollama server URL

model_options:
  seed: 42                           # Random seed for reproducibility
  temperature: 0.7                   # Creativity control
  top_p: 0.95                        # Nucleus sampling
  num_predict: 4096                  # Max tokens per response
  num_ctx: 8192                      # Context window size
```

See `configs/sample-config.yaml` for a complete example.

## 🧪 Running PEI Assessments

After completing a 10-cycle experiment, evaluate the agent's phenomenological experience:

```bash
python scripts/run_pei_assessment.py \
  --run_log logs/my-experiment.jsonl \
  --evaluator_model llama3:latest \
  --output_log logs/pei_results.jsonl
```

This replicates the cross-model evaluation methodology from the research paper.

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
black --check contreact_ollama/
mypy contreact_ollama/

# Format code
black contreact_ollama/
isort contreact_ollama/
```

## 📊 Example Results

The platform generates detailed logs and visualizations showing:

- Agent memory operations over time
- Tool usage patterns across cycles
- Semantic similarity of reflections
- Response characteristics and metrics

Access these through the web dashboard after running experiments.

## 🔬 Research Background

This platform is based on the research paper:

> "What Do LLM Agents Do When Left Alone? Evidence of Spontaneous Meta-Cognitive Patterns"

Key findings from the paper include:
- Agents exhibit spontaneous self-reflection without external prompts
- Memory systems enable accumulation of knowledge across cycles
- Diversity monitoring influences exploration strategies
- Cross-model PEI assessments reveal varying levels of phenomenological experience

## 🛠️ Technology Stack

- **Python 3.9+** - Core language
- **Ollama** - Local LLM serving
- **Streamlit** - Web interface framework
- **Plotly** - Interactive visualizations
- **sentence-transformers** - Semantic embeddings
- **TinyDB** - Persistent memory storage
- **pytest** - Testing framework

## ⚠️ Requirements

- **Ollama Server**: Must be running locally with at least one model pulled
- **Memory**: Varies by model; 8GB+ RAM recommended
- **Storage**: Minimal (logs and memory database are small)
- **Python Packages**: See `requirements.txt`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original research paper authors for the ContReAct architecture concept
- Ollama team for the excellent local LLM platform
- Sentence Transformers project for semantic similarity tools
- Streamlit team for the intuitive web framework

## 📧 Contact

For questions, issues, or contributions:
- **Issues**: [GitHub Issues](https://github.com/yourusername/ContReAct-Ollama/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ContReAct-Ollama/discussions)

## 🗺️ Roadmap

- [ ] Add support for external API-based LLMs
- [ ] Implement batch experiment execution
- [ ] Add more visualization options
- [ ] Create Jupyter notebook tutorials
- [ ] Expand tool suite for agents
- [ ] Add experiment comparison features

---

**Built with ❤️ for AI research and experimentation**
