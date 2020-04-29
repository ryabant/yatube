from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Post, Group
from .forms import PostForm
from django.shortcuts import render, redirect, get_object_or_404, reverse


User = get_user_model()


class ProfileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="user_test", password="12345")
        self.group = Group.objects.create(
            title='test', slug='test', description='test group')
        self.post = Post.objects.create(
            author=self.user, text='first')

    def test_profile(self):
        self.client.login(username="user_test", password="12345")
        response = self.client.get("/user_test/")
        self.assertEqual(response.status_code, 200)

    def test_user_create_new_post(self):
        self.client.login(username="user_test", password="12345")
        response = self.client.get("/new/")
        self.assertEqual(response.status_code, 200)

        self.client.logout()
        response = self.client.get("/new/")
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_new_post(self):

        self.client.login(username="user_test", password="12345")

        response = self.client.post('/new/', data={'text': 'new_post'})

        response = self.client.get("")
        self.assertEqual(len(response.context["page"]), 2)
        self.assertContains(response, text='new_post')

        response = self.client.get("/user_test/")
        self.assertContains(response, text='new_post')

        response = self.client.get("/user_test/2/")
        self.assertContains(response, text='new_post')

    def test_404(self):

        response = self.client.get("/badurl/")
        self.assertTemplateUsed(response, template_name='misc/404.html')

    def test_post_with_image(self):

        self.client.login(username="user_test", password="12345")
        with open('media/test.png', 'rb') as fp:
            self.client.post(
                "/new/", data={'text': 'new post', 'image': fp, 'group': self.group.pk})

        response = self.client.get("")
        self.assertContains(response, '<img', status_code=200)

        response = self.client.get("/user_test/")
        self.assertContains(response, '<img', status_code=200)

        response = self.client.get("/user_test/2/")
        self.assertContains(response, '<img', status_code=200)

        response = self.client.get("/group/test/")
        self.assertContains(response, '<img', status_code=200)

    def test_wrong_format_image(self):
        self.client.login(username="user_test", password="12345")

        with open('media/test.txt', 'rb') as fp:
            response = self.client.post(
                "/new/", {'text': "123", 'image': fp})

        self.assertFormError(response, 'form', "image",
                             'Отправленный файл пуст.')
