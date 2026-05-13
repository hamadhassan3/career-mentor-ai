from langfuse import Langfuse
import json
from datetime import datetime
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import os


class LangfuseLogger:
    def __init__(self):
        self.langfuse = Langfuse(
            secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            host=os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')
        ) if os.getenv('LANGFUSE_SECRET_KEY') else None
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="langfuse")
    
    def create_trace(self, 
                    conversation_id: str, 
                    user_id: int, 
                    user_context: Dict[str, Any]) -> Optional[str]:
        """Create a new trace for a conversation turn"""
        if not self.langfuse:
            return None
            
        try:
            trace = self.langfuse.trace.create(
                name=f"chat_conversation_{conversation_id}",
                metadata={
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            return trace.id
        except Exception as e:
            print(f"Error creating Langfuse trace: {e}")
            return None
    
    def log_llm_call(self, 
                    trace_id: Optional[str], 
                    model: str,
                    system_prompt: str,
                    user_message: str,
                    assistant_response: str,
                    token_usage: Dict[str, int]):
        """Log LLM generation span (async)"""
        if trace_id:
            self._submit_async(self._log_llm_call_sync, trace_id, model, system_prompt, user_message, assistant_response, token_usage)
    
    def _log_llm_call_sync(self, trace_id: str, model: str, system_prompt: str, user_message: str, assistant_response: str, token_usage: Dict[str, int]):
        """Synchronous LLM call logging"""
        try:
            self.langfuse.generation(
                trace_id=trace_id,
                name="llm_generation",
                model=model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                output=assistant_response,
                usage={
                    "input": token_usage.get("input_tokens", 0),
                    "output": token_usage.get("output_tokens", 0),
                    "total": token_usage.get("total_tokens", 0)
                },
                metadata={
                    "timestamp": datetime.utcnow().isoformat(),
                    "tools": []  # Ready for future tool calling
                }
            )
        except Exception as e:
            print(f"Error logging LLM call: {e}")
    
    def _submit_async(self, func, *args, **kwargs):
        """Submit function to background thread"""
        if self.langfuse:
            self.executor.submit(func, *args, **kwargs)
    
    def flush(self):
        """Flush pending logs to Langfuse"""
        if self.langfuse:
            self._submit_async(self._flush_sync)
    
    def _flush_sync(self):
        """Synchronous flush implementation"""
        try:
            self.langfuse.flush()
        except Exception as e:
            print(f"Error flushing Langfuse logs: {e}")


# Singleton instance
langfuse_logger = LangfuseLogger()