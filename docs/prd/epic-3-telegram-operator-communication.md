# Epic 3: Telegram Operator Communication - Brownfield Enhancement

## Epic Goal

Enable remote operator communication via Telegram to support unattended long-running experiments by providing an optional alternative to terminal-based operator tool call responses.

## Epic Description

### Existing System Context

**Current Relevant Functionality:**
- The `send_message_to_operator()` function in `contreact_ollama/tools/operator_communication.py` provides synchronous terminal-based communication
- Function blocks execution using `input()` waiting for operator response
- Operator must be present at the terminal to respond to agent queries
- This limitation interrupts long-running experiments when operator is unavailable

**Technology Stack:**
- Python 3.9+ backend
- Configuration managed via YAML files and `ExperimentConfig` dataclass
- Existing tool dispatcher pattern in `contreact_ollama/tools/tool_dispatcher.py`

**Integration Points:**
- `operator_communication.py` - existing operator communication module
- `config.py` - configuration system for enabling/disabling Telegram
- Configuration YAML files - add Telegram bot credentials and settings
- `cycle_orchestrator.py` - may need awareness of async communication

### Enhancement Details

**What's Being Added:**
1. **Telegram Bot Integration**: Python Telegram Bot library integration for bidirectional communication
2. **Configuration Options**: YAML-based configuration for:
   - Enabling/disabling Telegram mode
   - Telegram bot token
   - Authorized chat/user IDs for security
   - Fallback to terminal if Telegram unavailable
3. **Communication Abstraction**: Refactor `send_message_to_operator()` to route through configurable communication channel

**How It Integrates:**
- Extends existing operator communication without breaking terminal-based mode
- Uses configuration pattern already established in project
- Maintains backward compatibility - terminal remains default
- Security: Only authorized Telegram users can respond to agent

**Success Criteria:**
- Operator can respond to agent queries via Telegram when enabled in config
- Terminal-based communication continues to work when Telegram disabled
- Graceful fallback if Telegram connection fails
- Agent receives responses through either channel transparently
- Long-running experiments can complete without operator at terminal

## Stories

### Story 3.1: Telegram Configuration (Backend & UI)

Add configuration support for Telegram bot credentials and operation mode selection in both YAML files and Streamlit UI.

**Backend Requirements:**
- Extend `ExperimentConfig` or create separate `TelegramConfig` class
- Add YAML schema fields for:
  - `telegram_enabled` (boolean, default: false)
  - `telegram_bot_token` (string, sourced from environment variable)
  - `telegram_authorized_users` (list of integer user IDs)
  - `telegram_timeout_minutes` (minutes before fallback to terminal, default: 5, -1 = wait forever)
- Configuration validation on experiment startup
- Environment variable handling for `TELEGRAM_BOT_TOKEN`

**Streamlit UI Requirements:**
- Add "Telegram Integration" section to `pages/1_🧪_experiment_configuration.py`
- UI elements following existing form pattern:
  - Checkbox: "Enable Telegram Operator Communication" (default: unchecked)
  - Text input: "Bot Token (Environment Variable)" (read-only display, shows if `TELEGRAM_BOT_TOKEN` is set)
  - Text input: "Authorized User IDs" (comma-separated, e.g., "123456789, 987654321")
  - Number input: "Response Timeout (minutes)" (default: 5, range: -1 to 120, -1 = wait forever)
  - Help text explaining how to obtain bot token and user IDs (with link to README section)
  - Help text for timeout explaining -1 means "wait forever" (no timeout)
- Save Telegram settings to YAML config file alongside other experiment parameters
- Load and display Telegram settings when editing existing configuration

**Documentation Requirements:**
- Add README section: "Telegram Integration Setup" covering:
  1. Creating bot via BotFather (step-by-step)
  2. Obtaining bot token and storing in environment variable
  3. Finding your Telegram user ID
  4. Configuring authorized users
  5. Security best practices

### Story 3.2: Telegram Bot Service & README Documentation

Implement Telegram bot service for sending and receiving operator messages, and provide comprehensive setup documentation.

Implement Telegram bot service for sending and receiving operator messages.

**Telegram Service Requirements:**
- Create `contreact_ollama/communication/telegram_service.py` module
- Implement `TelegramOperatorChannel` class:
  - Initialize bot with token from environment variable
  - `send_message()` method to post to authorized users
  - `wait_for_response()` method with configurable timeout
  - Handle connection errors gracefully with fallback to terminal
  - Validate incoming responses are from authorized users only
- Message formatting for clarity:
  - **Agent messages**: Formatted with context (experiment run_id, cycle number)
  - **Operator messages**: Parsed and validated before returning
- Response parsing and validation
- Connection health check before first use
- Unit tests for Telegram service with mocked bot API

