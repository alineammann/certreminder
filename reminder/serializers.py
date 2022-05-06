from rest_framework import serializers
from .models import Certificate,Reminder,CustomUser

class CertificateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Certificate
        fields = ('common_name', 'serialnumber', 'expiration_date', 'uid')

class CustomUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('__all__')

class ReminderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reminder
        fields = ('certificate', 'email', 'user', 'message', 'days_until_expiration', 'already_sent')