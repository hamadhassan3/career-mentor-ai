from typing import Tuple
from django.utils import timezone
from nudge.models import Nudge
from chat.services.llm_service import llm_service
from chat.services.langfuse_logger import langfuse_logger
from chat.services.prompt_service import prompt_service


class NudgeService:

    @staticmethod 
    def get_or_generate_nudge(user) -> Tuple[str, bool]:
        """
        Get existing nudge for user or generate new one if needed
        
        Returns:
            Tuple of (nudge_content, is_newly_generated)
        """
        try:
            # Check for existing nudge
            latest_nudge = Nudge.get_latest_for_user(user)
            
            # Return existing nudge if it's fresh (less than 24 hours old)
            if latest_nudge and not latest_nudge.is_stale:
                return latest_nudge.content, False
            
            # Generate new nudge
            return NudgeService.generate_new_nudge(user)
            
        except Exception as e:
            print(f"Error in get_or_generate_nudge: {e}")
            return "Stay focused on your career goals! Take one small step forward today. 🚀", False
    
    @staticmethod
    def generate_new_nudge(user) -> Tuple[str, bool]:
        """Generate a new nudge for the user"""
        trace_id = None
        
        try:
            # Build user context using centralized prompt service
            user_context = prompt_service.build_user_context(user)
            
            # Create Langfuse trace
            trace_id = langfuse_logger.create_trace(
                conversation_id=f"nudge_{user.id}_{timezone.now().date()}",
                user_id=user.id,
                user_context={"context": user_context, "type": "nudge_generation"}
            )
            
            # Build nudge-specific system prompt using prompt service
            system_prompt = prompt_service.build_nudge_system_prompt(user_context)
            
            # Generate nudge using LLM
            nudge_content = llm_service.generate_response(
                system_prompt=system_prompt,
                conversation_history=[],
                user_message="Generate my daily career nudge."
            )
            
            # Clean up the response
            nudge_content = nudge_content.strip()
            if len(nudge_content) > 300:
                nudge_content = nudge_content[:297] + "..."
            
            # Log LLM call
            langfuse_logger.log_llm_call(
                trace_id=trace_id,
                model=llm_service.model_name or "unknown",
                system_prompt=system_prompt,  # Don't truncate - log full system prompt
                user_message="Generate my daily career nudge.",
                assistant_response=nudge_content,
                token_usage={}
            )
            
            # Save nudge to database
            nudge = Nudge.objects.create(
                user=user,
                content=nudge_content,
                langfuse_trace_id=trace_id
            )
            
            return nudge.content, True
            
        except Exception as e:
            error_msg = f"Error generating nudge: {str(e)}"
            print(error_msg)
            
            # Return fallback nudge
            fallback_content = "Your career journey is unique and valuable. Take one meaningful step today towards your professional goals! 🌟"
            
            # Try to save fallback nudge
            try:
                Nudge.objects.create(
                    user=user,
                    content=fallback_content,
                    langfuse_trace_id=trace_id
                )
            except:
                pass
            
            return fallback_content, True
        
        finally:
            langfuse_logger.flush()
    
    @staticmethod
    def force_regenerate_nudge(user) -> str:
        """Force regenerate a new nudge regardless of existing one"""
        try:
            content, _ = NudgeService.generate_new_nudge(user)
            return content
        except Exception as e:
            print(f"Error force regenerating nudge: {e}")
            return "Keep pushing forward! Every small action brings you closer to your career goals. 💪"


# Singleton instance
nudge_service = NudgeService()