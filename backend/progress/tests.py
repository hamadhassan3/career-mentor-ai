import io
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError, NoCredentialsError
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APITestCase


def real_png_upload(name='shot.png'):
    """A genuine PNG so DRF's ImageField (Pillow) accepts it."""
    buffer = io.BytesIO()
    Image.new('RGB', (2, 2), color='red').save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')

from progress.models import ProgressAchievement
from progress.serializers import (
    ProgressAchievementCreateSerializer, ProgressAchievementSerializer,
)
from progress.services import S3UploadService


def make_user(username='alice'):
    return User.objects.create_user(username=username, password='password123', email=f'{username}@x.com')


def make_image_file(name='shot.png', content_type='image/png', size=1024):
    f = io.BytesIO(b'x' * size)
    f.name = name
    upload = MagicMock()
    upload.name = name
    upload.content_type = content_type
    upload.size = size
    upload.read = f.read
    return upload


# --- Model -------------------------------------------------------------------

class ProgressModelTests(APITestCase):
    def test_str(self):
        user = make_user()
        ach = ProgressAchievement.objects.create(
            user=user, skill='Python', image_url='http://x/img.png', s3_key='k')
        self.assertIn('Python', str(ach))


# --- Serializers -------------------------------------------------------------

class ProgressSerializerTests(APITestCase):
    def test_validate_skill_blank(self):
        s = ProgressAchievementCreateSerializer()
        with self.assertRaises(Exception):
            s.validate_skill('   ')

    def test_validate_skill_strips(self):
        s = ProgressAchievementCreateSerializer()
        self.assertEqual(s.validate_skill('  Go  '), 'Go')

    def test_validate_image_too_large(self):
        s = ProgressAchievementCreateSerializer()
        big = make_image_file(size=6 * 1024 * 1024)
        with self.assertRaises(Exception):
            s.validate_image(big)

    def test_validate_image_bad_format(self):
        s = ProgressAchievementCreateSerializer()
        with self.assertRaises(Exception):
            s.validate_image(make_image_file(content_type='application/pdf'))

    def test_validate_image_ok(self):
        s = ProgressAchievementCreateSerializer()
        img = make_image_file()
        self.assertIs(s.validate_image(img), img)

    @patch('progress.serializers.S3UploadService')
    def test_get_image_url_presigned(self, mock_service):
        mock_service.return_value.s3_client.generate_presigned_url.return_value = 'http://signed'
        user = make_user()
        ach = ProgressAchievement.objects.create(
            user=user, skill='Go', image_url='http://stored', s3_key='k')
        data = ProgressAchievementSerializer(ach).data
        self.assertEqual(data['image_url'], 'http://signed')

    @patch('progress.serializers.S3UploadService', side_effect=RuntimeError('boom'))
    def test_get_image_url_fallback(self, _mock):
        user = make_user()
        ach = ProgressAchievement.objects.create(
            user=user, skill='Go', image_url='http://stored', s3_key='k')
        data = ProgressAchievementSerializer(ach).data
        self.assertEqual(data['image_url'], 'http://stored')


# --- S3UploadService ---------------------------------------------------------

class S3UploadServiceTests(APITestCase):
    def test_upload_success(self):
        with patch('progress.services.boto3.client') as mock_client:
            mock_client.return_value.generate_presigned_url.return_value = 'http://signed'
            service = S3UploadService()
            result = service.upload_progress_image(make_image_file(), user_id=1)
        self.assertTrue(result['success'])
        self.assertEqual(result['image_url'], 'http://signed')
        self.assertTrue(result['s3_key'].startswith('progress/1/'))

    def test_upload_no_credentials(self):
        with patch('progress.services.boto3.client') as mock_client:
            mock_client.return_value.upload_fileobj.side_effect = NoCredentialsError()
            service = S3UploadService()
            result = service.upload_progress_image(make_image_file(), user_id=1)
        self.assertFalse(result['success'])
        self.assertIn('credentials', result['error'])

    def test_upload_client_error(self):
        with patch('progress.services.boto3.client') as mock_client:
            mock_client.return_value.upload_fileobj.side_effect = ClientError(
                {'Error': {'Code': '500', 'Message': 'fail'}}, 'PutObject')
            service = S3UploadService()
            result = service.upload_progress_image(make_image_file(), user_id=1)
        self.assertFalse(result['success'])
        self.assertIn('Failed to upload', result['error'])

    def test_upload_unexpected_error(self):
        with patch('progress.services.boto3.client') as mock_client:
            mock_client.return_value.upload_fileobj.side_effect = RuntimeError('weird')
            service = S3UploadService()
            result = service.upload_progress_image(make_image_file(), user_id=1)
        self.assertFalse(result['success'])
        self.assertIn('Unexpected error', result['error'])

    def test_delete_success(self):
        with patch('progress.services.boto3.client'):
            service = S3UploadService()
            self.assertTrue(service.delete_progress_image('some-key'))

    def test_delete_failure(self):
        with patch('progress.services.boto3.client') as mock_client:
            mock_client.return_value.delete_object.side_effect = RuntimeError('boom')
            service = S3UploadService()
            self.assertFalse(service.delete_progress_image('some-key'))


# --- Views -------------------------------------------------------------------

class ProgressViewTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)

    @patch('progress.serializers.S3UploadService')
    def test_list_achievements(self, mock_service):
        mock_service.return_value.s3_client.generate_presigned_url.return_value = 'http://signed'
        ProgressAchievement.objects.create(
            user=self.user, skill='Go', image_url='http://x', s3_key='k')
        resp = self.client.get('/api/progress/achievements/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_create_invalid(self):
        resp = self.client.post('/api/progress/achievements/create/', {'skill': ''}, format='multipart')
        self.assertEqual(resp.status_code, 400)

    @patch('progress.views.S3UploadService')
    def test_create_upload_failure(self, mock_service):
        mock_service.return_value.upload_progress_image.return_value = {
            'success': False, 'error': 'S3 down'}
        resp = self.client.post('/api/progress/achievements/create/',
                                {'skill': 'Go', 'image': real_png_upload()}, format='multipart')
        self.assertEqual(resp.status_code, 500)

    @patch('progress.serializers.S3UploadService')
    @patch('progress.views.S3UploadService')
    def test_create_success(self, mock_view_service, mock_ser_service):
        mock_view_service.return_value.upload_progress_image.return_value = {
            'success': True, 'image_url': 'http://img', 's3_key': 'progress/1/x.png'}
        mock_ser_service.return_value.s3_client.generate_presigned_url.return_value = 'http://signed'
        resp = self.client.post('/api/progress/achievements/create/',
                                {'skill': 'Go', 'image': real_png_upload()}, format='multipart')
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(ProgressAchievement.objects.filter(skill='Go').exists())

    @patch('progress.views.S3UploadService')
    def test_delete_achievement(self, mock_service):
        mock_service.return_value.delete_progress_image.return_value = True
        ach = ProgressAchievement.objects.create(
            user=self.user, skill='Go', image_url='http://x', s3_key='k')
        resp = self.client.delete(f'/api/progress/achievements/{ach.id}/delete/')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(ProgressAchievement.objects.filter(id=ach.id).exists())

    def test_delete_not_found(self):
        resp = self.client.delete('/api/progress/achievements/99999/delete/')
        self.assertEqual(resp.status_code, 404)
