from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from django.conf import settings
from typing import List, Dict
import os
import requests


class ProxyLLM:
    """Custom LLM proxy hosted on AWS Lambda (public access, Gemini-backed)"""

    def __init__(self, base_url: str):
        self.base_url = base_url

    def invoke(self, messages):
        # Convert LangChain messages to Gemini-native format.
        # SystemMessage -> systemInstruction; Human/AI -> contents (roles user/model).
        contents = []
        system_parts = []
        for msg in messages:
            if not hasattr(msg, 'content'):
                continue
            cls = msg.__class__.__name__
            if cls == 'SystemMessage':
                system_parts.append({"text": msg.content})
            elif cls == 'HumanMessage':
                contents.append({"role": "user", "parts": [{"text": msg.content}]})
            elif cls == 'AIMessage':
                contents.append({"role": "model", "parts": [{"text": msg.content}]})

        payload = {"contents": contents}
        if system_parts:
            payload["systemInstruction"] = {"parts": system_parts}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Create a simple response object with content attribute
            class SimpleResponse:
                def __init__(self, content):
                    self.content = content

            return SimpleResponse(result["text"])

        except Exception as e:
            raise Exception(f"Proxy LLM error: {e}")


class LLMService:
    def __init__(self):
        environment = os.getenv('ENVIRONMENT', 'development')
        
        if environment == 'production':
            # Use custom AWS Lambda proxy for production (Gemini-backed, public access)
            proxy_url = os.getenv('LLM_PROXY_URL')
            if proxy_url:
                self.model = ProxyLLM(proxy_url)
                self.model_name = "gemini-3.1-flash-lite"
            else:
                self.model = None
                self.model_name = None
        else:
            # Use Gemini for development
            google_key = os.getenv('GOOGLE_API_KEY')
            if google_key:
                self.model = ChatGoogleGenerativeAI(
                    model="gemini-3.1-flash-lite",
                    google_api_key=google_key,
                    temperature=0.7,
                    max_tokens=1024,
                    top_p=0.9
                )
                self.model_name = "gemini-3.1-flash-lite"
            else:
                self.model = None
                self.model_name = None
    
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