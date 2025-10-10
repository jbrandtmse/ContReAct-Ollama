# Technical Assumptions

### Repository Structure: Monorepo
The project will be housed in a single monorepo. This structure is ideal for managing the closely related components—the core Python application, the Streamlit web UI, and the analysis scripts—simplifying dependency management and ensuring consistency across the entire platform.

### Service Architecture: Modular Monolith
[cite_start]The architecture will be a Modular Monolith, as detailed in the Software Design Specification[cite: 378]. [cite_start]This approach provides a clear separation of concerns between the six core components (e.g., `CycleOrchestrator`, `OllamaInterface`, `ToolDispatcher`) within a single, deployable application[cite: 379]. It offers the benefits of modularity without the operational overhead of a distributed microservices architecture.

### Testing Requirements: Unit + Integration Testing
A testing strategy that includes both unit and integration tests is required. [cite_start]Unit tests will be essential for validating the logic of each core component in isolation[cite: 379]. [cite_start]Integration tests will be critical to verify the interactions between components, especially the state machine transitions managed by the `CycleOrchestrator` and the communication with the external Ollama server[cite: 421].

### Additional Technical Assumptions and Requests
* [cite_start]**Core Technology**: The entire application will be built using **Python 3.9 or higher**[cite: 407].
* [cite_start]**UI Framework**: The web front-end will be built exclusively with **Streamlit**[cite: 667].
* [cite_start]**Database**: The agent's memory will use a file-based database, with **TinyDB** preferred for its simplicity[cite: 413, 414].
* [cite_start]**Platform Dependency**: The system is fundamentally dependent on the **Ollama platform** and its specific API for local LLM interaction[cite: 376].
