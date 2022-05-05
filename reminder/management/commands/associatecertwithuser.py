from datetime import date, datetime, timedelta
from random import randint
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMessage
from reminder.models import Reminder, CustomUser

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        users = CustomUser.objects.all()
        reminders = Reminder.objects.all()
        random = randint(0, users.count() - 1)
        
        for r in reminders:
            is_match = False
            currentMail = r.email
            for u in users:
                if currentMail == u.email:
                    is_match = True
                    print("matched")
            if not is_match:
                    r.email = users[random].email
                    r.save()

                

            
        

