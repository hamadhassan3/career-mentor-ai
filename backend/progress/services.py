import boto3
import uuid
from django.conf import settings
from botocore.exceptions import NoCredentialsError, ClientError
from django.core.exceptions import ImproperlyConfigured


class S3UploadService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION
        )
        self.bucket_name = settings.AWS_S3_BUCKET_NAME
        
    def upload_progress_image(self, image_file, user_id):
        try:
            # Generate unique filename
            file_extension = image_file.name.split('.')[-1].lower()
            filename = f"progress/{user_id}/{uuid.uuid4()}.{file_extension}"
            
            # Upload to S3
            self.s3_client.upload_fileobj(
                image_file,
                self.bucket_name,
                filename,
                ExtraArgs={
                    'ContentType': image_file.content_type
                }
            )
            
            # Generate presigned URL (valid for 1 year)
            image_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': filename},
                ExpiresIn=31536000  # 1 year in seconds
            )
            
            return {
                'image_url': image_url,
                's3_key': filename,
                'success': True
            }
            
        except NoCredentialsError:
            return {
                'error': 'AWS credentials not configured',
                'success': False
            }
        except ClientError as e:
            return {
                'error': f'Failed to upload to S3: {str(e)}',
                'success': False
            }
        except Exception as e:
            return {
                'error': f'Unexpected error: {str(e)}',
                'success': False
            }
    
    def delete_progress_image(self, s3_key):
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except Exception as e:
            print(f"Failed to delete S3 object {s3_key}: {str(e)}")
            return False