from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.conf import settings
import requests
import os
from .models import Resume, NextBestStep, CareerPathway, CareerStage
from .serializers import (
    ResumeSerializer, ResumeListSerializer, NextBestStepSerializer,
    CareerPathwaySerializer, CareerStageSerializer, ResumeWithRecommendationsSerializer
)


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
        
        # Check if target_designation is being changed
        old_designation = instance.target_designation
        new_designation = request.data.get('target_designation')
        
        response = super().update(request, *args, **kwargs)
        
        # Clear recommendations if target designation changed
        if (new_designation is not None and 
            new_designation != old_designation):
            self._clear_resume_recommendations(instance)
        
        return response
    
    def _clear_resume_recommendations(self, resume):
        """
        Helper method to clear recommendations for a resume
        """
        try:
            NextBestStep.objects.filter(resume=resume).delete()
            CareerPathway.objects.filter(resume=resume).delete()
        except Exception:
            pass  # Silently ignore errors
    
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
        
        # Check if target_designation is being changed
        old_designation = instance.target_designation
        new_designation = request.data.get('target_designation')
        
        response = super().partial_update(request, *args, **kwargs)
        
        # Clear recommendations if target designation changed
        if (new_designation is not None and 
            new_designation != old_designation):
            self._clear_resume_recommendations(instance)
        
        return response


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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_next_best_step(request):
    """
    Save next best step recommendations for the active resume
    """
    try:
        resume = Resume.objects.filter(user=request.user, is_active=True).first()
        if not resume:
            return Response({'error': 'No active resume found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get or create next best step for this resume
        next_step, created = NextBestStep.objects.get_or_create(
            resume=resume,
            defaults=request.data
        )
        
        if not created:
            # Update existing record
            for field, value in request.data.items():
                if hasattr(next_step, field):
                    setattr(next_step, field, value)
            next_step.save()
        
        serializer = NextBestStepSerializer(next_step)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_next_best_step(request):
    """
    Get next best step recommendations for the active resume
    """
    try:
        resume = Resume.objects.filter(user=request.user, is_active=True).first()
        if not resume:
            return Response({'error': 'No active resume found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            next_step = NextBestStep.objects.get(resume=resume)
            serializer = NextBestStepSerializer(next_step)
            return Response(serializer.data)
        except NextBestStep.DoesNotExist:
            return Response({'message': 'No next step recommendations found'}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_career_pathway(request):
    """
    Save career pathway recommendations for the active resume
    """
    try:
        resume = Resume.objects.filter(user=request.user, is_active=True).first()
        if not resume:
            return Response({'error': 'No active resume found'}, status=status.HTTP_404_NOT_FOUND)
        
        stages_data = request.data.pop('stages', [])
        
        with transaction.atomic():
            # Get or create career pathway
            pathway, created = CareerPathway.objects.get_or_create(
                resume=resume,
                defaults=request.data
            )
            
            if not created:
                # Update existing pathway
                for field, value in request.data.items():
                    if hasattr(pathway, field):
                        setattr(pathway, field, value)
                pathway.save()
                
                # Clear existing stages
                pathway.stages.all().delete()
            
            # Create stages
            for i, stage_data in enumerate(stages_data):
                stage_data['order'] = i
                CareerStage.objects.create(pathway=pathway, **stage_data)
        
        serializer = CareerPathwaySerializer(pathway)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_career_pathway(request):
    """
    Get career pathway recommendations for the active resume
    """
    try:
        resume = Resume.objects.filter(user=request.user, is_active=True).first()
        if not resume:
            return Response({'error': 'No active resume found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            pathway = CareerPathway.objects.get(resume=resume)
            serializer = CareerPathwaySerializer(pathway)
            return Response(serializer.data)
        except CareerPathway.DoesNotExist:
            return Response({'message': 'No career pathway found'}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_recommendations(request):
    """
    Clear both next best step and career pathway recommendations for the active resume
    """
    try:
        resume = Resume.objects.filter(user=request.user, is_active=True).first()
        if not resume:
            return Response({'error': 'No active resume found'}, status=status.HTTP_404_NOT_FOUND)
        
        deleted_count = 0
        
        # Delete next best step
        try:
            next_step = NextBestStep.objects.get(resume=resume)
            next_step.delete()
            deleted_count += 1
        except NextBestStep.DoesNotExist:
            pass
        
        # Delete career pathway (cascades to stages)
        try:
            pathway = CareerPathway.objects.get(resume=resume)
            pathway.delete()
            deleted_count += 1
        except CareerPathway.DoesNotExist:
            pass
        
        return Response({
            'message': f'Cleared {deleted_count} recommendation(s)',
            'cleared_items': deleted_count
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_course_recommendations(request):
    """
    Get course recommendations for the next best skill
    """
    try:
        resume = Resume.objects.filter(user=request.user, is_active=True).first()
        if not resume:
            return Response({'error': 'No active resume found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            next_step = NextBestStep.objects.get(resume=resume)
        except NextBestStep.DoesNotExist:
            return Response({'error': 'No next step recommendations found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Use the main skill (title) as the search query
        skill_query = next_step.title
        if not skill_query or skill_query == 'No recommendations available':
            return Response({'courses': []}, status=status.HTTP_200_OK)
        
        try:
            # Get course recommendation service URL from environment
            course_api_url = os.getenv('COURSE_RECOMMENDATION_API_BASE_URL', 'http://localhost:5051')
            
            # Make request to course recommendation service
            response = requests.post(
                f"{course_api_url}/courses/search",
                json={
                    "query": skill_query,
                    "platforms": ["coursera", "youtube"],
                    "limit": 3
                },
                timeout=10
            )
            
            if response.status_code == 200:
                course_data = response.json()
                return Response({
                    'skill': skill_query,
                    'courses': course_data.get('courses', [])[:]  # Ensure only 3 courses
                })
            else:
                return Response({
                    'skill': skill_query,
                    'courses': [],
                    'error': 'Failed to fetch course recommendations'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
        except requests.RequestException as e:
            return Response({
                'skill': skill_query,
                'courses': [],
                'error': f'Course recommendation service unavailable: {str(e)}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)