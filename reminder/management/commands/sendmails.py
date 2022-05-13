from datetime import date, datetime, timedelta
from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from reminder.models import Reminder

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        now = datetime.now()
        current_time = now.strftime("-----------------%d-%m-%Y %H:%M:%S-----------------")
        print(current_time)
        try:
            reminders = Reminder.objects.filter(already_sent = False).distinct()
            count = 0
            for r in reminders:
                cert = r.certificate
                expiration_date = cert.expiration_date
                if(expiration_date > date.today()):
                    days_until_expiration = r.days_until_expiration
                    if expiration_date - timedelta(days=days_until_expiration) == date.today():
                        msg = EmailMessage(subject='Certificate expiration in %d days' % days_until_expiration,body=r.message, to=[r.email])
                        msg.send()
                        r.already_sent = True
                        r.save()
                        count = count+1
            print("%d Email(s) have been sent" % count)
        except Exception as e:
            print(e)
