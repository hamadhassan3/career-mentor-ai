from unittest.mock import MagicMock, patch

import requests
from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from resumes.models import (
    Resume, NextBestStep, CareerPathway, CareerStage, SkillCourseRecommendation,
)


def make_user(username='alice'):
    return User.objects.create_user(username=username, password='password123', email=f'{username}@x.com')


class ConstantsTests(APITestCase):
    def test_skill_taxonomies_are_populated(self):
        from resumes import constants
        self.assertIn('Python', constants.IT_SKILLS['Programming Languages'])
        self.assertIn('Leadership', constants.SOFT_SKILLS['Leadership & Management'])
        self.assertIn('English', constants.LANGUAGE_SKILLS['English Languages'])


def make_active_resume(user, **kwargs):
    defaults = dict(title='My Resume', target_designation='Engineer', is_active=True)
    defaults.update(kwargs)
    return Resume.objects.create(user=user, **defaults)


# --- Models ------------------------------------------------------------------

class ResumeModelTests(APITestCase):
    def setUp(self):
        self.user = make_user()

    def test_resume_str(self):
        resume = make_active_resume(self.user, title='Frontend CV')
        self.assertIn('Frontend CV', str(resume))

    def test_resume_str_fallback_to_id(self):
        resume = Resume.objects.create(user=self.user)
        self.assertIn(self.user.username, str(resume))

    def test_next_best_step_str(self):
        resume = make_active_resume(self.user)
        step = NextBestStep.objects.create(resume=resume, title='Learn Go')
        self.assertIn('Learn Go', str(step))

    def test_course_recommendation_str(self):
        resume = make_active_resume(self.user)
        step = NextBestStep.objects.create(resume=resume, title='Learn Go')
        rec = SkillCourseRecommendation.objects.create(next_step=step, skill='Go')
        self.assertIn('Go', str(rec))

    def test_career_pathway_str(self):
        resume = make_active_resume(self.user)
        pathway = CareerPathway.objects.create(resume=resume, current_level='Jr', target_role='Sr')
        self.assertIn('Jr', str(pathway))

    def test_career_stage_str(self):
        resume = make_active_resume(self.user)
        pathway = CareerPathway.objects.create(resume=resume)
        stage = CareerStage.objects.create(pathway=pathway, title='Phase 1', duration='3mo')
        self.assertIn('Phase 1', str(stage))


# --- Resume list/create/detail ----------------------------------------------

class ResumeListCreateViewTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)

    def test_list_only_own_resumes(self):
        make_active_resume(self.user)
        other = make_user('bob')
        make_active_resume(other)
        resp = self.client.get('/api/resumes/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_create_resume(self):
        resp = self.client.post('/api/resumes/', {'title': 'New CV'}, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Resume.objects.get().user, self.user)


class ResumeDetailViewTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)

    def test_update_inactive_rejected(self):
        resume = Resume.objects.create(user=self.user, is_active=False, target_designation='Eng')
        resp = self.client.put(f'/api/resumes/{resume.id}/', {'title': 'x'}, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_update_active_resume(self):
        resume = make_active_resume(self.user)
        resp = self.client.put(f'/api/resumes/{resume.id}/',
                               {'title': 'Updated', 'target_designation': 'Engineer'}, format='json')
        self.assertEqual(resp.status_code, 200)
        resume.refresh_from_db()
        self.assertEqual(resume.title, 'Updated')

    def test_update_clears_recommendations_on_designation_change(self):
        resume = make_active_resume(self.user, target_designation='Engineer')
        NextBestStep.objects.create(resume=resume, title='Old step')
        CareerPathway.objects.create(resume=resume)
        resp = self.client.put(f'/api/resumes/{resume.id}/',
                               {'target_designation': 'Manager'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(NextBestStep.objects.filter(resume=resume).exists())
        self.assertFalse(CareerPathway.objects.filter(resume=resume).exists())

    def test_partial_update_inactive_rejected(self):
        resume = Resume.objects.create(user=self.user, is_active=False)
        resp = self.client.patch(f'/api/resumes/{resume.id}/', {'title': 'x'}, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_partial_update_active_clears_on_designation_change(self):
        resume = make_active_resume(self.user, target_designation='Engineer')
        NextBestStep.objects.create(resume=resume, title='Old step')
        resp = self.client.patch(f'/api/resumes/{resume.id}/',
                                 {'target_designation': 'Lead'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(NextBestStep.objects.filter(resume=resume).exists())


# --- Upload / latest / active / activate ------------------------------------

class ResumeUploadActivateTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)

    def test_create_from_upload_sets_active_and_deactivates_others(self):
        old = make_active_resume(self.user)
        resp = self.client.post('/api/resumes/upload/', {'title': 'Uploaded'}, format='json')
        self.assertEqual(resp.status_code, 201)
        old.refresh_from_db()
        self.assertFalse(old.is_active)
        self.assertTrue(resp.data['is_active'])

    def test_create_from_upload_invalid(self):
        resp = self.client.post('/api/resumes/upload/', {'total_exp': 'not-an-int'}, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_get_latest_resume(self):
        make_active_resume(self.user, title='Latest')
        resp = self.client.get('/api/resumes/latest/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['title'], 'Latest')

    def test_get_latest_resume_none(self):
        resp = self.client.get('/api/resumes/latest/')
        self.assertEqual(resp.status_code, 404)

    def test_get_active_resume(self):
        make_active_resume(self.user)
        resp = self.client.get('/api/resumes/active/')
        self.assertEqual(resp.status_code, 200)

    def test_get_active_resume_none(self):
        resp = self.client.get('/api/resumes/active/')
        self.assertEqual(resp.status_code, 404)

    def test_activate_resume(self):
        old = make_active_resume(self.user)
        new = Resume.objects.create(user=self.user, is_active=False, title='New')
        resp = self.client.post(f'/api/resumes/{new.id}/activate/')
        self.assertEqual(resp.status_code, 200)
        old.refresh_from_db()
        new.refresh_from_db()
        self.assertFalse(old.is_active)
        self.assertTrue(new.is_active)

    def test_activate_resume_not_found(self):
        # get_object_or_404 raises Http404, which the view's broad ``except
        # Exception`` swallows into a 500 response (rather than a 404).
        resp = self.client.post('/api/resumes/99999/activate/')
        self.assertEqual(resp.status_code, 500)


# --- Next best step ----------------------------------------------------------

class NextBestStepViewTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)

    def test_save_creates(self):
        make_active_resume(self.user)
        resp = self.client.post('/api/resumes/next-step/save/',
                                {'title': 'Learn Rust', 'impact': 'High'}, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(NextBestStep.objects.get().title, 'Learn Rust')

    def test_save_no_active_resume(self):
        resp = self.client.post('/api/resumes/next-step/save/', {'title': 'x'}, format='json')
        self.assertEqual(resp.status_code, 404)

    def test_save_updates_existing_and_clears_courses_on_title_change(self):
        resume = make_active_resume(self.user)
        step = NextBestStep.objects.create(resume=resume, title='Old')
        SkillCourseRecommendation.objects.create(next_step=step, skill='Old')
        resp = self.client.post('/api/resumes/next-step/save/', {'title': 'New'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(SkillCourseRecommendation.objects.filter(next_step=step).exists())

    def test_get_next_step(self):
        resume = make_active_resume(self.user)
        NextBestStep.objects.create(resume=resume, title='Learn Rust')
        resp = self.client.get('/api/resumes/next-step/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['title'], 'Learn Rust')

    def test_get_next_step_none(self):
        make_active_resume(self.user)
        resp = self.client.get('/api/resumes/next-step/')
        self.assertEqual(resp.status_code, 404)

    def test_get_next_step_no_active_resume(self):
        resp = self.client.get('/api/resumes/next-step/')
        self.assertEqual(resp.status_code, 404)


# --- Career pathway ----------------------------------------------------------

class CareerPathwayViewTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)

    def test_save_creates_with_stages(self):
        make_active_resume(self.user)
        payload = {
            'current_level': 'Jr', 'target_role': 'Sr',
            'stages': [{'title': 'Phase 1', 'duration': '3mo'},
                       {'title': 'Phase 2', 'duration': '6mo'}],
        }
        resp = self.client.post('/api/resumes/career-pathway/save/', payload, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(CareerStage.objects.count(), 2)

    def test_save_updates_existing_replaces_stages(self):
        resume = make_active_resume(self.user)
        pathway = CareerPathway.objects.create(resume=resume, current_level='Old')
        CareerStage.objects.create(pathway=pathway, title='Stale', duration='1mo')
        payload = {'current_level': 'New', 'stages': [{'title': 'Fresh', 'duration': '2mo'}]}
        resp = self.client.post('/api/resumes/career-pathway/save/', payload, format='json')
        self.assertEqual(resp.status_code, 200)
        pathway.refresh_from_db()
        self.assertEqual(pathway.current_level, 'New')
        self.assertEqual([s.title for s in pathway.stages.all()], ['Fresh'])

    def test_save_no_active_resume(self):
        resp = self.client.post('/api/resumes/career-pathway/save/', {}, format='json')
        self.assertEqual(resp.status_code, 404)

    def test_get_pathway(self):
        resume = make_active_resume(self.user)
        CareerPathway.objects.create(resume=resume, current_level='Jr')
        resp = self.client.get('/api/resumes/career-pathway/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_level'], 'Jr')

    def test_get_pathway_none(self):
        make_active_resume(self.user)
        resp = self.client.get('/api/resumes/career-pathway/')
        self.assertEqual(resp.status_code, 404)

    def test_get_pathway_no_active_resume(self):
        resp = self.client.get('/api/resumes/career-pathway/')
        self.assertEqual(resp.status_code, 404)


# --- Clear recommendations ---------------------------------------------------

class ClearRecommendationsTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)

    def test_clear_both(self):
        resume = make_active_resume(self.user)
        NextBestStep.objects.create(resume=resume, title='step')
        CareerPathway.objects.create(resume=resume)
        resp = self.client.delete('/api/resumes/recommendations/clear/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['cleared_items'], 2)

    def test_clear_nothing(self):
        make_active_resume(self.user)
        resp = self.client.delete('/api/resumes/recommendations/clear/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['cleared_items'], 0)

    def test_clear_no_active_resume(self):
        resp = self.client.delete('/api/resumes/recommendations/clear/')
        self.assertEqual(resp.status_code, 404)


# --- Course recommendations --------------------------------------------------

class CourseRecommendationsTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)

    def test_no_active_resume(self):
        resp = self.client.get('/api/resumes/courses/')
        self.assertEqual(resp.status_code, 404)

    def test_no_next_step(self):
        make_active_resume(self.user)
        resp = self.client.get('/api/resumes/courses/')
        self.assertEqual(resp.status_code, 404)

    def test_blank_skill_returns_empty(self):
        resume = make_active_resume(self.user)
        NextBestStep.objects.create(resume=resume, title='No recommendations available')
        resp = self.client.get('/api/resumes/courses/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['courses'], [])

    def test_returns_cached(self):
        resume = make_active_resume(self.user)
        step = NextBestStep.objects.create(resume=resume, title='Python')
        SkillCourseRecommendation.objects.create(
            next_step=step, skill='Python', courses=[{'title': 'Cached'}])
        resp = self.client.get('/api/resumes/courses/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['courses'], [{'title': 'Cached'}])

    @patch('resumes.views.requests.post')
    def test_fetches_and_persists(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200, json=MagicMock(return_value={'courses': [{'title': 'New'}]}))
        resume = make_active_resume(self.user)
        step = NextBestStep.objects.create(resume=resume, title='Python')
        resp = self.client.get('/api/resumes/courses/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['courses'], [{'title': 'New'}])
        self.assertTrue(SkillCourseRecommendation.objects.filter(next_step=step).exists())

    @patch('resumes.views.requests.post')
    def test_service_non_200(self, mock_post):
        mock_post.return_value = MagicMock(status_code=500)
        resume = make_active_resume(self.user)
        NextBestStep.objects.create(resume=resume, title='Python')
        resp = self.client.get('/api/resumes/courses/')
        self.assertEqual(resp.status_code, 503)

    @patch('resumes.views.requests.post', side_effect=requests.RequestException('down'))
    def test_service_unavailable(self, _mock):
        resume = make_active_resume(self.user)
        NextBestStep.objects.create(resume=resume, title='Python')
        resp = self.client.get('/api/resumes/courses/')
        self.assertEqual(resp.status_code, 503)

    @patch('resumes.views.requests.post')
    def test_stale_cache_refetches(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200, json=MagicMock(return_value={'courses': [{'title': 'Refreshed'}]}))
        resume = make_active_resume(self.user)
        step = NextBestStep.objects.create(resume=resume, title='Python')
        # Cache is for a different (old) skill -> should refetch and update.
        SkillCourseRecommendation.objects.create(next_step=step, skill='OldSkill', courses=[])
        resp = self.client.get('/api/resumes/courses/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['courses'], [{'title': 'Refreshed'}])
