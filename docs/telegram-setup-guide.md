# Telegram Bot Setup Guide for ContReAct-Ollama

This guide will walk you through setting up Telegram bot integration for the ContReAct-Ollama system, starting from a fresh Telegram account.

## Prerequisites

- A Telegram account (mobile or desktop app)
- Access to the ContReAct-Ollama system

## Step 1: Create Your Telegram Bot

### 1.1 Find BotFather

1. Open Telegram on your device
2. In the search bar, type: `@BotFather`
3. Select the official **BotFather** bot (it will have a verified checkmark)
4. Click **Start** or send `/start`

### 1.2 Create a New Bot

1. Send the command: `/newbot`
2. BotFather will ask for a **display name**:
   - This is what users see in their chat list
   - Example: "ContReAct Assistant" or "Experiment Monitor"
   - You can change this later
3. Next, provide a **username** for your bot:
   - Must be unique across all Telegram
   - Must end with "bot"
   - Examples: `ContReAct_Monitor_bot` or `MyExperimentBot`
   - **Important**: This is harder to change later, so choose carefully

### 1.3 Receive Your Bot Token

After creating the bot, BotFather will display your **API token**. It looks like:
```
270485614:AAHfiqksKZ8WmR2zSjiQ7_v4TMAKdiHm9T0
```

**⚠️ SECURITY WARNING**: Treat this token like a password! Anyone with this token can control your bot.

