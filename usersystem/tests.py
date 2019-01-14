import json
import mock
from django.test import TestCase, Client
from requests import ConnectTimeout

from usersystem import admin
from usersystem.admin import UserAdmin
from usersystem.models import *


class MockResponse:
    def __init__(self, status_code, *args, **kwargs):
        self.status_code = status_code

    def __call__(self, *args, **kwargs):
        return self

    @staticmethod
    def timeout(*args, **kwargs):
        raise ConnectTimeout()


class MockProjector:
    def __init__(self, *args, **kwargs):
        pass

    def authenticate(self):
        pass

    def get_power(self):
        return 'off'

    def set_power(self, *args, **kwargs):
        pass


class HomePageTestCase(TestCase):

    @staticmethod
    def prepare_user():
        user = User.objects.create(email='test@test.pl', is_active=True)
        user.set_password('secret')
        user.save()
        return user

    def setUp(self):
        self.user = HomePageTestCase.prepare_user()
        self.admin = User.objects.create(email='admin@test.pl', is_active=True, is_superuser=True, is_staff=True)
        self.admin.save()

    def test_home_page_status_code(self):
        response = self.client.get('/')
        self.assertEquals(response.status_code, 302)  # Redirect to login page

    def test_home_page_login_status_code_and_content(self):
        client = Client()
        client.force_login(self.user)
        response = client.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'NKRSI')

    def test_login(self):
        client = Client()
        self.assertTrue(client.login(email='test@test.pl', password='secret'))

    def test_admin_login(self):
        client = Client()
        client.force_login(self.admin)
        response = client.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'admin')
        response = client.get('/admin/')
        self.assertEquals(response.status_code, 200)


class LinkTestCase(TestCase):
    def setUp(self):
        self.user = HomePageTestCase.prepare_user()
        self.frontlink = FrontLink.objects.create(url='ajax\door', title='Door', description='Opens door', type=2,
                                                  bgcolor='#666600')
        self.frontlink.save()

    def test_link_on_page(self):
        client = Client()
        client.force_login(self.user)
        response = client.get('/')
        self.assertContains(response, 'card')
        self.assertContains(response, 'Opens door')


class AjaxAndREST(TestCase):
    def setUp(self):
        self.user = HomePageTestCase.prepare_user()
        self.user.student_card_id = 'superid'
        self.user.save()
        self.client = Client()

    def test_card_id_not_found(self):
        response = self.client.post('/rest/card_id', json.dumps({'card_id': 'nonsuperid'}),
                                    content_type="application/json")
        self.assertJSONEqual(response.content, json.dumps({'ok': False}))
        self.assertEquals(response.status_code, 404)

    def test_card_id_found(self):
        response = self.client.post('/rest/card_id', json.dumps({'card_id': 'superid'}),
                                    content_type="application/json")
        self.assertJSONEqual(response.content, json.dumps({'ok': True}))
        self.assertEquals(response.status_code, 200)

    @mock.patch('requests.get', MockResponse(404))
    def test_door_failed(self):
        self.client.force_login(self.user)
        response = self.client.get('/ajax/door')
        self.assertJSONEqual(response.content, json.dumps({'ok': False}))

    @mock.patch('requests.get', MockResponse.timeout)
    def test_door_timeout(self):
        self.client.force_login(self.user)
        response = self.client.get('/ajax/door')
        self.assertJSONEqual(response.content, json.dumps({'ok': False}))

    @mock.patch('requests.get', MockResponse(200))
    def test_door_ok(self):
        self.client.force_login(self.user)
        response = self.client.get('/ajax/door')
        self.assertJSONEqual(response.content, json.dumps({'ok': True}))

    @mock.patch('usersystem.views.Projector.from_address', MockResponse.timeout)
    def test_projector_timeout(self):
        self.client.force_login(self.user)
        response = self.client.get('/ajax/projector')
        self.assertJSONEqual(response.content, json.dumps({'ok': False}))

    @mock.patch('usersystem.views.Projector.from_address', MockProjector)
    def test_projector_ok(self):
        self.client.force_login(self.user)
        response = self.client.get('/ajax/projector')
        self.assertJSONEqual(response.content, json.dumps({'ok': True}))


class FAQTest(TestCase):
    def setUp(self):
        self.user = HomePageTestCase.prepare_user()
        self.client = Client()
        FAQ.objects.create(question="Jak żyć?", order=0, answer="Godnie.")
        FAQ.objects.create(question="Jak nie żyć?", order=1, answer="Niegodnie.")

    def test_faq_view(self):
        self.client.force_login(self.user)
        response = self.client.get('/faq')
        self.assertContains(response, 'Jak żyć?')
        self.assertContains(response, 'Jak nie żyć?')


class AdminTest(TestCase):
    def setUp(self):
        self.user = HomePageTestCase.prepare_user()
        self.user.is_superuser = True
        self.user.save()

    @mock.patch('usersystem.admin.User.email_user')
    @mock.patch('usersystem.admin.User.invite_to_slack')
    @mock.patch('usersystem.admin.User.create_radius_user')
    def test_create_user(self, mock1, mock2, mock3):
        user_admin = UserAdmin(User, None)
        new_user = User.objects.create(email='a@a.pl', is_active=True)
        user_admin.save_model(None, new_user, None, False)
        self.assertEqual(User.objects.filter(email='a@a.pl')[0], new_user)
