"""Gemini AI integration for Chatwoot agent bot."""

import google.generativeai as genai
from typing import Optional, Dict, Any
import logging
from pathlib import Path

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
        self.system_prompt = """You are a helpful customer service assistant. You should:
- Be polite, professional, and empathetic
- Keep responses concise but informative
- Reference previous conversation context when relevant
- If you don't know something, be honest and offer alternative help
- Maintain conversation continuity by acknowledging what was discussed before
- Adapt your tone based on the customer's interaction level"""
    
    def set_system_prompt(self, prompt: str):
        """Set a custom system prompt for the AI."""
        self.system_prompt = prompt
    
    def load_system_prompt_from_file(self, file_path: str):
        """Load system prompt from a text or markdown file."""
        try:
            prompt_file = Path(file_path)
            if not prompt_file.exists():
                logger.warning(f"System prompt file not found: {file_path}. Using default prompt.")
                return
            
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    self.system_prompt = content
                    logger.info(f"Loaded system prompt from: {file_path}")
                else:
                    logger.warning(f"System prompt file is empty: {file_path}. Using default prompt.")
        except Exception as e:
            logger.error(f"Error loading system prompt from file {file_path}: {e}")
            logger.info("Using default system prompt.")
    
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
            customer_info = []
            if "customer_name" in context and context["customer_name"]:
                customer_info.append(f"Customer name: {context['customer_name']}")
            if "customer_email" in context and context["customer_email"]:
                customer_info.append(f"Customer email: {context['customer_email']}")
            
            if customer_info:
                prompt_parts.append("Customer Information:")
                prompt_parts.extend(customer_info)
            
            # Add conversation status and interaction level
            if "conversation_status" in context:
                prompt_parts.append(f"Conversation status: {context['conversation_status']}")
            
            if "interaction_level" in context:
                if context["interaction_level"] == "high_engagement":
                    prompt_parts.append("Note: Customer has sent multiple messages - they may need extra attention or have an urgent issue.")
            
            # Add recent topics for context
            if "recent_topics" in context and context["recent_topics"]:
                prompt_parts.append(f"Recent topics discussed: {', '.join(context['recent_topics'])}")
            
            # Add conversation history with better formatting
            if "conversation_history" in context and context["conversation_history"]:
                prompt_parts.append("Recent conversation history:")
                history = context["conversation_history"]
                
                for msg in history[-5:]:  # Last 5 messages for context
                    sender_name = "Customer"
                    if msg.get("message_type") == 1:  # outgoing message
                        sender_info = msg.get("sender", {})
                        sender_name = sender_info.get("name", "Agent")
                    elif msg.get("message_type") == 0:  # incoming message  
                        sender_name = context.get("customer_name", "Customer")
                    
                    content = msg.get("content", "").strip()
                    if content:
                        prompt_parts.append(f"{sender_name}: {content}")
            
            if "custom_context" in context:
                prompt_parts.append(f"Additional context: {context['custom_context']}")
        
        prompt_parts.append(f"\nCurrent customer message: {message}")
        prompt_parts.append("\nYour response (be helpful and maintain conversation continuity):")
        
        return "\n".join(prompt_parts)
