from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import ProgressAchievement
from .serializers import ProgressAchievementSerializer, ProgressAchievementCreateSerializer
from .services import S3UploadService


class ProgressAchievementListView(generics.ListAPIView):
    serializer_class = ProgressAchievementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ProgressAchievement.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_progress_achievement(request):
    serializer = ProgressAchievementCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid data', 'details': serializer.errors}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Upload image to S3
    s3_service = S3UploadService()
    upload_result = s3_service.upload_progress_image(
        serializer.validated_data['image'],
        request.user.id
    )
    
    if not upload_result['success']:
        return Response(
            {'error': upload_result['error']}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Create achievement record
    achievement = ProgressAchievement.objects.create(
        user=request.user,
        skill=serializer.validated_data['skill'],
        image_url=upload_result['image_url'],
        s3_key=upload_result['s3_key']
    )
    
    response_serializer = ProgressAchievementSerializer(achievement)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_progress_achievement(request, achievement_id):
    achievement = get_object_or_404(
        ProgressAchievement, 
        id=achievement_id, 
        user=request.user
    )
    
    # Delete image from S3
    s3_service = S3UploadService()
    s3_service.delete_progress_image(achievement.s3_key)
    
    # Delete achievement record
    achievement.delete()
    
    return Response(
        {'message': 'Achievement deleted successfully'}, 
        status=status.HTTP_200_OK
    )


