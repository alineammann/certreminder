import datetime
from http import HTTPStatus
import uuid
from django import http
from django.urls import reverse
from rest_framework.test import APITestCase
from reminder.models import Certificate, CustomUser, Reminder


class CustomUserTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(email="customuser@email.com", password="sml12345")

    def test_get_user(self):
        c = self.user
        response = self.client.get(f"/reminder/api/customusers/{c.id}", {}, True)
        data = {
            "url": f"http://127.0.0.1:8000/reminder/api/customusers/{c.id}/",
            "username": "customuser2@email.com",
            "email": "customuser2@email.com",
            "is_active": True,
            "is_staff": False,
            "is_superuser": False,
            "last_login": c.last_login,
            "date_joined": c.date_joined
        }
        self.assertEqual(response.status_code, HTTPStatus.OK)              

    def test_get_users(self):
        url = reverse('customuser-list')
        print(url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_user(self):
        c = self.user
        data = {
            "url": f"http://127.0.0.1:8000/reminder/api/customusers/{c.id}/",
            "username": c.email,
            "email": c.email,
            "password": "sml12345",
            "is_active": True,
            "is_staff": False,
            "is_superuser": False,
            "last_login": c.last_login,
            "date_joined": c.date_joined
        }
        response = self.client.post(f"/reminder/api/customusers/{c.id}", data, follow=True, format="json")
        self.assertEqual(response.status_code, HTTPStatus.OK)

class ReminderTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(email="customuser@email.com", password="sml12345")
        self.certificate = Certificate.objects.create(common_name="API Testing", serialnumber="123", expiration_date=datetime.date(2030, 2, 23), uid=uuid.uuid4())
        self.reminder = Reminder.objects.create(email="customuser@email.com", certificate = self.certificate, user = self.user)

    def test_get_reminder(self):
        r = self.reminder
        response = self.client.get(f"/reminder/api/reminders/{r.id}", {}, True)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)              

    def test_get_reminders(self):
        url = reverse('reminder-list')
        print(url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_reminder(self):
        r = self.reminder
        data = {
            "url": f"http://127.0.0.1:8000/reminder/api/reminders/{r.id}/",
            "certificate": f"http://127.0.0.1:8000/reminder/api/certificates/{self.certificate.id}/",
            "email": r.email,
            "user": f"http://127.0.0.1:8000/reminder/api/customusers/{self.user.id}/",
            "days_until_expiration": 15,
            "message": "API Testing"
        }
        response = self.client.post(f"/reminder/api/reminders/{r.id}", data, follow=True, format="json")
        r.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.OK)

class CertificateTests(APITestCase):
    def setUp(self):
        self.certificate = Certificate.objects.create(common_name="API Testing", serialnumber="123", expiration_date=datetime.date(2030, 2, 23), uid=uuid.uuid4())

    def test_get_certificate(self):
        c = self.certificate
        response = self.client.get(f"/reminder/api/certificates/{c.id}", {}, True)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)              

    def test_get_reminders(self):
        url = reverse('certificate-list')
        print(url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_reminder(self):
        c = self.certificate
        data = {
            "url": f"http://127.0.0.1:8000/reminder/api/certificates/{c.id}/",
            "common_name": c.common_name,
            "serialnumber": c.serialnumber,
            "expiration_date": c.expiration_date,
            "uid": c.uid
        }
        response = self.client.post(f"/reminder/api/certificates/{c.id}", data, follow=True, format="json")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        