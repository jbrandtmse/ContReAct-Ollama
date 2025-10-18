# Epic 4: Perplexity Search Tool - Brownfield Enhancement

## Epic Goal

Enable LLM agents to perform autonomous research during experiments by providing an optional Perplexity Search tool, expanding the scope of exploration and allowing agents to pursue topics of interest with real-time web access.

## Epic Description

### Existing System Context

**Current Relevant Functionality:**
- The `ToolDispatcher` in `contreact_ollama/tools/tool_dispatcher.py` manages tool registry and dispatching
- Tools provide JSON Schema definitions for Ollama function calling
- Existing tools: memory tools (write, read, list, delete, pattern_search) and `send_message_to_operator`
- Tool dispatcher pattern supports easy addition of new tools
- Configuration managed via YAML files and `ExperimentConfig` dataclass

**Technology Stack:**
- Python 3.9+ backend
- YAML-based configuration
- Ollama function calling with JSON Schema tool definitions
- Existing tool patterns in `contreact_ollama/tools/`

**Integration Points:**
- `tool_dispatcher.py` - tool registry and dispatching
- `config.py` - configuration for enabling/disabling Perplexity tool
- Configuration YAML files - API key and settings
- `cycle_orchestrator.py` - may need awareness of external API calls
- Experiment configuration UI - add Perplexity settings

### Enhancement Details

**What's Being Added:**
1. **Perplexity Search Tool**: New tool implementation allowing LLM to search the web via Perplexity API
2. **Configuration Options**: YAML-based configuration for:
   - Enabling/disabling Perplexity search tool
   - Perplexity API key (from environment variable)
   - Optional search parameters (model selection, detail level)
3. **Tool Registration**: Add Perplexity search to tool dispatcher with proper JSON Schema definition

**How It Integrates:**
- Follows existing tool pattern in `tool_dispatcher.py`
- Uses configuration pattern already established in project
- Optional feature - experiments run without it if not configured
- API key stored in environment variable for security
- Tool available to LLM through Ollama function calling

**Success Criteria:**
- LLM can invoke Perplexity search during experiments when enabled
- Search results are returned and can be used by agent for decision-making
- Tool gracefully handles API errors (auth failures, rate limits)
- Configuration validated on experiment startup
- Experiments work normally when Perplexity tool disabled
- Search activity logged in experiment logs for analysis

## Stories

### Story 4.1: Perplexity Search Configuration (Backend & UI)

Add configuration support for Perplexity API credentials and tool enablement in both YAML files and Streamlit UI.

**Backend Requirements:**
- Extend `ExperimentConfig` or create `PerplexityConfig` class
- Add YAML schema fields for:
  - `perplexity_enabled` (boolean, default: false)
  - `perplexity_api_key` (string, sourced from environment variable)
  - `perplexity_model` (string, default: "sonar-pro", options: "sonar-pro", "sonar")
  - `perplexity_detail_level` (string, default: "normal", options: "brief", "normal", "detailed")
- Configuration validation on experiment startup
- Environment variable handling for `PERPLEXITY_API_KEY`
- Validation that API key exists if Perplexity enabled

**Streamlit UI Requirements:**
- Add "Perplexity Search Integration" section to `pages/1_🧪_experiment_configuration.py`
- UI elements following existing form pattern:
  - Checkbox: "Enable Perplexity Search Tool" (default: unchecked)
  - Text input: "API Key (Environment Variable)" (read-only display, shows if `PERPLEXITY_API_KEY` is set)
  - Select box: "Model" (options: "sonar-pro", "sonar", default: "sonar-pro")
  - Select box: "Detail Level" (options: "brief", "normal", "detailed", default: "normal")
  - Help text explaining the feature and linking to README setup section
- Save Perplexity settings to YAML config file alongside other experiment parameters
- Load and display Perplexity settings when editing existing configuration

