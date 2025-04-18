from rest_framework.test import APITestCase
from finance.models import CustomUser
from rest_framework import status
from django.urls import reverse

class TestAuth(APITestCase):

    def setUp(self):
        self.password = "Root@122"
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password=self.password
        )
        print(self.user)


    def login_e(self):
        response =  self.client.post(reverse('login'),{
            'email': self.user.email,
            'password': self.password,
        })
        return response.data['access'], response.data['refresh']


    def test_login(self):
        access, refresh = self.login_e()
        print(access)
        print(refresh)
        self.assertEqual()
