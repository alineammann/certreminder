from tkinter import Widget
from .models import CustomUser
from django import forms
from django.core.validators import MinValueValidator
from django.contrib.auth.forms import UserCreationForm


class PemUpload(forms.Form):
    textfile = forms.FileField()

class EmailInput(forms.Form):
    email = forms.EmailField()

class SettingInput(forms.Form):
    days_until_expiration = forms.IntegerField(validators=[MinValueValidator(0)])
    message = forms.CharField(widget = forms.Textarea)
    
class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email", "password1", "password2")

class LogInForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
