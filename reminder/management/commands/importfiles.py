from django.core.management.base import BaseCommand
from reminder.models import Certificate, Reminder
from cryptography import x509
from cryptography.x509.oid import NameOID
import os

class Command(BaseCommand):
    

    def handle(self, *args, **options):
        folder = '/home/aline/Testdata/certreminder'
        os.chdir(folder)
        for file in os.listdir():
            path = os.path.join(folder, file)
            f = os.open(path, os.O_RDONLY)
            data = os.read(f, 3000)
            initial = x509.load_der_x509_certificate(data)
            sn = initial.serial_number
            cn = initial.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
            ed_dt = initial.not_valid_after
            ed = ed_dt.strftime("%Y-%m-%d")
            certificate = Certificate.objects.create(common_name = cn, serialnumber = sn, expiration_date = ed)
            certificate.save()
            reminder = Reminder.objects.create(certificate = certificate, email = 'test@email.com')
            reminder.save()
        certs = Certificate.objects.all()
        print(certs.count())