from django.core.mail import EmailMessage

def send_email(subject : str, body : str, to : str):
        msg = EmailMessage(subject=subject,body=body, to=to)
        msg.send()