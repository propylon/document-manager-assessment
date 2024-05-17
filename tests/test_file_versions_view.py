from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from propylon_document_manager.file_versions.models import User, FileVersion
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


class FileVersionViewSetTest(APITestCase):
    def setUp(self):
        # import pdb; pdb.set_trace()
        self.user1 = get_user_model().objects.create_user(name="test1", email="test1@test.com")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)
        self.user2 = get_user_model().objects.create_user(name="test2", email="test2@test.com")
        self.filename = 'some/path/testfile.txt'

    def test_create_file_record(self):
        # import pdb; pdb.set_trace()
        url = reverse('file_version-list', kwargs={'filename': self.filename})
        # import pdb; pdb.set_trace()
        response = self.client.post(url, {"foo": "bar"})
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['version_number'], 1)
