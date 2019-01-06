from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory, Client

from usersystem.models import User


class HomePageTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@test.pl', is_active=True)
        self.user.set_password('secret')
        self.user.save()

    def test_home_page_status_code(self):
        response = self.client.get('/')
        self.assertEquals(response.status_code, 302)  # Redirect to login page

    def test_home_page_login_status_code(self):
        client = Client()
        client.force_login(self.user)
        response = client.get('/')
        self.assertEquals(response.status_code, 200)

    def test_login(self):
        client = Client()
        self.assertTrue(client.login(email='test@test.pl', password='secret'))


class UserTestCase(TestCase):
    pass


class LinkTestCase(TestCase):
    def setUp(self):
        pass
