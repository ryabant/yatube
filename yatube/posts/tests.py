from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Post, Group

User = get_user_model()


class ProfileTest(TestCase):
    def setUp(self):
        cache.clear()
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
        self.client.post('/new/', data={'text': 'new_post'})

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

    def test_cache(self):
        self.client.login(username="user_test", password="12345")
        self.client.post('/new/', data={'text': 'new_post'})
        response = self.client.get("")
        key = make_template_fragment_key('index_page')
        html_cache = cache.get(key)
        self.assertIn(html_cache, str(response.content.decode()))

    def test_auth_user_follow_unfollow(self):
        user = User.objects.create_user(username="user_2", password="12345")
        Post.objects.create(author=user, text='lalala')

        self.client.login(username="user_test", password="12345")
        self.client.get("/user_2/follow/")
        response = self.client.get("/follow/")
        self.assertContains(response, text='lalala')

        self.client.get("/user_2/unfollow/")
        response = self.client.get("/follow/")
        self.assertNotContains(response, text='lalala')

    def test_new_post_in_follow(self):
        user1 = User.objects.create_user(username="user_2", password="12345")
        Post.objects.create(author=user1, text='lalala')
        user2 = User.objects.create_user(username="user_3", password="12345")
        Post.objects.create(author=user2, text='hello')

        self.client.login(username="user_test", password="12345")
        self.client.get("/user_2/follow/")
        response = self.client.get("/follow/")
        self.assertContains(response, text='lalala')
        self.assertNotContains(response, text='hello')

    def test_auth_user_can_comment(self):
        user = User.objects.create_user(username="user_2", password="12345")
        Post.objects.create(author=user, text='lalala')

        self.client.login(username="user_test", password="12345")
        self.client.post('/user_2/1/comment/', data={'text': 'hello'})

        response = self.client.get("/user_2/1/")
        self.assertContains(response, text='hello')

        self.client.logout()
        response = self.client.get("/user_2/1/comment/")
        self.assertRedirects(response, '/auth/login/?next=/user_2/1/comment/')
