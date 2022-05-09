from rest_framework import serializers
from .models import Certificate,Reminder,CustomUser

class CertificateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Certificate
        fields = ('common_name', 'serialnumber', 'expiration_date', 'uid')

class CustomUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('url', 'username', 'email', 'is_active', 'is_staff', 'is_superuser',
                'last_login', 'date_joined', 'password',)
        read_only_fields = ('is_active', 'last_login', 'date_joined', 'is_staff', 'is_superuser')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

class ReminderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reminder
        fields = ('certificate', 'email', 'user', 'message', 'days_until_expiration', 'already_sent')