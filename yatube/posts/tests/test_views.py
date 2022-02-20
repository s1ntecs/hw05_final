from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from django.test import TestCase
from django.core.cache import cache
from itertools import islice

from ..models import Post, Group, User, Follow
from ..views import PR_POSTS

POSTS_COUNT = 13


class PaginationTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='susel')
        # Создаем группу
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='test-group',
        )
        # Создаем вторую группу, проверить что пост не попал в группу,
        # для которой не был предназначен
        ml_group = Group.objects.create(
            title='Вторая группа',
            slug='second-group',
            description='second-group',
        )
        # Создаем Пост
        Post.objects.create(
            author=cls.user,
            text='это пост 2',
            group=ml_group,
            pk=2,
        )
        # Создаем основной Пост
        cls.post = Post.objects.create(
            author=cls.user,
            text='это пост',
            group=cls.group,
            pk=1,
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.user = User.objects.get(username='susel')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        self.follower = User.objects.create_user(username='follower')
        cache.clear()

    def test_index_page_uses_correct_template(self):
        """URL-адрес использует шаблон posts/index.html."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertTemplateUsed(response, 'posts/index.html')

    def test_group_posts_page_uses_correct_template(self):
        """URL-адрес использует шаблон posts/group_list.html."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-group'}))
        self.assertTemplateUsed(response, 'posts/group_list.html')

    def test_profile_page_uses_correct_template(self):
        """URL-адрес использует шаблон posts/profile.html."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'susel'}))
        self.assertTemplateUsed(response, 'posts/profile.html')

    def test_post_detail_page_uses_correct_template(self):
        """URL-адрес использует шаблон posts/post_detail.html."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'}))
        self.assertTemplateUsed(response, 'posts/post_detail.html')

    def test_post_create_page_uses_correct_template(self):
        """URL-адрес использует шаблон posts/create_post.html."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_post_edit_page_uses_correct_template(self):
        """URL-адрес использует шаблон posts/create_post.html."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'}))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn(['page_obj'][0], response.context)
        self.assertEqual(len(response.context['page_obj']), 2)
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = str(first_object.author.username)
        post_title_0 = first_object.group.title
        post_description_0 = first_object.group.description
        self.assertEqual(post_text_0, 'это пост')
        self.assertEqual(post_author_0, 'susel')
        self.assertEqual(post_title_0, 'Тестовая группа')
        self.assertEqual(post_description_0, 'test-group')

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-group'}))
        self.assertIn(['page_obj'][0], response.context)
        self.assertEqual(len(response.context['page_obj']), 1)
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = str(first_object.author.username)
        post_title_0 = first_object.group.title
        post_description_0 = first_object.group.description
        self.assertEqual(post_text_0, 'это пост')
        self.assertEqual(post_author_0, 'susel')
        self.assertEqual(post_title_0, 'Тестовая группа')
        self.assertEqual(post_description_0, 'test-group')

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'susel'}))
        self.assertIn('author', response.context)
        first_object_auth = response.context['author']
        self.assertIn('count_posts', response.context)
        first_object_count = response.context['count_posts']
        self.assertIn(['page_obj'][0], response.context)
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = str(first_object_auth)
        post_title_0 = first_object.group.title
        post_description_0 = first_object.group.description
        post_count_0 = first_object_count
        self.assertEqual(post_text_0, 'это пост')
        self.assertEqual(post_author_0, 'susel')
        self.assertEqual(post_title_0, 'Тестовая группа')
        self.assertEqual(post_description_0, 'test-group')
        self.assertEqual(post_count_0, 2)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'}))
        self.assertIn('author', response.context)
        first_object_auth = response.context['author']
        self.assertIn('count_posts', response.context)
        first_object_count = response.context['count_posts']
        self.assertIn('post', response.context)
        self.assertIn('image', response.context)
        first_object = response.context['post']
        post_text_0 = first_object.text
        post_author_0 = str(first_object_auth)
        post_count_0 = first_object_count
        self.assertEqual(post_text_0, 'это пост')
        self.assertEqual(post_author_0, 'susel')
        self.assertEqual(post_count_0, 2)

    def test_create_post_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        self.assertIn('form', response.context)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)
        # Проверяем контекст 'username'
        first_object_username = response.context['username']
        post_username_0 = str(first_object_username)
        self.assertEqual(post_username_0, 'susel')

    def test_edit_post_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'}))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        self.assertIn('form', response.context)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)
        first_object = response.context['post']
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'это пост')

    def test_post_with_another_group_not_in_group_list(self):
        """Проверяем отсутсвие поста в другой группе."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'second-group'}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        self.assertIn(['page_obj'][0], response.context)
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        # post_group_0 = first_object.group
        self.assertNotEqual(post_text_0, 'это пост')

    def test_cache_work(self):
        """Проверяем работу кэша"""
        response = self.authorized_client.get(reverse('posts:index'))
        post = Post.objects.get(pk=1)
        # Удаляем 1 пост
        post.delete()
        # Проверяем, что в контексте 2 поста
        self.assertEqual(len(response.context['page_obj']), 2)
        # Очищаем кэш
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        # Проверяем, что в контексте 1 пост удален
        self.assertIs(len(response.context['page_obj']), 1)

    def test_follow_and_unfollow_work(self):
        """Проверяем работу подписки"""
        # Создаем клиент для подписчика
        follower_client = Client()
        # Авторизуем пользователя
        follower_client.force_login(self.follower)
        # Создаем клиент для подписки
        follower_client.get(
            reverse('posts:profile_follow', kwargs={'username': 'susel'}))
        # Запрашиваем авторов с модели Follow
        author = Follow.objects.values_list('author', flat=True)
        # Запрашиваем подпичиков с модели Follow
        follow = Follow.objects.values_list('user', flat=True)
        # Запрашиваем автора и подписчика с модели User
        author_user = User.objects.get(id__in=author)
        follower_user = User.objects.get(id__in=follow)
        # Проверяем подписан ли пользователь 'follower' на 'susel'
        self.assertEqual(follower_user, self.follower)
        self.assertEqual(author_user, self.user)
        """Проверяем работу отписки"""
        # считаем количество подписок до отписки
        Follow_counted = Follow.objects.count()
        follower_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': 'susel'}))
        # считаем количество подписок после отписки
        Follow_count = Follow.objects.count()
        # смотрим произошла ли отписка
        self.assertEqual(Follow_count, (Follow_counted - 1))

    def test_follow_correct_work(self):
        # Создаем связь подписчика с автором
        Follow.objects.create(
            author=self.user,
            user=self.follower,
        )
        # Создаем клиент для подписчика
        follower_client = Client()
        # Авторизуем пользователя
        follower_client.force_login(self.follower)
        """Новая запись пользователя появляется у тех, кто на него подписан"""
        response = follower_client.get(reverse('posts:follow_index'))
        self.assertIn(['page_obj'][0], response.context)
        first_object = response.context['page_obj'][0]
        follow_object = Follow.objects.filter(user=self.follower.id)
        author = follow_object.values_list('author', flat=True)
        post_auth_0 = first_object.author.id
        self.assertIn(post_auth_0, author)

        """Проверяем что посты автора не появляются у тех, кто не подписан"""
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(['page_obj'][0], response.context)
        first_object = response.context['authors']
        # Проверяем, что в контексте нет автора
        # на которого пользователь не подписан
        self.assertNotIn(author, first_object)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='susel')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='test-group',
        )
        cls.post = (Post(
            text='это пост № %s' % i,
            author=cls.user,
            group=cls.group) for i in range(POSTS_COUNT)
        )
        batch = list(islice(cls.post, POSTS_COUNT))
        Post.objects.bulk_create(batch, POSTS_COUNT)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.user = User.objects.get(username='susel')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_index_first_page_contains_ten_records(self):
        """Проверяем Пагинатор. количество постов на первой странице index"""
        response = self.authorized_client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), PR_POSTS)

    def test_index_second_page_contains_three_records(self):
        """Проверяем Пагинатор. количество постов на второй странице index"""
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']), (POSTS_COUNT - PR_POSTS))

    def test_group_list_first_page_contains_ten_records(self):
        """Проверяем Пагинатор. к-во постов на первой странице group_list"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-group'}))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), PR_POSTS)

    def test_group_list_second_page_contains_three_records(self):
        """Проверяем Пагинатор. к-во постов на второй странице group_list"""
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']), (POSTS_COUNT - PR_POSTS))

    def test_profile_first_page_contains_ten_records(self):
        """Проверяем Пагинатор. количество постов на первой странице profile"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'susel'}))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), PR_POSTS)

    def test_profile_second_page_contains_three_records(self):
        """Проверяем Пагинатор. количество постов на второй странице profile"""
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']), (POSTS_COUNT - PR_POSTS))
