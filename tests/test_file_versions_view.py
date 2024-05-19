from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token


class FileVersionViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = get_user_model().objects.create_user(name="test1", email="test1@test.com")
        cls.user1.set_password("user@1234")
        cls.client = APIClient()
        cls.token = Token.objects.create(user=cls.user1)
        cls.client.force_authenticate(user=cls.user1)
        cls.user2 = get_user_model().objects.create_user(name="test2", email="test2@test.com")
        cls.user2.set_password("user@1234")

        # import pdb; pdb.set_trace()
        # cls.client.login(username='test1@test.com', password='user@1234')
        cls.filename1 = 'some/path/testfile1.txt'
        cls.client.post(reverse('file_version-list', kwargs={'filename': cls.filename1}))

        cls.filename2 = 'some/path/testfile2.txt'
        cls.client.force_authenticate(user=cls.user2)
        cls.client.post(reverse('file_version-list', kwargs={'filename': cls.filename2}))

    def test_create_file(self):
        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.client.force_authenticate(user=self.user1)
        # response = self.client.login(username='test1@test.com', password='user@1234')
        import pdb; pdb.set_trace()
        url = reverse('file_version-list', kwargs={'filename': f'{self.filename1}-extra'})
        import pdb; pdb.set_trace()
        response = self.client.post(url, {"foo": "bar"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['version_number'], 1)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Different user trying to access the file
        response = self.client.login(username='test2@test.com', password='user@1234')
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.client.logout()

    def test_file_create_incr(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('file_version-list', kwargs={'filename': self.filename1})
        response = self.client.post(url, {"foo": "bar"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['version_number'], 2)

    def test_file_specific_version(self):
        # specific version
        self.client.force_authenticate(user=self.user1)
        url = reverse('file_version-list', kwargs={'filename': self.filename1})
        for _ in range(10):
            response = self.client.post(url, {"foo": "bar"})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(url, {"revision": 9})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['version_number'], 9)

        # Different user
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # His own file
        url = reverse('file_version-list', kwargs={'filename': self.filename2})
        for _ in range(10):
            response = self.client.post(url, {"foo": "bar"})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(url, {"revision": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['version_number'], 5)

    def test_file_latest_version(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('file_version-list', kwargs={'filename': self.filename1})
        self.client.force_authenticate(user=self.user1)
        cur_version = 0
        for _ in range(10):
            response = self.client.post(url, {"foo": "bar"})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            cur_version = response.data['version_number']
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['version_number'], cur_version)

        # User2 create more revisions
        url = reverse('file_version-list', kwargs={'filename': self.filename2})
        self.client.force_authenticate(user=self.user2)
        cur_version = 0
        for _ in range(5):
            response = self.client.post(url, {"foo": "bar"})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            cur_version = response.data['version_number']

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['version_number'], cur_version)
