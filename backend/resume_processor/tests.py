from unittest.mock import MagicMock, patch

import requests
from django.test import TestCase

import resume_processor.views as views


def mock_response(content=b'{"ok": true}', status_code=200, content_type='application/json', headers=None):
    resp = MagicMock()
    resp.content = content
    resp.status_code = status_code
    base_headers = {'content-type': content_type}
    if headers:
        base_headers.update(headers)
    resp.headers = base_headers
    return resp


class ProxyConfigurationTests(TestCase):
    def test_not_configured_returns_500(self):
        with patch.object(views, 'RESUME_PROCESSOR_API_BASE_URL', None):
            resp = self.client.post('/api/resume-processor/predict', {}, content_type='application/json')
        self.assertEqual(resp.status_code, 500)
        self.assertIn('not configured', resp.json()['error'])


@patch.object(views, 'RESUME_PROCESSOR_API_BASE_URL', 'http://service.local/')
class ProxyMethodTests(TestCase):
    @patch('resume_processor.views.requests.get')
    def test_get_proxy(self, mock_get):
        mock_get.return_value = mock_response(headers={'ETag': 'abc', 'Cache-Control': 'no-cache'})
        resp = self.client.get('/api/resume-processor/skills/all?foo=bar')
        self.assertEqual(resp.status_code, 200)
        mock_get.assert_called_once()
        self.assertTrue(mock_get.call_args.args[0].endswith('/skills/all'))

    @patch('resume_processor.views.requests.post')
    def test_post_json_proxy(self, mock_post):
        mock_post.return_value = mock_response()
        resp = self.client.post('/api/resume-processor/predict',
                                data='{"x": 1}', content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        mock_post.assert_called_once()

    @patch('resume_processor.views.requests.post')
    def test_post_multipart_proxy(self, mock_post):
        mock_post.return_value = mock_response()
        from django.core.files.uploadedfile import SimpleUploadedFile
        upload = SimpleUploadedFile('cv.pdf', b'%PDF-1.4 data', content_type='application/pdf')
        resp = self.client.post('/api/resume-processor/resumes/upload',
                                {'field': 'value', 'file': upload})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('files', mock_post.call_args.kwargs)
        self.assertIn('file', mock_post.call_args.kwargs['files'])

    @patch('resume_processor.views.requests.get')
    def test_service_unavailable(self, mock_get):
        mock_get.side_effect = requests.RequestException('down')
        resp = self.client.get('/api/resume-processor/skills/it')
        self.assertEqual(resp.status_code, 503)
        self.assertIn('Service unavailable', resp.json()['error'])

    @patch('resume_processor.views.requests.get')
    def test_generic_error(self, mock_get):
        mock_get.side_effect = RuntimeError('weird')
        resp = self.client.get('/api/resume-processor/skills/soft')
        self.assertEqual(resp.status_code, 500)
        self.assertIn('Internal server error', resp.json()['error'])


class ProxyDirectMethodTests(TestCase):
    """Exercise PUT / DELETE / unsupported branches via the proxy_request helper directly."""

    def setUp(self):
        self.patcher = patch.object(views, 'RESUME_PROCESSOR_API_BASE_URL', 'http://service.local')
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def _request(self, method, body=b'', content_type='application/json'):
        from django.test import RequestFactory
        rf = RequestFactory()
        builder = getattr(rf, method.lower())
        if method in ('PUT',):
            return builder('/x', data=body, content_type=content_type)
        return builder('/x')

    @patch('resume_processor.views.requests.put')
    def test_put(self, mock_put):
        mock_put.return_value = mock_response()
        req = self._request('PUT', body=b'{"a":1}')
        resp = views.proxy_request(req, 'path')
        self.assertEqual(resp.status_code, 200)
        mock_put.assert_called_once()

    @patch('resume_processor.views.requests.delete')
    def test_delete(self, mock_delete):
        mock_delete.return_value = mock_response()
        req = self._request('DELETE')
        resp = views.proxy_request(req, 'path')
        self.assertEqual(resp.status_code, 200)
        mock_delete.assert_called_once()

    def test_method_not_allowed(self):
        from django.test import RequestFactory
        req = RequestFactory().generic('PATCH', '/x')
        resp = views.proxy_request(req, 'path')
        self.assertEqual(resp.status_code, 405)

    @patch('resume_processor.views.requests.get')
    def test_header_forwarding_excludes_host(self, mock_get):
        mock_get.return_value = mock_response()
        from django.test import RequestFactory
        req = RequestFactory().get('/x', HTTP_HOST='ignore.me', HTTP_AUTHORIZATION='Bearer tok')
        views.proxy_request(req, 'path')
        sent_headers = mock_get.call_args.kwargs['headers']
        self.assertIn('Authorization', sent_headers)
        self.assertNotIn('Host', sent_headers)


class EndpointWrapperTests(TestCase):
    """Each thin wrapper should delegate to proxy_request with the right path."""

    @patch('resume_processor.views.proxy_request')
    def test_all_wrappers(self, mock_proxy):
        from django.http import JsonResponse
        mock_proxy.return_value = JsonResponse({'ok': True})
        cases = [
            ('post', '/api/resume-processor/resumes/upload', 'resumes/upload'),
            ('get', '/api/resume-processor/skills/all', 'skills/all'),
            ('get', '/api/resume-processor/skills/it', 'skills/it'),
            ('get', '/api/resume-processor/skills/soft', 'skills/soft'),
            ('get', '/api/resume-processor/skills/languages', 'skills/languages'),
            ('get', '/api/resume-processor/designations', 'designations'),
            ('post', '/api/resume-processor/predict', 'predict'),
            ('post', '/api/resume-processor/predict_next_skill', 'predict_next_skill'),
        ]
        for method, url, expected_path in cases:
            mock_proxy.reset_mock()
            getattr(self.client, method)(url)
            self.assertEqual(mock_proxy.call_args.args[1], expected_path)
