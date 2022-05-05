from django.forms import EmailInput
from django.test import TestCase
from reminder.forms import EmailInput, SettingInput, PemUpload

class EnterEmailTestCase(TestCase):
    def test_email_without_at(self):
        form = EmailInput(data={"email": "testemail.com"})
        self.assertFalse(form.is_valid())

    def test_email_without_dot(self):
        form = EmailInput(data={"email": "test@emailcom"})
        self.assertFalse(form.is_valid())

    def test_blank_input(self):
        form = EmailInput(data={"email": ""})
        self.assertFalse(form.is_valid())

class UploadFileTestCase(TestCase):
    def test_something(self):
        form = PemUpload()

class SetReminderTestCase(TestCase):
    def test_value_under_zero(self):
        form = SettingInput(data={"days_until_expiration": -1})
        self.assertFalse(form.is_valid())
    
    def test_letter_input(self):
        form = SettingInput(data={"days_until_expiration": 'a'})
        self.assertFalse(form.is_valid())