""" Webhook service for Chatwoot with Gemini AI integration."""

import uvicorn
from woot import AsyncChatwoot
from typer import Typer
from typing import Dict, Optional
from woothook.utils import load_config
from woothook.gemini_ai import GeminiAI
from fastapi import FastAPI, Response, status
import logging
import asyncio

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
        
        # Initialize Gemini AI
        self.gemini = GeminiAI(
            api_key=self.config.gemini.api_key,
            model=self.config.gemini.model,
            max_tokens=self.config.gemini.max_tokens,
            temperature=self.config.gemini.temperature
        )

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
            
            # Build context for AI
            context = await self._build_context(conversation, contact, account_id)
            
            # Generate AI response
            ai_response = await self.gemini.generate_response(message, context)
            
            # Send response back to Chatwoot
            await self._send_response(account_id, conversation_id, ai_response)
            
            logger.info(f"Sent AI response to conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def _build_context(self, conversation: Dict, contact: Dict, account_id: int) -> Dict:
        """Build context information for the AI."""
        context = {}
        
        # Add customer information
        if contact:
            context["customer_name"] = contact.get("name", "")
            context["customer_email"] = contact.get("email", "")
        
        # Try to get recent conversation history
        conversation_id = conversation.get("id")
        if conversation_id:
            try:
                # Get recent messages from the conversation
                messages_response = await self.chatwoot.conversations.messages.list(
                    account_id=account_id,
                    conversation_id=conversation_id
                )
                
                if messages_response and hasattr(messages_response, 'get'):
                    messages = messages_response.get("payload", [])
                    # Get last few messages for context
                    context["conversation_history"] = messages[-5:] if messages else []
                    
            except Exception as e:
                logger.warning(f"Could not fetch conversation history: {e}")
                context["conversation_history"] = []
        
        return context

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
