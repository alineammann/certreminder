import datetime
from ftplib import MSG_OOB
from django.test import TestCase
from reminder.MailManager import send_email
from reminder.models import Reminder, Certificate
import uuid

class CertificateTestCase(TestCase):
    def setUp(self):
        Certificate.objects.create(common_name="expired", serialnumber="123", expiration_date=datetime.date(2019, 3, 14), uid=uuid.uuid4())
        Certificate.objects.create(common_name="valid", serialnumber="456", expiration_date=datetime.date(2030, 2, 23), uid=uuid.uuid4())
    
    def test_if_expired_true(self):
        expired = Certificate.objects.get(common_name = "expired")
        
        self.assertTrue(expired.is_expired())
        
    def test_if_expired_false(self):
        valid = Certificate.objects.get(common_name = "valid")

        self.assertFalse(valid.is_expired())

class ReminderTestCase(TestCase):
    msg = None
    def setUp(self):
        c = Certificate.objects.create(common_name="Reminder Test", serialnumber = "123", expiration_date=datetime.date(2030, 2, 23), uid = uuid.uuid4())
        r = Reminder.objects.create(certificate = c, email = "remindertest@email.com", message = "Test message", days_until_expiration = 20)
        self.msg = send_email('TestCase', 'This is a test email', [r.email])

    def test_send_email_from(self):
        msg = self.msg
        self.assertEquals(
            msg.from_email, 'revosie144@gmail.com'
        )

    def test_send_email_subject(self):
        msg = self.msg
        self.assertEquals(
            msg.subject, 'TestCase'
        )