- Copy this token immediately
- Do NOT share it publicly
- Do NOT commit it to code repositories
- Store it securely (we'll use environment variables)

## Step 2: Find Your Telegram User ID

Your system needs to know which Telegram users are authorized to interact with the bot during experiments.

### 2.1 Get Your Numeric User ID

1. In Telegram search bar, type: `@userinfobot`
2. Select the bot and click **Start**
3. The bot will automatically reply with your information, including your numeric **user ID**
4. Copy the numeric ID (e.g., `123456789`)

### 2.2 Get Additional User IDs (Optional)

If you want to authorize additional users (colleagues, team members):
- Have them follow the same process with @userinfobot
- Collect their numeric user IDs
- You'll add all authorized IDs to the configuration

## Step 3: Configure Environment Variables

Create a `.env` file in your project root directory to securely store your bot token.

### 3.1 Create .env File

**On Windows (PowerShell):**
```powershell
echo "TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE" > .env
```

**On Windows (Command Prompt):**
```cmd
echo TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE > .env
```

**On Linux/macOS:**
```bash
echo "TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE" > .env
```

Replace `YOUR_TOKEN_HERE` with the actual token from BotFather.

### 3.2 Add .env to .gitignore

**CRITICAL**: Ensure `.env` is in your `.gitignore` file to prevent accidentally committing your token:

```bash
# Check if .env is already in .gitignore
cat .gitignore | grep ".env"

# If not present, add it
echo ".env" >> .gitignore
```

## Step 4: Configure Your Experiment

Create or modify your experiment configuration YAML file to enable Telegram communication.

### 4.1 Sample Configuration

Create a file in `configs/` directory (e.g., `configs/telegram-experiment.yaml`):

```yaml
# Basic experiment settings
run_id: "telegram-test-001"
model_name: "llama3.2:latest"
cycle_count: 3

# Ollama settings
ollama_client_config:
  host: "http://localhost:11434"

# Model parameters
model_options:
  temperature: 0.7
  top_p: 0.9
  top_k: 40

# Telegram configuration
telegram_enabled: true
telegram_authorized_users:
  - 123456789  # Replace with YOUR user ID from @userinfobot
  # - 987654321  # Add more authorized users if needed
telegram_timeout_minutes: 10  # How long to wait for operator response
```

### 4.2 Configuration Fields Explained

- **telegram_enabled**: Set to `true` to use Telegram, `false` for terminal only
- **telegram_authorized_users**: List of numeric user IDs who can respond to the bot
  - Only users in this list can interact with the bot during experiments
  - Add multiple IDs if you want team members to be able to respond
- **telegram_timeout_minutes**: Maximum wait time for operator response
  - Set to `-1` to wait indefinitely
  - Recommended: 5-15 minutes for active monitoring

## Step 5: Test Your Configuration

### 5.1 Verify Environment Variable

**Windows (PowerShell):**
```powershell
$env:TELEGRAM_BOT_TOKEN
```

**Linux/macOS:**
```bash
echo $TELEGRAM_BOT_TOKEN
```

If this doesn't show your token, you need to load the .env file (Python script does this automatically).

### 5.2 Start a Test Experiment

```bash
python scripts/run_experiment.py configs/telegram-experiment.yaml
```

### 5.3 Interact via Telegram

1. Open Telegram
2. Search for your bot by its username (e.g., `@MyExperimentBot`)
3. Click **Start** to begin a conversation
4. Wait for the experiment to trigger operator communication
5. You should receive a message from your bot with experiment context
6. Reply to the bot - your response will be sent back to the running experiment

## Step 6: Understanding the System Behavior

### Automatic Fallback

The system includes automatic fallback protection:
- If Telegram connection fails → automatically switches to terminal
- If timeout is reached → automatically switches to terminal
- If bot token is invalid → automatically switches to terminal

You'll see log messages indicating when fallback occurs.

### Message Format

When the bot contacts you during an experiment, messages include context:

```
🤖 Agent Message (Run: telegram-test-001, Cycle: 2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Should I continue with the current approach or try a different strategy?
```

### Authorization

Only users listed in `telegram_authorized_users` can interact with the bot. If an unauthorized user tries to send messages, they will be ignored.

## Troubleshooting

### Issue: Bot doesn't respond

**Check:**
1. Is `TELEGRAM_BOT_TOKEN` environment variable set correctly?
2. Is the token valid? (Try `/token` command in BotFather to verify)
3. Is your user ID in the `telegram_authorized_users` list?
4. Did you click **Start** on the bot before the experiment began?

**Test Connection:**
```python
# Quick test script
from contreact_ollama.communication.telegram_service import TelegramOperatorChannel

channel = TelegramOperatorChannel([123456789], 5)
print("Connection successful!" if channel.check_connection() else "Connection failed!")
```

### Issue: "TELEGRAM_BOT_TOKEN environment variable is required"

The `.env` file isn't being loaded or doesn't exist.

**Fix:**
1. Verify `.env` file exists in project root
2. Verify it contains: `TELEGRAM_BOT_TOKEN=your_token_here`
3. Restart your terminal/IDE to reload environment

### Issue: Messages not reaching me

**Check:**
1. Open your bot in Telegram and click **Start**
2. Verify your user ID is correct (use @userinfobot again)
3. Check if you have notifications enabled for the bot

### Issue: Experiment falls back to terminal

Check the log output for specific error messages:
- `ConnectionError` → Bot token invalid or bot unreachable
- `TimeoutError` → No response received within timeout period
- Fallback is automatic and safe - the experiment continues in terminal mode

## Security Best Practices

1. **Never commit** `.env` file to version control
2. **Rotate tokens** periodically using BotFather's `/token` command
3. **Limit authorized users** to only those who need access
4. **Monitor bot activity** through BotFather's analytics
5. **Use specific user IDs** rather than allowing all users

## Advanced Configuration

### Multiple Bots for Different Experiments

You can create multiple bots for different purposes:
1. Create additional bots via BotFather
2. Store tokens with descriptive names: `TELEGRAM_BOT_TOKEN_PRODUCTION`, `TELEGRAM_BOT_TOKEN_DEV`
3. Use different config files for each environment

### Integration with CI/CD

For automated testing:
```yaml
telegram_enabled: false  # Disable for CI/CD pipelines
```

Or use a dedicated testing bot with test user IDs.

## Next Steps

- **Customize bot profile**: Use BotFather's `/mybots` → select your bot → **Edit Bot** to set profile picture, description, and commands
- **Test thoroughly**: Run short experiments to ensure messages flow correctly
- **Document for team**: Share authorized user IDs with team members
- **Monitor usage**: Check bot analytics in BotFather periodically

## Support

If you encounter issues:
1. Check the logs in `logs/[run_id].jsonl` for detailed error messages
2. Verify all configuration fields match the examples above
3. Test bot connection independently before running full experiments
4. Consult Story 3.2 (telegram-bot-service) and Story 3.3 (channel-abstraction) documentation

---

**Configuration Template Reference**: `configs/sample-config.yaml`
**Related Documentation**: 
- Story 3.1: Telegram Configuration
- Story 3.2: Telegram Bot Service  
- Story 3.3: Communication Channel Abstraction
