from http import HTTPStatus
import json

from django.forms import model_to_dict
from reminder.serializers import CertificateSerializer
from .MailManager import send_email
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.shortcuts import redirect, render
from django.http import BadHeaderError, HttpResponse, JsonResponse
from .models import Certificate, Reminder, CustomUser
from .forms import EmailInput, PemUpload, SettingInput, SignUpForm, LogInForm
from cryptography import x509
from cryptography.x509.oid import NameOID
from django.template import loader
from django.contrib.auth import login, authenticate, logout
from django .urls import reverse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import CertificateSerializer, ReminderSerializer, CustomUserSerializer
from reminder import serializers

""" Using JsonResponse, serializers and csrf_exempt for RestAPI 
    - https://medium.com/geekculture/building-django-api-views-without-django-rest-framework-4fa9883de0a8
    - https://dev.to/alexmercedcoder/creating-a-restful-api-with-django-without-djangorestframework-17n7
    
    Alternative: Partitially implement django rest framework functions
"""

def index(request):
    return HttpResponse("Index Page")

def upload_certificate(request):
    form = PemUpload()
    error = ""
    if request.method == 'POST':
        try:
            uploadFile = request.FILES['textfile']
            data = str(uploadFile.read(), 'utf-8')
            raw_bytes = bytes(data, 'utf-8')
            initial = x509.load_pem_x509_certificate(raw_bytes)
            sn = initial.serial_number
            cn = initial.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
            ed_dt = initial.not_valid_after
            ed = ed_dt.strftime("%Y-%m-%d")
            certificate = Certificate.objects.create(common_name = cn, serialnumber = sn, expiration_date = ed)
            certificate.save()
            
            return redirect('show_certificate', certUid = certificate.uid)
            
        except Exception as e:
            error = str(e)
    return render(request, 'reminder/upload.html', {'form':form, 'error':error})

def show_certificate(request, certUid):
    cert = Certificate.objects.filter(uid = certUid).first()
    emailInput = EmailInput(request.POST or None)
    if request.method == 'POST':
        email = str(request.POST['email'])
        user_exists = CustomUser.objects.filter(email=email).exists()
        if not user_exists:
            user = CustomUser.objects.create(email=email, username = email)
            return redirect('password_set', userId = user.id)
        user = CustomUser.objects.get(email=email)
        reminder = Reminder.objects.create(certificate = cert, email = email, user = user)
        reminder.save()
        send_email(subject='Confirmation Link', body='http://127.0.0.1:8000/reminder/certificate/%s/settings' % str(cert.uid), to=[reminder.email])
        return HttpResponse('Please check your email')

    template = loader.get_template('reminder/show.html')
    context = {
                'form': emailInput,
                'certificate': cert
            }
    return HttpResponse(template.render(context, request))

def settings(request, uid):
    cert = Certificate.objects.filter(uid = uid).first()
    reminder = Reminder.objects.filter(certificate = cert.id).first()
    settingInput = SettingInput(initial={'days_until_expiration': reminder.days_until_expiration, 'message': reminder.message})

    if request.method == 'POST':
        new_days_until_expiration = int(request.POST['days_until_expiration'])
        new_message = str(request.POST['message'])
        reminder.days_until_expiration = new_days_until_expiration
        reminder.message = new_message
        reminder.save()
        if request.user.is_authenticated:
            return redirect('home')
        return redirect('login')
        
    template = loader.get_template('reminder/settings.html')
    context = {
                'form': settingInput,
                'reminder': reminder
            }
    
    return HttpResponse(template.render(context, request))

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            form.instance.username = email
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'reminder/signup.html', {'form': form})

def log_in(request):
    error = False
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        form = LogInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return redirect('home')
            else:
                error = True
    else:
        form = LogInForm()

    return render(request,'reminder/login.html', {'form': form, 'error': error})

def log_out(request):
    logout(request)
    reverse('login')
    return redirect('index')

