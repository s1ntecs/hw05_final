import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from ..models import Post, Group, User, Comment, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='susel')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='test-group',
        )
        # Создаем вторую группу, она нам понадобиться при редактировании поста
        cls.sec_group = Group.objects.create(
            title='Вторая группа',
            slug='second-group',
            description='second-group',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Ж' * 15,
            group=cls.group,
            pk=1,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.follower = User.objects.create_user(username='misha')
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованного клиента
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        # Создаем связь подписчика с автором
        Follow.objects.create(
            author=self.user,
            user=self.follower,
        )
        self.follower_client = Client()
        # Авторизуем пользователя
        self.follower_client.force_login(self.follower)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
            'image': uploaded,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'susel'}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_post = Post.objects.latest('pub_date')
        form_fields = {
            last_post.text: form_data['text'],
            last_post.group.pk: form_data['group'],
            str(last_post.image.name): 'posts/small.gif',
            last_post.author: self.user,
        }

        # Проверяем, что сoдержания поля в словаре соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertEqual(value, expected)

    def test_edit_post(self):
        """Валидная форма Редактирует запись в Post."""
        changed_small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x39\x00\x21\xf9\x04'
            b'\x01\x0a\x49\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='changed_small.gif',
            content=changed_small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
            'image': uploaded,
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        changed_post = Post.objects.latest('pub_date')
        form_fields = {
            changed_post.text: form_data['text'],
            # Проверяем, изменилась ли группа
            changed_post.group.pk: form_data['group'],
            str(changed_post.author): 'susel',
            str(changed_post.image.name): 'posts/changed_small.gif'
        }
        # Проверяем, что сoдержания поля в словаре соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertEqual(value, expected)

    def test_guest_cant_create_post(self):
        """Проверяем, что гость не может создать пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
        }
        # От имени гостя пытаемся создать пост
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, что число постов не изменилось
        self.assertEqual(Post.objects.count(), posts_count)

    def test_guest_cant_create_comment(self):
        """Проверяем, что гость не может создать комментарий."""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        # От имени гостя пытаемся создать комментарий
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        # Проверяем, что число постов не изменилось
        self.assertEqual(Comment.objects.count(), comment_count)

    def test_authorized_client_can_create_comment(self):
        """Проверяем, что авторизованный клинет может создать комментарий."""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        # Авторизованный клинет пытается создать коментарий
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        # Проверяем, что число комментрариев изменилось
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        last_comment = Comment.objects.latest('created')
        # После успешной отправки комментарий появляется на странице поста.
        self.assertEqual(last_comment.text, form_data['text'])
        self.assertEqual(last_comment.author, self.user)
        self.assertEqual(last_comment.post.id, self.post.pk)

    def test_guest_cant_follow(self):
        """Проверяем, что гость не может подписаться."""
        follow_count = Follow.objects.count()
        # От имени гостя пытаемся подписаться
        self.guest_client.get(
            reverse('posts:profile_follow', kwargs={'username': 'susel'}))
        # Проверяем, что число полписок не изменилось
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_guest_cant_unfollow(self):
        """Проверяем, что гость не может отписаться."""
        Follow.objects.create(
            author=self.user,
            user=self.follower,
        )
        follow_count = Follow.objects.count()
        # От имени гостя пытаемся подписаться
        self.guest_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': 'susel'}))
        # Проверяем, что число полписок не изменилось
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_authorized_can_follow(self):
        """Проверяем, что авторизованный пользователь может подписаться."""
        follow_count = Follow.objects.count()
        # Подписываемся от имени авторизованного пользователя
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': 'misha'}))
        # Проверяем, что появилась одна подписка
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_authorized_can_unfollow(self):
        """Проверяем, что авторизованный пользователь может отписаться."""
        follow_count = Follow.objects.count()
        # Авторизованный пользователь отписывается
        self.follower_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': 'susel'}))
        # Проверяем, что число полписок изменилось
        self.assertEqual(Follow.objects.count(), follow_count - 1)

    def test_follow_work(self):
        """Проверяем работу подписки"""
        # Создаем клиент для подписчика
        # Создаем клиент для подписки
        self.follower_client.get(
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

    def test_follow_correct_work(self):
        # Создаем связь подписчика с автором
        # Создаем клиент для подписчика
        """Новая запись пользователя появляется у тех, кто на него подписан"""
        response = self.follower_client.get(reverse('posts:follow_index'))
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
