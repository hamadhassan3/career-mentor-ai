from rest_framework import serializers
from .models import Resume, NextBestStep, CareerPathway, CareerStage


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class ResumeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ('id', 'title', 'target_designation', 'original_filename', 'is_active', 'created_at', 'updated_at')


class CareerStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerStage
        fields = ('id', 'title', 'duration', 'status', 'skills', 'milestones', 'order', 'created_at', 'updated_at')


class CareerPathwaySerializer(serializers.ModelSerializer):
    stages = CareerStageSerializer(many=True, read_only=True)
    
    class Meta:
        model = CareerPathway
        fields = ('id', 'current_level', 'target_role', 'timeline_total', 'target_designation', 'stages', 'created_at', 'updated_at')


class NextBestStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = NextBestStep
        fields = ('id', 'title', 'skill_type', 'confidence', 'impact', 'recommended_skills', 'target_designation', 'created_at', 'updated_at')


class ResumeWithRecommendationsSerializer(serializers.ModelSerializer):
    next_step = NextBestStepSerializer(read_only=True)
    career_path = CareerPathwaySerializer(read_only=True)
    
    class Meta:
        model = Resume
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')