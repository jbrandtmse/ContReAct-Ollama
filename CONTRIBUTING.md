# Contributing to ContReAct-Ollama

Thank you for your interest in contributing to the ContReAct-Ollama Experimental Platform! This document provides guidelines and instructions for contributing to the project.

## 🤝 Ways to Contribute

- **Bug Reports**: Submit detailed bug reports via GitHub Issues
- **Feature Requests**: Propose new features or improvements
- **Code Contributions**: Submit pull requests for bug fixes or new features
- **Documentation**: Improve or expand documentation
- **Testing**: Help test the platform and report issues
- **Research**: Share experimental results and findings

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.9 or higher installed
- Ollama installed and running locally
- Git configured with your name and email
- A GitHub account

### Setting Up Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/ContReAct-Ollama.git
   cd ContReAct-Ollama
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/originalowner/ContReAct-Ollama.git
   ```

4. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

6. **Install pre-commit hooks** (if available):
   ```bash
   pre-commit install
   ```

## 📝 Development Workflow

### Creating a Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications

### Making Changes

1. **Follow the coding standards** defined in [docs/architecture.md](docs/architecture.md#coding-standards)

2. **Write clear, descriptive commit messages**:
   ```
   type(scope): Brief description
   
   Detailed explanation of what changed and why.
   
   Fixes #issue-number
   ```
   
   Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

3. **Add tests** for new functionality:
   - Unit tests in `tests/unit/`
   - Integration tests in `tests/integration/`
   - Aim for >80% code coverage

4. **Update documentation** if needed:
   - Update README.md for user-facing changes
   - Update architecture.md for technical changes
   - Add docstrings to all new functions/classes

### Code Quality Standards

#### Type Hints

All functions must have complete type annotations:

```python
from typing import List, Dict, Optional

def process_data(input_data: List[str], config: Dict[str, Any]) -> Optional[str]:
    """Process input data according to configuration."""
    pass
```

#### Docstrings

Use Google-style docstrings:

```python
def execute_cycle(self, agent_state: AgentState) -> AgentState:
    """
    Execute a single cycle of the ContReAct state machine.
    
    Args:
        agent_state: Current state of the agent including message history
        
    Returns:
        Updated agent state after cycle completion
        
    Raises:
        CycleExecutionError: If cycle execution fails
        
    Example:
        >>> orchestrator = CycleOrchestrator(config)
        >>> new_state = orchestrator.execute_cycle(initial_state)
    """
    pass
```

#### Code Formatting

Run these before committing:

```bash
# Format code
black --line-length 100 contreact_ollama/
isort contreact_ollama/

# Check formatting
black --check --line-length 100 contreact_ollama/

# Type checking
mypy contreact_ollama/

# Linting
flake8 contreact_ollama/
```

### Testing

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=contreact_ollama --cov-report=html

# Run specific test file
pytest tests/unit/test_cycle_orchestrator.py

# Run tests matching pattern
pytest -k "test_similarity"
```

#### Writing Tests

Follow the test naming convention:

```python
def test_<method>_<scenario>_<expected_result>():
    """Test that <method> <expected_result> when <scenario>."""
    # Arrange
    config = create_test_config()
    orchestrator = CycleOrchestrator(config)
    
    # Act
    result = orchestrator.some_method()
    
    # Assert
    assert result == expected_value
```

Use fixtures for common setup:

```python
import pytest

@pytest.fixture
def sample_agent_state():
    """Provide sample AgentState for testing."""
    return AgentState(
        run_id="test-run",
        cycle_number=1,
        model_name="llama3:latest",
        message_history=[],
        reflection_history=[]
    )
```

### Submitting Changes

1. **Ensure all tests pass**:
   ```bash
   pytest
   ```

2. **Ensure code is formatted**:
   ```bash
   black --check contreact_ollama/
   mypy contreact_ollama/
   ```

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat(component): Add new feature"
   ```

4. **Update your branch with upstream changes**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

## 📋 Pull Request Guidelines

### PR Title Format

Use conventional commit format:
```
type(scope): Brief description
```

Examples:
- `feat(tools): Add new memory search tool`
- `fix(orchestrator): Correct state machine transition logic`
- `docs(readme): Update installation instructions`

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Testing
Describe how you tested your changes.

## Checklist
- [ ] My code follows the project's coding standards
- [ ] I have added tests that prove my fix/feature works
- [ ] All tests pass locally
- [ ] I have updated documentation as needed
- [ ] My changes generate no new warnings
- [ ] I have added type hints to all functions
- [ ] I have added docstrings to all public APIs

## Related Issues
Fixes #issue-number
```

### PR Review Process

1. **Automated Checks**: CI/CD will run tests and linting
2. **Code Review**: Maintainers will review your code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, maintainers will merge

## 🐛 Reporting Bugs

### Before Submitting

- Check if the bug has already been reported
- Ensure you're using the latest version
- Verify the bug is reproducible

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Configure experiment with '...'
2. Run command '...'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment:**
- OS: [e.g., Windows 11, macOS 14, Ubuntu 22.04]
- Python version: [e.g., 3.11.4]
- Ollama version: [e.g., 0.1.32]
- Model used: [e.g., llama3:latest]

**Configuration File**
```yaml
# Paste your config.yaml here
```

**Logs**
```
# Paste relevant log output here
```

**Additional context**
Any other information about the problem.
```

## 💡 Requesting Features

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Any alternative solutions or features you've considered.

**Additional context**
Any other context, mockups, or examples.

**Would you be willing to implement this feature?**
- [ ] Yes, I can submit a PR
- [ ] No, but I can help test
- [ ] No, I'm just suggesting the idea
```

## 📚 Documentation Contributions

Documentation is as important as code! You can contribute by:

- Fixing typos or unclear explanations
- Adding examples and tutorials
- Improving API documentation
- Creating guides for common use cases

Documentation files:
- `README.md` - Main project documentation
- `docs/architecture.md` - Technical architecture
- `docs/prd.md` - Product requirements
- Code docstrings - Inline API documentation

## 🎯 Good First Issues

Look for issues labeled `good-first-issue` - these are designed for newcomers to the project.

## 💬 Communication

- **GitHub Issues**: For bugs, features, and technical discussions
- **GitHub Discussions**: For questions, ideas, and general chat
- **Pull Requests**: For code review and implementation discussions

## 📜 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what's best for the community
- Show empathy towards other contributors

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information

## ⚖️ License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

All contributors will be recognized in the project. Significant contributions may result in being added to the CONTRIBUTORS.md file.

## ❓ Questions?

If you have questions about contributing:
1. Check existing documentation
2. Search closed issues
3. Ask in GitHub Discussions
4. Create a new issue with the `question` label

Thank you for contributing to ContReAct-Ollama! 🎉
