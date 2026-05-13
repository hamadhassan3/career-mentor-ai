from typing import Tuple
from django.utils import timezone
from chat.models import Conversation, Message, MessageRole
from chat.services.llm_service import llm_service
from chat.services.prompt_service import prompt_service
from chat.services.langfuse_logger import langfuse_logger
import uuid


class ChatService:
    MAX_HISTORY = 10
    
    @staticmethod
    def build_user_context(user) -> str:
        """Build user context string from Django models"""
        try:
            # Get active resume
            active_resume = user.resumes.filter(is_active=True).first()
            
            # Get next step
            next_step = user.next_steps.first() if hasattr(user, 'next_steps') else None
            
            # Get career pathway
            career_pathway = user.career_pathways.first() if hasattr(user, 'career_pathways') else None
            
            # Build context string
            context_parts = []
            
            # User Profile
            context_parts.append(f"User Profile:")
            context_parts.append(f"Name: {user.first_name} {user.last_name}")
            
            if active_resume:
                context_parts.append(f"Target Role: {getattr(active_resume, 'target_designation', 'Not specified')}")
                context_parts.append(f"Experience: {getattr(active_resume, 'total_exp', 0)} years")
                
                # Get skills - handle both list and string formats
                skills = getattr(active_resume, 'it_skills', [])
                if isinstance(skills, list):
                    skills_str = ', '.join(skills[:10])  # Limit to 10 skills
                else:
                    skills_str = str(skills)[:200]  # Limit string length
                context_parts.append(f"Current Skills: {skills_str}")
            
            if next_step:
                context_parts.append(f"\nNext Best Step: {getattr(next_step, 'title', 'Not available')}")
                # Handle recommended_skills
                rec_skills = getattr(next_step, 'recommended_skills', [])
                if isinstance(rec_skills, list):
                    rec_skills_str = ', '.join(rec_skills)
                else:
                    rec_skills_str = str(rec_skills)
                context_parts.append(f"Recommended Skills: {rec_skills_str}")
                context_parts.append(f"Impact: {getattr(next_step, 'impact', 'Unknown')}")
            
            if career_pathway:
                current_level = getattr(career_pathway, 'current_level', '')
                target_role = getattr(career_pathway, 'target_role', '')
                timeline = getattr(career_pathway, 'timeline_total', 'TBD')
                context_parts.append(f"\nCareer Pathway: {current_level} → {target_role}")
                context_parts.append(f"Timeline: {timeline}")
            
            return '\n'.join(context_parts)
            
        except Exception as e:
            print(f"Error building user context: {e}")
            return f"User Profile:\nName: {user.first_name} {user.last_name}\nTarget Role: Career guidance seeker"
    
    @staticmethod
    def get_or_create_conversation(conversation_id: str = None, user=None) -> Conversation:
        """Get existing conversation or create new one"""
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id, user=user)
                return conversation
            except Conversation.DoesNotExist:
                pass
        
        # Create new conversation
        conversation = Conversation.objects.create(user=user)
        return conversation
    
    @staticmethod
    def get_conversation_messages(conversation: Conversation):
        """Get the last 10 messages from conversation"""
        messages = conversation.messages.order_by('-created_at')[:ChatService.MAX_HISTORY]
        
        # Reverse to get chronological order (oldest first)
        messages = list(reversed(messages))
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            } for msg in messages
        ]
    
    @staticmethod
    def add_message(conversation: Conversation, role: str, content: str, langfuse_trace_id: str = None) -> Message:
        """Add message to conversation"""
        # Convert string role to enum
        if role == "user":
            message_role = MessageRole.USER
        elif role == "assistant":
            message_role = MessageRole.ASSISTANT
        elif role == "system":
            message_role = MessageRole.SYSTEM
        else:
            raise ValueError(f"Invalid message role: {role}")
        
        message = Message.objects.create(
            conversation=conversation,
            role=message_role,
            content=content,
            langfuse_trace_id=langfuse_trace_id
        )
        
        # Update conversation's updated_at
        conversation.updated_at = timezone.now()
        conversation.save()
        
        return message
    
    @staticmethod
    def process_chat_message(message: str, user, conversation_id: str = None) -> Tuple[str, str]:
        """
        Process a chat message and return AI response
        
        Args:
            message: User's message
            user: Django User instance
            conversation_id: Optional conversation ID
            
        Returns:
            Tuple of (ai_response, conversation_id)
        """
        trace_id = None
        
        try:
            # Build user context from Django models
            user_context = ChatService.build_user_context(user)
            
            # Create Langfuse trace
            trace_id = langfuse_logger.create_trace(
                conversation_id=conversation_id or "new",
                user_id=user.id,
                user_context={"context": user_context}
            )
            
            # Get or create conversation
            conversation = ChatService.get_or_create_conversation(
                conversation_id=conversation_id,
                user=user
            )
            
            # Get conversation messages (last 10)
            recent_messages = ChatService.get_conversation_messages(conversation)
            
            # Build conversation context for prompt
            conversation_context = prompt_service.build_conversation_context(
                recent_messages=recent_messages
            )
            
            # Build system prompt with user context
            system_prompt = prompt_service.build_system_prompt(
                user_context=user_context,
                conversation_context=conversation_context
            )
            
            # Generate AI response
            ai_response = llm_service.generate_response(
                system_prompt=system_prompt,
                conversation_history=recent_messages,
                user_message=message
            )
            
            # Log LLM call
            langfuse_logger.log_llm_call(
                trace_id=trace_id,
                model=llm_service.model_name or "unknown",
                system_prompt=system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt,
                user_message=message,
                assistant_response=ai_response,
                token_usage={}
            )
            
            # Save messages to database
            ChatService.add_message(
                conversation=conversation,
                role="user",
                content=message,
                langfuse_trace_id=trace_id
            )
            
            ChatService.add_message(
                conversation=conversation,
                role="assistant",
                content=ai_response,
                langfuse_trace_id=trace_id
            )
            
            return ai_response, str(conversation.id)
            
        except Exception as e:
            error_msg = f"Error processing chat message: {str(e)}"
            print(error_msg)
            
            # Return a friendly error message
            error_response = "I apologize, but I encountered an issue while processing your message. Please try again in a moment."
            
            # Try to save error context if we have a conversation
            try:
                if conversation_id:
                    conversation = ChatService.get_or_create_conversation(
                        conversation_id=conversation_id,
                        user=user
                    )
                    
                    ChatService.add_message(
                        conversation=conversation,
                        role="user",
                        content=message,
                        langfuse_trace_id=trace_id
                    )
                    
                    ChatService.add_message(
                        conversation=conversation,
                        role="assistant",
                        content=error_response,
                        langfuse_trace_id=trace_id
                    )
                    
                    return error_response, str(conversation.id)
            except:
                pass  # If we can't save, just return the error
            
            return error_response, conversation_id or str(uuid.uuid4())
        
        finally:
            langfuse_logger.flush()