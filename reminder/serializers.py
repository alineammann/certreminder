from rest_framework import serializers
from .models import Certificate,Reminder,CustomUser

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ('pk', 'common_name', 'serialnumber', 'expiration_date', 'uid')
        read_only_fields = ('pk', 'uid')

    def create(self, validated_data):
        instance = Certificate.objects.create(**validated_data)
        instance.save()
        return instance
        

class CustomUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('url', 'username', 'email', 'is_active', 'is_staff', 'is_superuser',
                'last_login', 'date_joined', 'password')
        read_only_fields = ('is_active', 'last_login', 'date_joined', 'is_staff', 'is_superuser')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        certificate: CertificateSerializer
        user: CustomUserSerializer
        fields = ('pk', 'certificate', 'email', 'user', 'message', 'days_until_expiration', 'already_sent')
        read_only_fields = ('pk', 'already_sent')

    def create(self, validated_data, *args, **kwargs):
        instance = Reminder.objects.create(**validated_data)
        instance.save()
        return instance

    def update(self, instance, validated_data, *args, **kwargs):
        update_fields = [k for k in validated_data]
        for k,v in validated_data.items():
            print(k)
            print(v)
            setattr(instance, k, v)
        instance.save(update_fields=update_fields)
        return instance