from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from nudge.services.nudge_service import nudge_service


class NudgeView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get daily nudge for user"""
        try:
            nudge_content, is_newly_generated = nudge_service.get_or_generate_nudge(request.user)
            
            return Response({
                "nudge": nudge_content,
                "is_new": is_newly_generated
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error fetching nudge: {e}")
            return Response({
                "error": "Failed to fetch your daily nudge"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Force regenerate a new nudge"""
        try:
            new_nudge = nudge_service.force_regenerate_nudge(request.user)
            
            return Response({
                "nudge": new_nudge,
                "is_new": True
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error regenerating nudge: {e}")
            return Response({
                "error": "Failed to regenerate your nudge"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
