from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase

from nudge.models import Nudge
from nudge.services.nudge_service import NudgeService


def make_user(username='alice'):
    return User.objects.create_user(username=username, password='password123', email=f'{username}@x.com',
                                    first_name='Al', last_name='Ice')


class NudgeModelTests(APITestCase):
    def setUp(self):
        self.user = make_user()

    def test_str(self):
        nudge = Nudge.objects.create(user=self.user, content='Do it')
        self.assertIn(self.user.username, str(nudge))

    def test_is_stale_false_for_fresh(self):
        nudge = Nudge.objects.create(user=self.user, content='fresh')
        self.assertFalse(nudge.is_stale)

    def test_is_stale_true_for_old(self):
        nudge = Nudge.objects.create(user=self.user, content='old')
        Nudge.objects.filter(pk=nudge.pk).update(created_at=timezone.now() - timedelta(days=2))
        nudge.refresh_from_db()
        self.assertTrue(nudge.is_stale)

    def test_get_latest_for_user(self):
        Nudge.objects.create(user=self.user, content='first')
        latest = Nudge.objects.create(user=self.user, content='second')
        self.assertEqual(Nudge.get_latest_for_user(self.user).id, latest.id)


class NudgeServiceTests(APITestCase):
    def setUp(self):
        self.user = make_user()

    def test_get_or_generate_returns_fresh_existing(self):
        Nudge.objects.create(user=self.user, content='still good')
        content, is_new = NudgeService.get_or_generate_nudge(self.user)
        self.assertEqual(content, 'still good')
        self.assertFalse(is_new)

    @patch('nudge.services.nudge_service.llm_service')
    def test_get_or_generate_creates_when_stale(self, mock_llm):
        mock_llm.generate_response.return_value = 'Brand new nudge'
        mock_llm.model_name = 'm'
        old = Nudge.objects.create(user=self.user, content='old')
        Nudge.objects.filter(pk=old.pk).update(created_at=timezone.now() - timedelta(days=2))
        content, is_new = NudgeService.get_or_generate_nudge(self.user)
        self.assertEqual(content, 'Brand new nudge')
        self.assertTrue(is_new)

    @patch('nudge.services.nudge_service.Nudge.get_latest_for_user', side_effect=RuntimeError('boom'))
    def test_get_or_generate_fallback_on_error(self, _mock):
        content, is_new = NudgeService.get_or_generate_nudge(self.user)
        self.assertIn('Stay focused', content)
        self.assertFalse(is_new)

    @patch('nudge.services.nudge_service.llm_service')
    def test_generate_new_nudge_success(self, mock_llm):
        mock_llm.generate_response.return_value = '  Punchy nudge  '
        mock_llm.model_name = 'm'
        content, is_new = NudgeService.generate_new_nudge(self.user)
        self.assertEqual(content, 'Punchy nudge')
        self.assertTrue(is_new)
        self.assertEqual(Nudge.objects.filter(user=self.user).count(), 1)

    @patch('nudge.services.nudge_service.llm_service')
    def test_generate_new_nudge_truncates_long_output(self, mock_llm):
        mock_llm.generate_response.return_value = 'x' * 400
        mock_llm.model_name = 'm'
        content, _ = NudgeService.generate_new_nudge(self.user)
        self.assertTrue(content.endswith('...'))
        self.assertEqual(len(content), 300)

    @patch('nudge.services.nudge_service.llm_service')
    def test_generate_new_nudge_fallback_on_error(self, mock_llm):
        mock_llm.generate_response.side_effect = RuntimeError('boom')
        mock_llm.model_name = 'm'
        content, is_new = NudgeService.generate_new_nudge(self.user)
        self.assertIn('career journey is unique', content)
        self.assertTrue(is_new)

    @patch('nudge.services.nudge_service.NudgeService.generate_new_nudge', return_value=('regen', True))
    def test_force_regenerate(self, _mock):
        self.assertEqual(NudgeService.force_regenerate_nudge(self.user), 'regen')

    @patch('nudge.services.nudge_service.NudgeService.generate_new_nudge', side_effect=RuntimeError('boom'))
    def test_force_regenerate_fallback(self, _mock):
        self.assertIn('Keep pushing forward', NudgeService.force_regenerate_nudge(self.user))


class NudgeViewTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)

    @patch('nudge.views.nudge_service.get_or_generate_nudge', return_value=('today nudge', True))
    def test_get_success(self, _mock):
        resp = self.client.get('/api/nudge/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['nudge'], 'today nudge')
        self.assertTrue(resp.data['is_new'])

    @patch('nudge.views.nudge_service.get_or_generate_nudge', side_effect=RuntimeError('boom'))
    def test_get_error(self, _mock):
        resp = self.client.get('/api/nudge/')
        self.assertEqual(resp.status_code, 500)

    @patch('nudge.views.nudge_service.force_regenerate_nudge', return_value='regenerated')
    def test_post_success(self, _mock):
        resp = self.client.post('/api/nudge/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['nudge'], 'regenerated')

    @patch('nudge.views.nudge_service.force_regenerate_nudge', side_effect=RuntimeError('boom'))
    def test_post_error(self, _mock):
        resp = self.client.post('/api/nudge/')
        self.assertEqual(resp.status_code, 500)
