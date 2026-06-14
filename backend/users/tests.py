import pyotp
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail, signing
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APITestCase

from users.models import TOTPDevice
from users.serializers import RegisterSerializer, UserSerializer


def make_user(username='alice', password='password123', email='alice@example.com', **extra):
    return User.objects.create_user(username=username, password=password, email=email, **extra)


class TOTPDeviceModelTests(APITestCase):
    def test_str_pending_and_confirmed(self):
        user = make_user()
        device = TOTPDevice.objects.create(user=user, secret=pyotp.random_base32())
        self.assertIn('pending', str(device))
        device.confirmed = True
        device.save()
        self.assertIn('confirmed', str(device))


class RegisterSerializerTests(APITestCase):
    def test_create_builds_user_with_hashed_password(self):
        serializer = RegisterSerializer(data={
            'username': 'bob', 'email': 'bob@example.com',
            'password': 'supersecret', 'first_name': 'Bob', 'last_name': 'Jones',
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertTrue(user.check_password('supersecret'))
        self.assertEqual(user.first_name, 'Bob')

    def test_duplicate_email_rejected(self):
        make_user(email='dupe@example.com')
        serializer = RegisterSerializer(data={
            'username': 'other', 'email': 'dupe@example.com', 'password': 'supersecret',
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


class UserSerializerTests(APITestCase):
    def test_totp_confirmed_flag(self):
        user = make_user()
        self.assertFalse(UserSerializer(user).data['totp_confirmed'])
        TOTPDevice.objects.create(user=user, secret=pyotp.random_base32(), confirmed=True)
        user.refresh_from_db()
        self.assertTrue(UserSerializer(user).data['totp_confirmed'])


class RegisterViewTests(APITestCase):
    def test_register_creates_user(self):
        resp = self.client.post('/api/auth/register/', {
            'username': 'newuser', 'email': 'new@example.com', 'password': 'supersecret',
        })
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(User.objects.filter(username='newuser').exists())


class LoginViewTests(APITestCase):
    def test_missing_credentials(self):
        resp = self.client.post('/api/auth/login/', {'username': 'x'})
        self.assertEqual(resp.status_code, 400)

    def test_unknown_user(self):
        resp = self.client.post('/api/auth/login/', {'username': 'ghost', 'password': 'x'})
        self.assertEqual(resp.status_code, 401)

    def test_wrong_password(self):
        make_user()
        resp = self.client.post('/api/auth/login/', {'username': 'alice', 'password': 'wrong'})
        self.assertEqual(resp.status_code, 401)

    def test_login_without_totp_issues_tokens(self):
        make_user()
        resp = self.client.post('/api/auth/login/', {'username': 'alice', 'password': 'password123'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('access', resp.data)
        self.assertTrue(resp.data['totp_setup_required'])

    def test_login_with_confirmed_totp_requires_second_factor(self):
        user = make_user()
        TOTPDevice.objects.create(user=user, secret=pyotp.random_base32(), confirmed=True)
        resp = self.client.post('/api/auth/login/', {'username': 'alice', 'password': 'password123'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data['totp_required'])
        self.assertIn('totp_token', resp.data)


class TOTPLoginVerifyViewTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.secret = pyotp.random_base32()
        self.device = TOTPDevice.objects.create(user=self.user, secret=self.secret, confirmed=True)
        self.token = signing.dumps(self.user.pk, salt='totp-login')

    def test_invalid_token(self):
        resp = self.client.post('/api/auth/totp/login/', {
            'totp_token': 'garbage', 'code': '123456',
        })
        self.assertEqual(resp.status_code, 400)

    def test_totp_not_set_up(self):
        self.device.confirmed = False
        self.device.save()
        resp = self.client.post('/api/auth/totp/login/', {
            'totp_token': self.token, 'code': pyotp.TOTP(self.secret).now(),
        })
        self.assertEqual(resp.status_code, 400)

    def test_invalid_code(self):
        resp = self.client.post('/api/auth/totp/login/', {
            'totp_token': self.token, 'code': '000000',
        })
        self.assertEqual(resp.status_code, 400)

    def test_valid_code_returns_tokens(self):
        resp = self.client.post('/api/auth/totp/login/', {
            'totp_token': self.token, 'code': pyotp.TOTP(self.secret).now(),
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)


class TOTPSetupViewTests(APITestCase):
    def test_creates_device_and_returns_uri(self):
        user = make_user()
        self.client.force_authenticate(user=user)
        resp = self.client.get('/api/auth/totp/setup/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('provisioning_uri', resp.data)
        self.assertTrue(TOTPDevice.objects.filter(user=user).exists())

    def test_regenerates_secret_when_unconfirmed(self):
        user = make_user()
        device = TOTPDevice.objects.create(user=user, secret='OLDSECRET', confirmed=False)
        self.client.force_authenticate(user=user)
        resp = self.client.get('/api/auth/totp/setup/')
        device.refresh_from_db()
        self.assertNotEqual(device.secret, 'OLDSECRET')
        self.assertEqual(resp.data['secret'], device.secret)

    def test_keeps_secret_when_confirmed(self):
        user = make_user()
        TOTPDevice.objects.create(user=user, secret='KEEPSECRET', confirmed=True)
        self.client.force_authenticate(user=user)
        resp = self.client.get('/api/auth/totp/setup/')
        self.assertEqual(resp.data['secret'], 'KEEPSECRET')

    def test_requires_authentication(self):
        self.assertEqual(self.client.get('/api/auth/totp/setup/').status_code, 401)


class TOTPConfirmViewTests(APITestCase):
    def test_no_device(self):
        user = make_user()
        self.client.force_authenticate(user=user)
        resp = self.client.post('/api/auth/totp/confirm/', {'code': '123456'})
        self.assertEqual(resp.status_code, 400)

    def test_invalid_code(self):
        user = make_user()
        TOTPDevice.objects.create(user=user, secret=pyotp.random_base32())
        self.client.force_authenticate(user=user)
        resp = self.client.post('/api/auth/totp/confirm/', {'code': '000000'})
        self.assertEqual(resp.status_code, 400)

    def test_valid_code_confirms(self):
        user = make_user()
        secret = pyotp.random_base32()
        device = TOTPDevice.objects.create(user=user, secret=secret)
        self.client.force_authenticate(user=user)
        resp = self.client.post('/api/auth/totp/confirm/', {'code': pyotp.TOTP(secret).now()})
        self.assertEqual(resp.status_code, 200)
        device.refresh_from_db()
        self.assertTrue(device.confirmed)


class ChangePasswordViewTests(APITestCase):
    def test_wrong_current_password(self):
        user = make_user()
        self.client.force_authenticate(user=user)
        resp = self.client.post('/api/auth/change-password/', {
            'current_password': 'nope', 'new_password': 'brandnewpass',
        })
        self.assertEqual(resp.status_code, 400)

    def test_successful_change(self):
        user = make_user()
        self.client.force_authenticate(user=user)
        resp = self.client.post('/api/auth/change-password/', {
            'current_password': 'password123', 'new_password': 'brandnewpass',
        })
        self.assertEqual(resp.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password('brandnewpass'))


class MeViewTests(APITestCase):
    def test_returns_current_user(self):
        user = make_user()
        self.client.force_authenticate(user=user)
        resp = self.client.get('/api/auth/me/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['username'], 'alice')


class PasswordResetRequestViewTests(APITestCase):
    def test_sends_email_for_existing_user(self):
        make_user(email='reset@example.com')
        resp = self.client.post('/api/auth/password-reset/', {'email': 'reset@example.com'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

    def test_silent_for_unknown_email(self):
        resp = self.client.post('/api/auth/password-reset/', {'email': 'nobody@example.com'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)


class PasswordResetConfirmViewTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)

    def test_invalid_uid(self):
        resp = self.client.post('/api/auth/password-reset/confirm/', {
            'uid': 'not-base64!!', 'token': self.token, 'new_password': 'newpassword1',
        })
        self.assertEqual(resp.status_code, 400)

    def test_invalid_token(self):
        resp = self.client.post('/api/auth/password-reset/confirm/', {
            'uid': self.uid, 'token': 'bad-token', 'new_password': 'newpassword1',
        })
        self.assertEqual(resp.status_code, 400)

    def test_valid_reset(self):
        resp = self.client.post('/api/auth/password-reset/confirm/', {
            'uid': self.uid, 'token': self.token, 'new_password': 'newpassword1',
        })
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword1'))
