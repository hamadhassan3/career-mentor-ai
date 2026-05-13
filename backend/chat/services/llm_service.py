from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from django.conf import settings
from typing import List, Dict
import os


class LLMService:
    def __init__(self):
        groq_api_key = os.getenv('GROQ_API_KEY')
        
        self.model = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=groq_api_key,
            temperature=0.7,
            max_tokens=1024
        ) if groq_api_key else None
    
    def generate_response(self, 
                         system_prompt: str, 
                         conversation_history: List[Dict[str, str]], 
                         user_message: str) -> str:
        """
        Generate AI response using Gemini via LangChain
        
        Args:
            system_prompt: The system prompt with user context
            conversation_history: List of previous messages
            user_message: Current user message
            
        Returns:
            response_text
        """
        if not self.model:
            return "I'm sorry, the AI service is currently unavailable."
        
        try:
            # Build message chain
            messages = [SystemMessage(content=system_prompt)]
            
            # Add conversation history
            for msg in conversation_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
            
            # Add current user message
            messages.append(HumanMessage(content=user_message))
            
            # Generate response
            response = self.model.invoke(messages)
            
            # Handle Gemini 3.1 Flash Lite response format
            content = response.content
            if isinstance(content, list) and content:
                return content[0]['text']
            
            return content
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while processing your request. Please try again."


# Singleton instance
llm_service = LLMService()