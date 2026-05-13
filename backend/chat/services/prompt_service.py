from typing import List, Dict


class PromptService:
    
    CAREER_MENTOR_SYSTEM_PROMPT = """You are FawkesPath AI, an intelligent career mentor for the FawkesPath career development platform. 
You provide personalized career guidance based on each user's specific situation and goals.

{user_context}

GUIDELINES:
- Provide personalized advice based on the user's specific career data above
- Only discuss career development, job search, and professional growth topics
- If asked about unrelated topics, politely redirect: "I'm here to help with your career development. Let's focus on your career goals."
- Be supportive and actionable in your guidance
- Keep responses SHORT and focused (2-4 sentences max, unless specifically asked for detail)
- Use bullet points for multiple recommendations
- Always tie advice back to the user's specific situation
- Prioritize the most impactful advice first

{conversation_context}"""

    CONVERSATION_CONTEXT_TEMPLATE = """
CURRENT CONVERSATION CONTEXT:
{recent_messages}"""

    @staticmethod
    def build_system_prompt(user_context: str, conversation_context: str = "") -> str:
        """Build dynamic system prompt from user context string"""
        
        return PromptService.CAREER_MENTOR_SYSTEM_PROMPT.format(
            user_context=user_context,
            conversation_context=conversation_context
        )
    
    @staticmethod
    def build_conversation_context(recent_messages: List[Dict[str, str]] = None) -> str:
        """Build conversation context section"""
        if not recent_messages:
            return ""
        
        # Format recent messages
        formatted_messages = "\n".join([
            f"{msg['role'].title()}: {msg['content'][:200]}{'...' if len(msg['content']) > 200 else ''}"
            for msg in recent_messages[-5:]  # Last 5 messages only
        ])
        
        return PromptService.CONVERSATION_CONTEXT_TEMPLATE.format(
            recent_messages=formatted_messages
        )


# Singleton instance
prompt_service = PromptService()