**README Documentation Requirements:**
Add new section to `README.md`: **"Telegram Integration for Remote Operator Communication"**

Include the following subsections:

**1. Overview**
- Explain the feature: respond to operator tool calls via Telegram
- Benefits: unattended long-running experiments
- Optional feature: terminal communication still default

**2. Prerequisites**
- Telegram account
- Python environment with `python-telegram-bot` installed

**3. Creating Your Telegram Bot**
Step-by-step instructions:
1. Open Telegram and search for "BotFather"
2. Send `/newbot` command
3. Follow prompts to name your bot (name must end with "bot")
4. Copy the API token provided by BotFather
5. Store token securely (never commit to repository)

**4. Setting Up Environment Variables**
- Create `.env` file (add to `.gitignore`)
- Add line: `TELEGRAM_BOT_TOKEN=your_token_here`
- Alternative: Set system environment variable
- Verification: How to check if token is loaded

**5. Finding Your Telegram User ID**
Methods to obtain user ID:
- Use bot like @userinfobot
- Start conversation with your bot and check logs
- Include code snippet or reference to helper script

**6. Configuring in Streamlit UI**
- Navigate to Experiment Configuration page
- Enable "Telegram Operator Communication"
- Enter your user ID in "Authorized User IDs" field
- Set timeout preference
- Save configuration

**7. Testing Your Setup**
- Run test experiment with Telegram enabled
- Verify bot sends messages when operator input needed
- Confirm responses are received properly
- Troubleshooting common issues

**8. Security Best Practices**
- Never commit bot token to version control
- Use environment variables or secure secret management
- Limit authorized users to trusted individuals
- Regularly rotate bot token if compromised
- Monitor bot activity for unauthorized access attempts

**9. Example Configuration**
Provide sample YAML snippet showing Telegram configuration:
```yaml
run_id: "telegram-test-001"
model_name: "llama3:latest"
cycle_count: 10
telegram_enabled: true
telegram_authorized_users: [123456789]
telegram_timeout_minutes: 5  # or -1 for no timeout
# ... other config fields
```

**10. Fallback Behavior**
- Explain automatic fallback to terminal if Telegram unavailable
- Timeout behavior
- Error handling and user notifications

### Story 3.3: Communication Channel Abstraction & Integration

Refactor operator communication to support multiple channels (terminal, Telegram).

**Key Requirements:**
- Create abstract `OperatorChannel` interface/protocol
- Implement `TerminalChannel` (wraps existing `input()` logic)
- Implement `TelegramChannel` (uses service from Story 3.2)
- Refactor `send_message_to_operator()`:
  - Check config for enabled channel
  - Route to appropriate channel implementation
  - Handle fallback logic (Telegram fails → terminal)
- Update `tool_dispatcher.py` if needed for async awareness
- Integration tests covering both channels
- Update existing tests to ensure backward compatibility

## Compatibility Requirements

- [x] Existing terminal-based operator communication remains unchanged when Telegram disabled
- [x] Configuration schema backward compatible (all Telegram fields optional)
- [x] No changes to `send_message_to_operator()` function signature
- [x] Existing experiments run without modification when Telegram not configured
- [x] Performance impact minimal (only when Telegram enabled)

## Risk Mitigation

**Primary Risk:** Telegram bot connection failure during critical operator query could block experiment indefinitely

**Mitigation:**
- Implement timeout with automatic fallback to terminal
- Connection health check before first use in experiment
- Clear error messages guide operator to terminal if Telegram unavailable
- Configuration validation prevents experiments starting with invalid Telegram setup

**Rollback Plan:**
- Remove or disable Telegram configuration in YAML files
- Existing terminal-based communication continues to work immediately
- No database schema changes to rollback
- New module can be isolated without affecting existing code

## Definition of Done

- [x] All 3 stories completed with acceptance criteria met
- [x] Telegram communication works for operator tool call responses
- [x] Terminal communication verified still working (regression testing)
- [x] Configuration validation prevents invalid Telegram setup
- [x] Unit tests for Telegram service (mocked API)
- [x] Integration tests for both communication channels
- [x] Documentation updated:
  - README section on Telegram setup
  - Configuration reference for Telegram options
  - Security best practices (bot token handling, authorized users)
- [x] No regression in existing operator communication functionality
- [x] Successful end-to-end test of long-running experiment with Telegram responses

## Additional Technical Notes

**Dependencies to Add:**
- `python-telegram-bot` library (latest stable version)
- Environment variable management for secure token storage

**Security Considerations:**
- Bot token must not be committed to repository
- Validate user ID authorization before accepting responses
- Consider end-to-end encryption for sensitive experiments

**Future Enhancement Opportunities:**
- Support for multiple notification services (Discord, Slack)
- Rich message formatting with experiment status
- Proactive notifications for experiment milestones
- Bidirectional file transfer (logs, results)
