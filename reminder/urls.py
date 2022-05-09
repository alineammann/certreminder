from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'certificates', views.CertificateViewSet)
router.register(r'reminders', views.ReminderViewSet)
router.register(r'customusers', views.CustomUserViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', views.index, name='index'),
    path('certificate/upload', views.upload_certificate, name='upload_certificate'),
    path('certificate/<uuid:certUid>', views.show_certificate, name='show_certificate'),
    path('certificate/<uuid:uid>/settings', views.settings, name='settings'),
    path('password_reset', views.password_reset_request, name="password_reset"),    #ACCOUNTS APP?
    path('password_set/<int:userId>', views.password_set_request, name="password_set"), #ACCOUNTS APP?
    path('<int:reminderId>/delete>', views.delete_reminder, name='delete_reminder'), 
]