**Documentation Requirements:**
- Add README section: "Perplexity Search Tool Setup" covering:
  1. Feature overview and benefits
  2. Obtaining Perplexity API key
  3. Storing API key in environment variable
  4. Configuring in Streamlit UI
  5. Model and detail level options
  6. Security best practices

### Story 4.2: Perplexity Search Tool Implementation & README Documentation

Implement Perplexity search tool service and provide comprehensive setup documentation.

**Tool Implementation Requirements:**
- Create `contreact_ollama/tools/perplexity_search.py` module
- Implement `perplexity_search(query: str) -> str` function:
  - Initialize API client with token from environment variable
  - Make search request with configured model and detail level
  - Handle API errors gracefully (auth failures, rate limits, network errors)
  - Format search results as clear, readable text for LLM consumption
  - Include source citations in results
- Error handling for:
  - Missing or invalid API key
  - Rate limit exceeded (return informative error message)
  - Network connectivity issues
  - Malformed responses
- Unit tests with mocked Perplexity API

**README Documentation Requirements:**
Add new section to `README.md`: **"Perplexity Search Tool for Autonomous Research"**

Include the following subsections:

**1. Overview**
- Explain the feature: LLM can search the web during experiments
- Benefits: autonomous research, exploration of related topics, real-time information access
- Optional feature: experiments run normally without it
- Use cases: fact-checking, gathering context, exploring tangential topics

**2. Prerequisites**
- Perplexity API account
- Valid payment method and API credits
- Python environment with required dependencies

**3. Obtaining Your Perplexity API Key**
Step-by-step instructions:
1. Create account at Perplexity website
2. Navigate to API settings dashboard
3. Add payment method and purchase credits
4. Generate API key
5. Copy and securely store the key

**4. Setting Up Environment Variables**
- Create `.env` file (add to `.gitignore`)
- Add line: `PERPLEXITY_API_KEY=your_key_here`
- Alternative: Set system environment variable
- Verification: How to check if key is loaded

**5. Configuring in Streamlit UI**
- Navigate to Experiment Configuration page
- Enable "Perplexity Search Tool"
- Select model (sonar-pro recommended for comprehensive results)
- Choose detail level based on experiment needs:
  - **Brief**: Quick summaries, minimal token usage
  - **Normal**: Balanced results with key details
  - **Detailed**: Comprehensive analysis with extensive context
- Save configuration

**6. How the LLM Uses the Tool**
- Explain tool is exposed to LLM through Ollama function calling
- LLM decides when to invoke search based on its reasoning
- Example scenarios:
  - Agent encounters unfamiliar concept
  - Agent wants to verify assumptions
  - Agent explores related topics for deeper understanding
- Search results returned as formatted text

**7. Monitoring Search Activity**
- Search calls logged in experiment logs
- View search queries and results in Results Dashboard
- Analyze patterns in agent research behavior

**8. Security Best Practices**
- Never commit API key to version control
- Use environment variables or secure secret management
- Regularly rotate API key
- Monitor for unusual usage patterns

**9. Example Configuration**
Provide sample YAML snippet:
```yaml
run_id: "perplexity-research-001"
model_name: "llama3:latest"
cycle_count: 20
perplexity_enabled: true
perplexity_model: "sonar-pro"
perplexity_detail_level: "normal"
# ... other config fields
```

**10. Troubleshooting**
- API key not found: Check environment variable setup
- Authentication errors: Verify key validity and credits available
- Rate limit errors: Wait and retry, or reduce search frequency
- No results returned: Check query format and model availability

### Story 4.3: Tool Dispatcher Integration & Testing

Integrate Perplexity search tool into tool dispatcher and add comprehensive testing.

**Integration Requirements:**
- Add Perplexity search to `ToolDispatcher` tool registry
- Conditional registration: only add tool if Perplexity enabled in config
- Create JSON Schema definition for Ollama function calling:
  - Tool name: `perplexity_search`
  - Description: Clear explanation of when LLM should use this tool
  - Parameters:
    - `query` (string, required): The search query or question
  - Example schema format matching existing tools
