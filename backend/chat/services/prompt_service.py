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
- Keep responses SHORT and focused (2-4 sentences max in less than 50 words, unless specifically asked for detail)
- Use bullet points for multiple recommendations
- Always tie advice back to the user's specific situation
- Prioritize the most impactful advice first

{conversation_context}"""

    NUDGE_SYSTEM_PROMPT = """You are FawkesPath AI, a motivational career mentor. Generate a single, inspiring daily nudge for the user based on their specific career data.

{user_context}

CRITICAL INSTRUCTION: You MUST prioritize the specific information provided above in this exact order:

1. IF "Next Best Step" is provided with specific recommended skills or actions → Create nudge about that exact step
2. IF "Career Pathway" shows a target role → Create nudge about progressing toward that specific role  
3. IF only current skills/resume info is available → Create nudge about improving those specific skills

NUDGE REQUIREMENTS:
- Keep it VERY short and punchy (around 20 words maximum)
- Must reference SPECIFIC skills, roles, or actions from the context above
- Do NOT give generic advice - use the actual data provided
- Include ONE concrete action they can take today
- Use an upbeat, motivational tone

GOOD Examples (using specific context):
- "Master React hooks today! Spend 30 minutes practicing - it's your next recommended skill."
- "Apply to 2 Senior Developer roles today - you're ready for that promotion!"
- "Polish your Python portfolio today - showcase those 3 years of experience!"

BAD Examples (too generic):
- "Learn something new today!"
- "Update your resume!"
- "Apply to jobs!"

Generate ONE specific motivational nudge now:"""

    CONVERSATION_CONTEXT_TEMPLATE = """
CURRENT CONVERSATION CONTEXT:
{recent_messages}"""

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
    def build_system_prompt(user_context: str, conversation_context: str = "") -> str:
        """Build dynamic system prompt from user context string"""
        
        return PromptService.CAREER_MENTOR_SYSTEM_PROMPT.format(
            user_context=user_context,
            conversation_context=conversation_context
        )
    
    @staticmethod
    def build_nudge_system_prompt(user_context: str) -> str:
        """Build nudge-specific system prompt from user context string"""
        
        return PromptService.NUDGE_SYSTEM_PROMPT.format(
            user_context=user_context
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