import uuid
from rest_framework.test import APIClient

client = APIClient()
uid=uuid.uuid4()
request = client.post('reminder/api/certificates', {'common_name': 'API Post Test', 'serialnumber': '123', })