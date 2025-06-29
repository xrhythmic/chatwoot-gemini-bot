#!/usr/bin/env python3
"""
Test script to verify Gemini API connectivity and configuration.
Run this script to test your API key and model configuration.
"""

import sys
import asyncio
from pathlib import Path
from woothook.utils import load_config
from woothook.gemini_ai import GeminiAI

async def test_gemini_api():
    """Test the Gemini API connection and configuration."""
    
    print("🧪 Testing Gemini API Configuration")
    print("=" * 40)
    
    # Check if bot.config exists
    config_file = Path("bot.config")
    if not config_file.exists():
        print("❌ Error: bot.config file not found.")
        print("Please copy example.config to bot.config and configure your API key.")
        return False
    
    try:
        # Load configuration
        config = load_config("bot.config")
        print(f"📝 Config loaded successfully")
        print(f"   Model: {config.gemini.model}")
        print(f"   Max tokens: {config.gemini.max_tokens}")
        print(f"   Temperature: {config.gemini.temperature}")
        
        # Show system prompt configuration
        prompt_info = "Default prompt"
        if hasattr(config.gemini, 'system_prompt_file') and config.gemini.system_prompt_file:
            prompt_info = f"File: {config.gemini.system_prompt_file}"
            # Check if file exists
            if not Path(config.gemini.system_prompt_file).exists():
                prompt_info += " (FILE NOT FOUND)"
        elif hasattr(config.gemini, 'system_prompt') and config.gemini.system_prompt:
            prompt_preview = config.gemini.system_prompt[:100] + "..." if len(config.gemini.system_prompt) > 100 else config.gemini.system_prompt
            prompt_info = f"Inline: {prompt_preview}"
        
        print(f"   System prompt: {prompt_info}")
        
        # Check if API key is set
        if config.gemini.api_key == "your_gemini_api_key_here":
            print("❌ Error: Please set your actual Gemini API key in bot.config")
            return False
        
        print(f"   API Key: {config.gemini.api_key[:8]}...")
        
        # Initialize Gemini AI
        print("\n🔌 Testing API connection...")
        gemini = GeminiAI(
            api_key=config.gemini.api_key,
            model=config.gemini.model,
            max_tokens=config.gemini.max_tokens,
            temperature=config.gemini.temperature
        )
        
        # Load custom system prompt from file or inline config
        if hasattr(config.gemini, 'system_prompt_file') and config.gemini.system_prompt_file:
            gemini.load_system_prompt_from_file(config.gemini.system_prompt_file)
        elif hasattr(config.gemini, 'system_prompt') and config.gemini.system_prompt:
            gemini.set_system_prompt(config.gemini.system_prompt)
        
        # Test with a simple message
        test_message = "Hello! This is a test message. Please respond with 'API test successful'."
        print(f"📤 Sending test message...")
        
        # Test basic response
        response = await gemini.generate_response(
            message=test_message,
            context={"test": True}
        )
        
        print(f"📥 Response received:")
        print(f"   {response}")
        
        # Test conversation continuity
        print(f"\n🔄 Testing conversation continuity...")
        conversation_context = {
            "customer_name": "Test User",
            "conversation_history": [
                {"content": "I have an issue with my order", "message_type": 0, "sender": {"name": "Test User"}},
                {"content": "I'd be happy to help you with your order issue. Can you provide more details?", "message_type": 1, "sender": {"name": "AI Assistant"}}
            ],
            "recent_topics": ["order", "issue"]
        }
        
        followup_message = "My order number is 12345 and it hasn't arrived yet"
        followup_response = await gemini.generate_response(
            message=followup_message,
            context=conversation_context
        )
        
        print(f"📤 Followup message: {followup_message}")
        print(f"📥 Contextual response:")
        print(f"   {followup_response}")
        
        print("\n✅ Gemini API test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing Gemini API: {e}")
        return False

def main():
    """Main function."""
    try:
        success = asyncio.run(test_gemini_api())
        
        if success:
            print("\n🎉 Your Gemini API configuration is working correctly!")
            print("You can now start the Chatwoot bot with: python start_bot.py")
        else:
            print("\n🔧 Please fix the configuration issues and try again.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Test cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
