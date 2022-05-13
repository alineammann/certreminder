import datetime
from email.mime import application
from http import HTTPStatus
from http.client import responses
import json
import uuid
from django.forms import EmailField
from django.http import HttpRequest, HttpResponse
from django.test import TestCase, Client
from reminder.forms import EmailInput
from reminder.models import Certificate, CustomUser, Reminder

class GetViewTestCase(TestCase):
    def setUp(self):
        c = Certificate.objects.create(common_name="Get View Test", serialnumber="123", expiration_date=datetime.date(2030, 2, 23), uid=uuid.uuid4())
        Reminder.objects.create(certificate = c, email = "getviewtest@email.com", message = "Test message", days_until_expiration = 20)

    def test_get_index_view(self):
        cli = Client()
        response = cli.get('/reminder/')
        self.assertEqual(
            response.status_code, HTTPStatus.OK
        )

    def test_get_show_view(self):
        c = Certificate.objects.filter(common_name = 'Get View Test').first()
        cli = Client()
        response = cli.get(f'/reminder/certificate/{c.uid}')
        self.assertEqual(
            response.context['certificate'], c        
        )

    def test_get_settings_view(self):
        r = Reminder.objects.filter(email = 'getviewtest@email.com').first()
        c = r.certificate
        cli = Client()
        response = cli.get(f'/reminder/certificate/{c.uid}/settings')
        self.assertEqual(
            response.context['reminder'], r 
        )

class PostViewTestCase(TestCase):
    def setUp(self):
        c = Certificate.objects.create(common_name="Post View Test", serialnumber="123", expiration_date=datetime.date(2030, 2, 23), uid=uuid.uuid4())
        u = CustomUser.objects.create(email="postviewtest@email.com", password="sml12345")
        r = Reminder.objects.create(certificate = c, email = "postviewtest@email.com", message = "Test message", days_until_expiration = 20, user = u)

    def test_post_index_view(self):
        cli = Client()
        filepath = './reminder/testing/test.pem'
        f = open(filepath, "r")
        response = cli.post('/reminder/certificate/upload', data={'textfile': f}, content_type="multipart/form-data")
        self.assertEqual(
            response.status_code, HTTPStatus.OK
        )

    def test_post_show_view(self):
            c = Certificate.objects.filter(common_name = 'Post View Test').first()
            cli = Client()
            cli.user = CustomUser.objects.filter(email="postviewtest@email.com").first()
            cli.login(email="postviewtest@email.com", password="sml12345")
            response = cli.post(f'/reminder/certificate/{c.uid}', data={'email': "postviewtest@email.com"}, content_type="multipart/form-data", follow=True)
            self.assertEqual(
                response.status_code, HTTPStatus.OK
            )