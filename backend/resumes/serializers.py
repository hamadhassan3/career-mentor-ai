from rest_framework import serializers
from .models import Resume


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class ResumeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ('id', 'title', 'target_designation', 'original_filename', 'is_active', 'created_at', 'updated_at')