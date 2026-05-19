from rest_framework import serializers
from .models import ProgressAchievement
from .services import S3UploadService


class ProgressAchievementSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProgressAchievement
        fields = ['id', 'skill', 'image_url', 'created_at']
        read_only_fields = ['id', 'image_url', 'created_at']
    
    def get_image_url(self, obj):
        # Generate fresh presigned URL for each request
        try:
            s3_service = S3UploadService()
            presigned_url = s3_service.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': s3_service.bucket_name, 'Key': obj.s3_key},
                ExpiresIn=3600  # 1 hour
            )
            return presigned_url
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return obj.image_url  # Fallback to stored URL


class ProgressAchievementCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True)
    
    class Meta:
        model = ProgressAchievement
        fields = ['skill', 'image']
        
    def validate_skill(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Skill is required")
        return value.strip()
        
    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError("Image is required")
        
        # Validate image size (max 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Image size must be less than 5MB")
            
        # Validate image format
        allowed_formats = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if value.content_type not in allowed_formats:
            raise serializers.ValidationError("Only JPEG, PNG, and WebP images are allowed")
            
        return value