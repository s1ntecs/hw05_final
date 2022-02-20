from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Post, Group
from http import HTTPStatus

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='susel')
        Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='test-group',
        )
        Post.objects.create(
            author=cls.user,
            text='Ж' * 10,
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.get(username='susel')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """Страницы доступны пользователю."""
        # Шаблоны по адресам
        status_url_names = {
            self.guest_client.get('/auth/signup/'): HTTPStatus.OK,
            self.guest_client.get('/auth/login/'): HTTPStatus.OK,
            self.guest_client.get('/auth/logout/'): HTTPStatus.OK,
            self.authorized_client.get(
                '/auth/password_change/'): HTTPStatus.OK,
            self.authorized_client.get(
                '/auth/password_change/done/'): HTTPStatus.OK,
            self.guest_client.get(
                '/auth/password_reset/'): HTTPStatus.OK,
            self.guest_client.get(
                '/auth/password_reset/done/'): HTTPStatus.OK,
            self.authorized_client.get(
                '/auth/password_change/done/'): HTTPStatus.OK,
            self.guest_client.get('/auth/reset/done/'): HTTPStatus.OK,
        }
        for address, status in status_url_names.items():
            with self.subTest(address=address):
                self.assertEqual(address.status_code, status)