def password_set_request(request, userId):
    user = CustomUser.objects.get(Q(id = userId))
    subject = "Welcome to CertReminder"
    email_template_name = "password/emailPasswordFirstSet.txt"
    c = {
    "email": user.email,
    'domain':'127.0.0.1:8000',
    'site_name': 'Website',
    "uid":  urlsafe_base64_encode(force_bytes(user.pk)),
    "user": user,
    'token': default_token_generator.make_token(user),
    'protocol': 'http',
    }
    body = render_to_string(email_template_name, c)
    try:
        send_email(subject, body, [user.email])
    except BadHeaderError:
        return HttpResponse('Invalid header found.')
    return render(request, 'password/password_first_set_info.html', {})

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['email']
            user = CustomUser.objects.get(Q(email=data))
            if user:
                subject = "Password Reset Requested"
                email_template_name = "password/emailPasswordReset.txt"
                c = {
                "email": user.email,
                'domain':'127.0.0.1:8000',
                'site_name': 'Website',
                "uid":  urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                'token': default_token_generator.make_token(user),
                'protocol': 'http',
                }
                body = render_to_string(email_template_name, c)
                try:
                    send_email(subject, body, [user.email])
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
                return redirect ("../password_reset/done/")

    password_reset_form = PasswordResetForm()
    return render(request, 'password/password_reset.html', context={'form':password_reset_form})

def home(request):
    user = request.user
    reminders = user.reminder_set.all()
    return render(request, 'reminder/userhome.html', context={'reminders':reminders})

def delete_reminder(request, reminderId):
    r = Reminder.objects.get(id=reminderId)
    r.delete()
    return redirect('home')


from rest_framework.views import APIView
from rest_framework import status


class CertificateListAPIView(APIView):
    permission_classes = [AllowAny]

    # Create a new Certificate object with the given data
    def post(self, request, format=None):
        serializer = CertificateSerializer(data=request.data)
        if serializer.is_valid():
           serializer.save()
           return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, pk, format=None):
        print("API GET")

class CertificateDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, cert_id):
        try:
            return Certificate.objects.get(id=cert_id)
        except Certificate.DoesNotExist:
            return None

    def get(self, request, id, format=None):
        certificate = self.get_object(id)
        if not certificate:
            return Response("An object with this id doesnt exist", status=status.HTTP_400_BAD_REQUEST)
        serializer = CertificateSerializer(certificate)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id, format=None):
        certificate = self.get_object(id)
        if not certificate:
            return Response("An object with this id doesnt exist", status=status.HTTP_400_BAD_REQUEST)
        certificate.delete()
        return Response("Object deleted", status=status.HTTP_200_OK)

class ReminderListAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = ReminderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, format=None):
        reminders = Reminder.objects.filter(user = request.user)
        serializer = ReminderSerializer(reminders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReminderDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, reminder_id):
        try:
            return Reminder.objects.get(id=reminder_id)
        except Reminder.DoesNotExist:
            return None

    def get(self, request, id, format=None):
        reminder = self.get_object(id)
        if not reminder:
            return Response("An object with this id doesnt exist", status=status.HTTP_400_BAD_REQUEST)
        serializer = ReminderSerializer(reminder)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id, format=None):
        reminder = self.get_object(id)
        if not reminder:
            return Response("An object with this id doesnt exist", status=status.HTTP_400_BAD_REQUEST)
        data = {
            'days_until_expiration': request.data.get('days_until_expiration'),
            'message': request.data.get('message')
        }
        serializer = ReminderSerializer(instance=reminder,data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        reminder = self.get_object(id)
        if not reminder:
            return Response("An object with this id doesnt exist", status=status.HTTP_400_BAD_REQUEST)
        reminder.delete()
        return Response("Object deleted", status=status.HTTP_200_OK)

#class ReminderViewSet(viewsets.ModelViewSet):
#    queryset = Reminder.objects.all()
#    serializer_class = ReminderSerializer
#    permission_classes = [AllowAny]
#
#    def create(self, request, *args, **kwargs):
#        try:
#         body_unicode = request.body.decode('utf-8')
#         body = json.loads(body_unicode)
#         serializer = ReminderSerializer(data=body, context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data)
#     except Exception as e:
#         return JsonResponse(e)

# def partial_update(self, request, id=None, *args, **kwargs):
#     try:
#         id = kwargs.get('pk')
#         instance = Reminder.objects.filter(pk=id).get()
#         if not instance:
#             return JsonResponse(status=HTTPStatus.NOT_FOUND)
#         serializer = ReminderSerializer(instance=instance, data=request.data, context={'request': request}, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data)
#     except Exception as e:
#         return JsonResponse(e)
