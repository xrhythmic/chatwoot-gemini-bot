""" Webhook service for Chatwoot with Gemini AI integration."""

import uvicorn
from woot import AsyncChatwoot
from typer import Typer
from typing import Dict, Optional, List
from woothook.utils import load_config
from woothook.gemini_ai import GeminiAI
from fastapi import FastAPI, Response, status
import logging
import asyncio
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Typer()


class WootHook:
    def __init__(self, config_file: str):
        self.config = load_config(config_file)
        self.chatwoot = AsyncChatwoot(
            chatwoot_url=self.config.chatwoot.url,
            access_key=self.config.chatwoot.access_key,
        )
        self.port = self.config.service.port
        self.host = self.config.service.host
        
        # Conversation context cache - stores recent messages per conversation
        # Format: {conversation_id: {"messages": [...], "last_updated": datetime}}
        self.conversation_cache = {}
        self.cache_timeout = timedelta(hours=2)  # Clear cache after 2 hours
        
        # Initialize Gemini AI
        self.gemini = GeminiAI(
            api_key=self.config.gemini.api_key,
            model=self.config.gemini.model,
            max_tokens=self.config.gemini.max_tokens,
            temperature=self.config.gemini.temperature
        )
        
        # Set custom system prompt if provided in config
        if hasattr(self.config.gemini, 'system_prompt') and self.config.gemini.system_prompt:
            self.gemini.set_system_prompt(self.config.gemini.system_prompt)

        async def message_handler(request: Dict):
            await self.process_message(request)
            return Response(status_code=status.HTTP_204_NO_CONTENT)

        self.listener = FastAPI()
        self.listener.add_api_route("/", message_handler, methods=["POST"])

    async def process_message(self, request: Dict):
        """Process incoming Chatwoot webhook messages."""
        try:
            logger.info(f"Received webhook: {request}")
            
            # Extract message information
            message_type = request.get("message_type")
            conversation = request.get("conversation", {})
            message = request.get("content")
            sender = request.get("sender", {})
            
            # Only respond to incoming customer messages (message_type = 0)
            if message_type != 0 or not message:
                logger.info("Skipping non-customer message or empty message")
                return
            
            # Get conversation and contact details
            conversation_id = conversation.get("id")
            contact = conversation.get("contact", {})
            account_id = self.config.chatwoot.account_id
            
            if not conversation_id:
                logger.warning("No conversation ID found")
                return
            
            # Update conversation cache with new message
            await self._update_conversation_cache(conversation_id, {
                "content": message,
                "message_type": message_type,
                "sender": sender,
                "timestamp": datetime.now()
            })
            
            # Build context for AI with conversation history
            context = await self._build_context(conversation, contact, account_id, conversation_id)
            
            # Generate AI response
            ai_response = await self.gemini.generate_response(message, context)
            
            # Send response back to Chatwoot
            await self._send_response(account_id, conversation_id, ai_response)
            
            # Update cache with bot's response
            await self._update_conversation_cache(conversation_id, {
                "content": ai_response,
                "message_type": 1,  # outgoing message
                "sender": {"name": "AI Assistant"},
                "timestamp": datetime.now()
            })
            
            logger.info(f"Sent AI response to conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def _update_conversation_cache(self, conversation_id: int, message: Dict):
        """Update the conversation cache with a new message."""
        now = datetime.now()
        
        # Clean old cache entries
        self._clean_cache()
        
        if conversation_id not in self.conversation_cache:
            self.conversation_cache[conversation_id] = {
                "messages": [],
                "last_updated": now
            }
        
        # Add new message to cache
        self.conversation_cache[conversation_id]["messages"].append(message)
        self.conversation_cache[conversation_id]["last_updated"] = now
        
        # Keep only last 10 messages per conversation
        messages = self.conversation_cache[conversation_id]["messages"]
        if len(messages) > 10:
            self.conversation_cache[conversation_id]["messages"] = messages[-10:]
    
    def _clean_cache(self):
        """Remove old conversations from cache."""
        now = datetime.now()
        expired_conversations = []
        
        for conv_id, data in self.conversation_cache.items():
            if now - data["last_updated"] > self.cache_timeout:
                expired_conversations.append(conv_id)
        
        for conv_id in expired_conversations:
            del self.conversation_cache[conv_id]
            logger.info(f"Cleaned conversation {conv_id} from cache")

    async def _build_context(self, conversation: Dict, contact: Dict, account_id: int, conversation_id: int) -> Dict:
    async def _build_context(self, conversation: Dict, contact: Dict, account_id: int, conversation_id: int) -> Dict:
        """Build context information for the AI with conversation history."""
        context = {}
        
        # Add customer information
        if contact:
            context["customer_name"] = contact.get("name", "")
            context["customer_email"] = contact.get("email", "")
        
        # Add conversation metadata
        context["conversation_id"] = conversation_id
        context["conversation_status"] = conversation.get("status", "open")
        
        # Get conversation history from cache first, then API if needed
        conversation_history = []
        
        # Try to get from cache first
        if conversation_id in self.conversation_cache:
            cached_messages = self.conversation_cache[conversation_id]["messages"]
            # Convert cached messages to expected format
            for msg in cached_messages[-5:]:  # Last 5 messages
                conversation_history.append({
                    "content": msg.get("content", ""),
                    "message_type": msg.get("message_type", 0),
                    "sender": msg.get("sender", {}),
                    "timestamp": msg.get("timestamp", "").isoformat() if isinstance(msg.get("timestamp"), datetime) else str(msg.get("timestamp", ""))
                })
        else:
            # Fallback to API if not in cache
            try:
                messages_response = await self.chatwoot.conversations.messages.list(
                    account_id=account_id,
                    conversation_id=conversation_id
                )
                
                if messages_response and hasattr(messages_response, 'get'):
                    messages = messages_response.get("payload", [])
                    conversation_history = messages[-5:] if messages else []
                    
            except Exception as e:
                logger.warning(f"Could not fetch conversation history from API: {e}")
        
        context["conversation_history"] = conversation_history
        
        # Add some conversational intelligence
        if conversation_history:
            # Check if this is a continuation of a topic
            recent_messages = [msg.get("content", "") for msg in conversation_history[-3:]]
            context["recent_topics"] = self._extract_topics(recent_messages)
            
            # Check if customer seems frustrated (multiple messages in short time)
            customer_messages = [msg for msg in conversation_history if msg.get("message_type") == 0]
            if len(customer_messages) >= 3:
                context["interaction_level"] = "high_engagement"
        
        return context
    
    def _extract_topics(self, messages: List[str]) -> List[str]:
        """Extract key topics from recent messages for context."""
        # Simple keyword extraction - could be enhanced with NLP
        topics = []
        keywords = ["order", "payment", "delivery", "refund", "support", "problem", "issue", "help"]
        
        for message in messages:
            if message:
                message_lower = message.lower()
                for keyword in keywords:
                    if keyword in message_lower and keyword not in topics:
                        topics.append(keyword)
        
        return topics

    async def _send_response(self, account_id: int, conversation_id: int, message: str):
        """Send AI response back to Chatwoot."""
        try:
            await self.chatwoot.conversations.messages.create(
                account_id=account_id,
                conversation_id=conversation_id,
                content=message,
                message_type="outgoing",
                private=False
            )
        except Exception as e:
            logger.error(f"Error sending response to Chatwoot: {e}")


@app.command()
def start(config_file: str):
    """Start the Chatwoot webhook server with Gemini AI integration."""
    hook = WootHook(config_file)
    logger.info(f"Starting Chatwoot-Gemini agent bot on {hook.host}:{hook.port}")
    uvicorn.run(
        hook.listener, host=hook.host, port=hook.port
    )


if __name__ == "__main__":
    app()
