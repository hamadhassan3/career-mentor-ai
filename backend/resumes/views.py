from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Resume
from .serializers import ResumeSerializer, ResumeListSerializer


class ResumeListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ResumeListSerializer
        return ResumeSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ResumeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """
        Override update to only allow updating active resumes
        """
        instance = self.get_object()
        
        # Check if the resume is active
        if not instance.is_active:
            return Response(
                {'error': 'Only active resumes can be updated. Please activate this resume first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Override partial_update to only allow updating active resumes
        """
        instance = self.get_object()
        
        # Check if the resume is active
        if not instance.is_active:
            return Response(
                {'error': 'Only active resumes can be updated. Please activate this resume first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().partial_update(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_resume_from_upload(request):
    """
    Create a resume from uploaded file data with additional metadata
    """
    data = request.data.copy()
    data['user'] = request.user.id
    
    with transaction.atomic():
        # Deactivate all existing resumes for this user
        Resume.objects.filter(user=request.user, is_active=True).update(is_active=False)
        
        # Set new resume as active
        data['is_active'] = True
        
        serializer = ResumeSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_latest_resume(request):
    """
    Get the user's most recent resume (for backward compatibility)
    """
    try:
        resume = Resume.objects.filter(user=request.user).first()
        if resume:
            serializer = ResumeSerializer(resume)
            return Response(serializer.data)
        return Response({'message': 'No resumes found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_resume(request):
    """
    Get the user's currently active resume
    """
    try:
        resume = Resume.objects.filter(user=request.user, is_active=True).first()
        if resume:
            serializer = ResumeSerializer(resume)
            return Response(serializer.data)
        return Response({'message': 'No active resume found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activate_resume(request, pk):
    """
    Activate a specific resume (deactivates all others)
    """
    try:
        resume = get_object_or_404(Resume, pk=pk, user=request.user)
        
        with transaction.atomic():
            # Deactivate all other resumes for this user
            Resume.objects.filter(user=request.user, is_active=True).update(is_active=False)
            
            # Activate the selected resume
            resume.is_active = True
            resume.save()
        
        serializer = ResumeSerializer(resume)
        return Response({'message': 'Resume activated successfully', 'resume': serializer.data})
    
    except Resume.DoesNotExist:
        return Response({'error': 'Resume not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)