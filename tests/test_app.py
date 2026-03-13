import os
import sys
import unittest
from unittest.mock import patch


BACKEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'backend')
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import create_app  # noqa: E402
from job_scam_analyzer import analyze_job_text  # noqa: E402
from flask_jwt_extended import create_access_token  # noqa: E402


class JobScamAnalyzerTests(unittest.TestCase):
    def test_flags_high_risk_job_post(self):
        result = analyze_job_text(
            'Work from home. Earn $500 per day. No interview. Send training fee today using UPI or crypto.'
        )

        self.assertEqual(result['risk_level'], 'High')
        self.assertGreaterEqual(result['score'], 55)
        self.assertTrue(result['red_flags'])

    def test_recognizes_lower_risk_job_post(self):
        result = analyze_job_text(
            'Apply on our official career page. No fee required. Screening call and technical interview included.'
        )

        self.assertIn(result['risk_level'], {'Low', 'Medium'})
        self.assertLess(result['score'], 55)


class ApiTests(unittest.TestCase):
    def setUp(self):
        with patch('app.init_db'), patch('app.start_scheduler'):
            self.app = create_app()
        self.client = self.app.test_client()

    def test_job_scam_endpoint_is_public(self):
        response = self.client.post(
            '/api/job-scam/check',
            json={'title': 'Remote Role', 'content': 'Immediate joining. Send processing fee today.'},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload['title'], 'Remote Role')
        self.assertIn('risk_level', payload)

    def test_stats_summary_is_available_without_login(self):
        fake_results = [
            {'cnt': 8},
            {'cnt': 3},
            {'cnt': 2},
            {'cnt': 1},
        ]

        with patch('api.stats.execute', side_effect=fake_results):
            response = self.client.get('/api/stats/summary')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                'total_scans': 8,
                'malware_detected': 2,
                'vulnerability_reports': 3,
                'fraud_detected': 1,
            },
        )

    def test_profile_update_round_trip(self):
        with patch('auth.routes.execute') as mock_execute:
            mock_execute.side_effect = [
                {
                    'id': 1,
                    'username': 'alice',
                    'password': 'hashed',
                    'role': 'user',
                    'tenant_id': 'default',
                    'full_name': '',
                    'bio': '',
                    'avatar_url': '',
                    'google_url': '',
                    'facebook_url': '',
                    'linkedin_url': '',
                    'github_url': '',
                },
                None,
                {
                    'id': 1,
                    'username': 'alice',
                    'password': 'hashed',
                    'role': 'user',
                    'tenant_id': 'default',
                    'full_name': 'Alice Doe',
                    'bio': 'Researcher',
                    'avatar_url': 'data:image/png;base64,abc',
                    'google_url': 'https://google.com',
                    'facebook_url': '',
                    'linkedin_url': 'https://linkedin.com/in/alice',
                    'github_url': 'https://github.com/alice',
                },
            ]

            with self.app.app_context():
                token = create_access_token(identity='alice', additional_claims={'role': 'user', 'tenant_id': 'default'})

            response = self.client.put(
                '/api/auth/profile',
                json={
                    'full_name': 'Alice Doe',
                    'bio': 'Researcher',
                    'avatar_url': 'data:image/png;base64,abc',
                    'social_links': {
                        'google': 'https://google.com',
                        'linkedin': 'https://linkedin.com/in/alice',
                        'github': 'https://github.com/alice',
                    },
                },
                headers={'Authorization': f'Bearer {token}'},
            )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload['profile']['full_name'], 'Alice Doe')
        self.assertEqual(payload['profile']['social_links']['github'], 'https://github.com/alice')


if __name__ == '__main__':
    unittest.main()
