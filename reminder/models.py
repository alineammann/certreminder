from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from datetime import datetime, date
import datetime
import uuid

# Create your models here.
class Certificate(models.Model):
    common_name = models.CharField(max_length=255)
    serialnumber = models.CharField(max_length=100)
    expiration_date = models.DateField(default=datetime.date.today)
    uid = models.UUIDField(default=uuid.uuid4)
    def save(self, *args, **kw):
        if self.uid is None:
            self.uid = uuid.uuid4()
        return super(Certificate, self).save(*args,**kw)

    def is_expired(self):
        today = date.today()
        if self.expiration_date < today:
            return True
        return False
    
class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser must have is_staff=True"
            )
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must have is_superuser=True"
            )
        
        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField("email address", unique=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Reminder(models.Model):
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE)
    email = models.EmailField(max_length=150)
    user = models.ForeignKey(CustomUser, on_delete = models.CASCADE, null=True)
    message = models.TextField(default="Guten Tag, Ihr Zertifikat läuft bald ab.")
    days_until_expiration = models.IntegerField(default=20)
    already_sent = models.BooleanField(default=False)
    def get_status(self):
        if (self.already_sent):
            return "Reminder was already sent"
        return "Reminder not sent yet"