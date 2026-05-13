from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from chat.services.chat_service import ChatService
import uuid


class ChatView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get conversation history for user"""
        try:
            conversation_id = request.query_params.get('conversation_id')
            
            if conversation_id:
                # Get specific conversation
                try:
                    conversation = ChatService.get_or_create_conversation(
                        conversation_id=conversation_id, 
                        user=request.user
                    )
                except:
                    return Response({
                        "error": "Conversation not found"
                    }, status=status.HTTP_404_NOT_FOUND)
                
                messages = ChatService.get_conversation_messages(conversation)
                return Response({
                    "conversation_id": str(conversation.id),
                    "messages": messages
                }, status=status.HTTP_200_OK)
            else:
                # Get latest conversation for user
                latest_conversation = request.user.conversations.order_by('-updated_at').first()
                if latest_conversation:
                    messages = ChatService.get_conversation_messages(latest_conversation)
                    return Response({
                        "conversation_id": str(latest_conversation.id),
                        "messages": messages
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "conversation_id": None,
                        "messages": []
                    }, status=status.HTTP_200_OK)
                    
        except Exception as e:
            print(f"Error fetching conversation: {e}")
            return Response({
                "error": "Failed to fetch conversation history"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Handle chat messages"""
        try:
            data = request.data
            
            # Validate required fields
            if not data.get('message'):
                return Response({
                    "error": "Message is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not isinstance(data.get('message'), str):
                return Response({
                    "error": "Message must be a string"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate conversation ID if provided
            conversation_id = data.get('conversation_id')
            if conversation_id:
                try:
                    uuid.UUID(conversation_id)
                except ValueError:
                    return Response({
                        "error": "Invalid conversation ID format"
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Process chat message
            ai_response, conversation_id = ChatService.process_chat_message(
                message=data['message'].strip(),
                user=request.user,
                conversation_id=conversation_id
            )
            
            return Response({
                "response": ai_response,
                "conversation_id": conversation_id
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            error_msg = str(e)
            print(f"Chat endpoint error: {error_msg}")
            
            return Response({
                "error": "An internal error occurred while processing your message"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
