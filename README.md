# Chatwoot Gemini Agent Bot

A Chatwoot webhook server that integrates with Google's Gemini AI to provide intelligent automated responses to customer messages. Based on [woothook](https://github.com/dearkafka/woothook) and uses the [woot](https://github.com/dearkafka/woot) package for Chatwoot API integration.

This agent bot listens for incoming customer messages in Chatwoot and automatically generates contextual responses using Gemini AI, helping to provide 24/7 customer support with intelligent, human-like responses.

## Features

- 🤖 **Gemini AI Integration**: Powered by Google's Gemini AI for intelligent responses
- 💬 **Automatic Response**: Responds to customer messages automatically
- 📝 **Context Awareness**: Uses conversation history and customer information for better responses
- 🔧 **Configurable**: Easy configuration via config file
- 🐳 **Docker Support**: Ready for containerized deployment
- 🔌 **Webhook Based**: Integrates seamlessly with Chatwoot webhooks

## Install

```bash
pip install git+https://github.com/your-username/chatwoot-agent-bot
```

## Configuration

1. Get a Gemini AI API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set up your Chatwoot webhook:
   - Go to Chatwoot → Settings → Integrations → Webhooks
   - Add a new webhook pointing to your server URL
   - Subscribe to "Message Created" events
3. Copy `example.config` and fill in your details:

```ini
[chatwoot]
account_id = 1
access_key = your_chatwoot_access_token
url = https://your-chatwoot-instance.com/

[gemini]
api_key = your_gemini_api_key_here
model = gemini-pro
max_tokens = 1000
temperature = 0.7

[service]
host = 0.0.0.0
port = 8000
```

## Run

```bash
woothook your_config_file.config
```

## Docker

```bash
docker build -t chatwoot-gemini-bot .
docker run -it -p 8000:8000 chatwoot-gemini-bot "your_config_file.config"
```

## Important Notes

- **Domain Requirements**: Chatwoot requires a proper domain name for webhooks (no localhost or IP addresses)
- **Security**: Consider implementing webhook signature verification for production use
- **Rate Limits**: Be aware of Gemini AI API rate limits and quotas

## Solutions for Local Development

- **ngrok**: Use ngrok to expose your local server with a public domain
- **nginx/traefik**: Configure local DNS and reverse proxy for more secure testing

## Configuration Options

### Gemini Settings

- `model`: Gemini model to use (`gemini-pro`, `gemini-pro-vision`)
- `max_tokens`: Maximum response length (default: 1000)
- `temperature`: Response creativity, 0.0-1.0 (default: 0.7)

## Customization

You can customize the AI behavior by modifying the system prompt in `woothook/gemini_ai.py` or by extending the context-building logic in `woothook/service.py`.