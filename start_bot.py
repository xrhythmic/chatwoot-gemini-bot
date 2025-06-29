#!/usr/bin/env python3
"""
Quick start script for Chatwoot Gemini Bot.
This script creates a basic config file and starts the bot.
"""

import os
import sys
from pathlib import Path

def create_config():
    """Create a basic config file if it doesn't exist."""
    config_content = """[chatwoot]
account_id = 1
access_key = your_chatwoot_access_token_here
url = https://your-chatwoot-instance.com/

[gemini]
api_key = your_gemini_api_key_here
model = models/gemini-2.5-flash
max_tokens = 1000
temperature = 0.7
system_prompt = You are a helpful customer service assistant. You should be polite, professional, and empathetic. Keep responses concise but informative. Reference previous conversation context when relevant. If you don't know something, be honest and offer alternative help. Maintain conversation continuity by acknowledging what was discussed before. Adapt your tone based on the customer's interaction level.

[service]
host = 0.0.0.0
port = 8000
"""
    
    config_file = Path("bot.config")
    if not config_file.exists():
        config_file.write_text(config_content)
        print(f"Created config file: {config_file}")
        print("Please edit bot.config with your actual credentials before running the bot.")
        return False
    return True

def main():
    """Main function to start the bot."""
    print("🤖 Chatwoot Gemini Agent Bot")
    print("=" * 40)
    
    # Check if config exists, create if not
    if not create_config():
        sys.exit(1)
    
    # Import and start the bot
    try:
        from woothook.service import start
        print("Starting the bot...")
        start("bot.config")
    except ImportError:
        print("Error: Please install the package first:")
        print("pip install -e .")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
    except Exception as e:
        print(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
