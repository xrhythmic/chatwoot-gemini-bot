<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Chatwoot Gemini AI Agent Bot

This is a Python-based Chatwoot agent bot powered by Google's Gemini AI. The bot processes incoming Chatwoot webhooks and responds with AI-generated messages.

## Project Structure

- `woothook/service.py` - Main FastAPI application handling webhooks
- `woothook/gemini_ai.py` - Google Gemini AI integration module
- `woothook/utils.py` - Utility functions for configuration and validation
- `start_bot.py` - Entry point script for running the bot
- `example.config` - Configuration template
- `.env.example` - Environment variables template

## Development Guidelines

- Follow Python PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Handle errors gracefully with proper exception handling
- Log important events for debugging and monitoring
- Validate all configuration parameters before use
- Use environment variables for sensitive data like API keys

## Key Features

- Chatwoot webhook integration
- Google Gemini AI for intelligent responses
- Configurable response parameters
- Conversation context management
- Error handling and logging

## Testing

When suggesting code changes:
- Ensure proper error handling for API calls
- Validate webhook payload structure
- Test with different conversation scenarios
- Consider rate limiting and API quotas