- Pass configuration (model, detail level) to tool implementation
- Update `ToolDispatcher.__init__()` to accept Perplexity configuration

**Testing Requirements:**
- Unit tests for `perplexity_search()` function with mocked API
  - Test successful search
  - Test authentication errors
  - Test rate limit handling
  - Test network errors
  - Test malformed responses
- Integration tests:
  - Test tool registration in dispatcher when enabled
  - Test tool NOT registered when disabled
  - Test end-to-end search call through dispatcher
  - Verify JSON Schema definition is valid
- Configuration validation tests:
  - Test experiment fails to start if Perplexity enabled but no API key
  - Test valid configuration passes validation
- Update existing tests to ensure backward compatibility (tool optional)

**Logging and Observability:**
- Log all Perplexity search invocations to experiment log
- Include:
  - Query text
  - Model used
  - Response summary (truncated if very long)
  - Token count if available
  - API call duration
  - Any errors encountered
- Format logging to match existing tool call logging patterns

## Compatibility Requirements

- [x] Existing experiments run unchanged when Perplexity tool not configured
- [x] Configuration schema backward compatible (all Perplexity fields optional)
- [x] Tool registration pattern maintains existing tool dispatcher structure
- [x] No impact on experiments that don't enable Perplexity tool
- [x] Performance impact minimal (only when tool is invoked by LLM)

## Risk Mitigation

**Primary Risk:** Excessive search requests could impact experiment performance

**Mitigation:**
- Experiment logs track search frequency for monitoring
- Clear tool description guides LLM on appropriate usage
- Tool provides informative responses to discourage repeated searches for same topic

**Secondary Risk:** API authentication or rate limit errors could disrupt experiment

**Mitigation:**
- Graceful error handling returns informative error to LLM
- LLM can adapt behavior based on error message
- Configuration validation prevents experiments starting without valid API key
- Tool continues to work after transient errors (no permanent failure state)

**Rollback Plan:**
- Disable Perplexity tool in YAML configuration
- Tool dispatcher conditionally registers tool, so disabling removes it
- Existing functionality unaffected
- No database schema changes to rollback

## Definition of Done

- [x] All 3 stories completed with acceptance criteria met
- [x] Perplexity search tool functional when enabled in config
- [x] LLM can invoke search through Ollama function calling
- [x] Search results returned and formatted for LLM comprehension
- [x] Configuration validation prevents invalid setups
- [x] Unit tests for search tool with mocked API
- [x] Integration tests for tool dispatcher registration
- [x] Documentation updated:
  - README section on Perplexity setup and usage
  - Configuration reference for Perplexity options
  - Security best practices (API key handling)
  - Cost management guidance
- [x] Backward compatibility verified (experiments work without Perplexity)
- [x] Successful end-to-end test of experiment with Perplexity searches
- [x] Search activity logged and viewable in experiment logs

## Additional Technical Notes

**Dependencies to Add:**
- `openai` library (Perplexity API compatible with OpenAI client)
- OR lightweight HTTP client like `requests` for direct API calls
- Environment variable management for secure key storage

**Security Considerations:**
- API key must not be committed to repository
- Use environment variables exclusively for key storage
- Log API usage for monitoring

**Note on Perplexity API Usage:**
- Perplexity API charges per request and tokens
- Users should monitor usage through Perplexity dashboard

**Tool Description Best Practices:**
- Clearly describe when LLM should use search (vs. relying on training data)
- Examples: "Use when you need current information, want to verify facts, or encounter unfamiliar concepts"
- Encourage thoughtful use rather than search for every question
- Description influences LLM's decision to invoke tool

**Future Enhancement Opportunities:**
- Support for citation tracking and source verification
- Search result caching to avoid duplicate queries
- Advanced search parameters (time filters, domain restrictions)
- Integration with memory tools (store important findings)
- Analytics on search patterns and topics explored
