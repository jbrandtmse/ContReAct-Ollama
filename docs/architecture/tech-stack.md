# Tech Stack

### Technology Stack Table

Note: The versions listed below are the minimum required versions. During implementation, newer stable versions may be used.

| Category | Technology | Version | Purpose | Rationale |
|----------|-----------|---------|---------|-----------|
| Backend Language | Python | 3.9+ | Primary language for the entire application. | Required for compatibility with key libraries. |
| Frontend Framework | Streamlit | 1.38.0+ | Framework for building the web-based UI. | Chosen for simplicity in creating data-centric apps. |
| Database | TinyDB | 4.8.0+ | Persistent key-value store for agent memory. | Lightweight, avoiding overhead of a full DB server. |
| API Interaction | ollama | 0.4.0+ | Official Python client for the Ollama platform. | Provides the fundamental interface to local LLMs. |
| Embeddings | sentence-transformers | 3.0.1+ | Generates semantic embeddings for text. | Used for the exploration diversity mechanism. |
| Numerical Ops | numpy / scipy | 1.26.4+ / 1.13.1+ | Numerical computing for vector operations. | Used for efficient calculation of cosine similarity. |
| Data Visualization | Plotly | 5.22.0+ | Library for creating interactive charts. | Enables rich visualizations within Streamlit. |
| Data Manipulation | Pandas | 2.2.2+ | Parses .jsonl files into DataFrames. | Used to structure log data for UI display. |
| Backend Testing | pytest | 8.2.2+ | Testing framework for the Python backend. | Industry standard for Python unit/integration testing. |
| Frontend Testing | pytest-playwright | 0.5.0+ | End-to-end testing for the Streamlit UI. | Allows for testing the UI in a real browser. |
| App Logging | Python logging | (built-in) | Application-level logging (errors, debug info). | Standard Python library for robust application logging. |
