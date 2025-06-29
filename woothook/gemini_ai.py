"""Gemini AI integration for Chatwoot agent bot."""

import google.generativeai as genai
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GeminiAI:
    """Gemini AI client for generating responses to Chatwoot messages."""
    
    def __init__(self, api_key: str, model: str = "gemini-pro", 
                 max_tokens: int = 1000, temperature: float = 0.7):
        """
        Initialize Gemini AI client.
        
        Args:
            api_key: Google AI API key
            model: Gemini model to use
            max_tokens: Maximum tokens in response
            temperature: Response creativity (0.0-1.0)
        """
        self.api_key = api_key
        self.model_name = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        
        # Default system prompt
        self.system_prompt = """You are a helpful customer service assistant for a business. 
You should be polite, professional, and helpful. Keep your responses concise but informative.
If you don't know something, be honest about it and offer to help in other ways."""
    
    def set_system_prompt(self, prompt: str):
        """Set a custom system prompt for the AI."""
        self.system_prompt = prompt
    
    async def generate_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a response to a customer message.
        
        Args:
            message: The customer's message
            context: Additional context (customer info, conversation history, etc.)
            
        Returns:
            Generated response string
        """
        try:
            # Prepare the prompt with context
            prompt = self._build_prompt(message, context)
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
            )
            
            if response.text:
                return response.text.strip()
            else:
                logger.warning("Gemini returned empty response")
                return "I apologize, but I'm having trouble generating a response right now. Please try again or contact our support team."
                
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again later or contact our support team directly."
    
    def _build_prompt(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build the complete prompt including system instructions and context."""
        prompt_parts = [self.system_prompt]
        
        if context:
            # Add customer context if available
            if "customer_name" in context:
                prompt_parts.append(f"Customer name: {context['customer_name']}")
            
            if "customer_email" in context:
                prompt_parts.append(f"Customer email: {context['customer_email']}")
            
            if "conversation_history" in context and context["conversation_history"]:
                prompt_parts.append("Recent conversation history:")
                for msg in context["conversation_history"][-3:]:  # Last 3 messages
                    sender = "Customer" if msg.get("message_type") == 0 else "Agent"
                    prompt_parts.append(f"{sender}: {msg.get('content', '')}")
            
            if "custom_context" in context:
                prompt_parts.append(f"Additional context: {context['custom_context']}")
        
        prompt_parts.append(f"Customer message: {message}")
        prompt_parts.append("Your response:")
        
        return "\n\n".join(prompt_parts)
