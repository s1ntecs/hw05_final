from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='test-group',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Ж' * 16,
        )

    def test_models_have_correct_object_names(self):
        """__str__  post - это строчка с содержимым post.text."""
        post = PostModelTest.post
        expected_object_name = post.text
        self.assertEqual(expected_object_name[:15], str(post))

    def test_models_have_correct_object_names_1(self):
        """__str__  group - это строчка с содержимым group.title."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_group_verboses(self):
        """verbose_name класса Group поля совпадают с ожидаемыми."""
        group = PostModelTest.group
        field_verboses = {
            'title': 'Заглавие',
            'description': 'Описание',
            'slug': 'URL',
        }
        # Получаем из свойста класса Group значение verbose_name для title
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_post_verboses(self):
        """verbose_name класса Group поля совпадают с ожидаемыми."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'author': 'Автор',
            'group': 'Группа',
        }
        # Получаем из свойста класса Group значение verbose_name для title
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_group_help_text(self):
        """Help_text класса Group поля совпадают с ожидаемыми."""
        group = PostModelTest.group
        field_help_texts = {
            'title': 'Введите заглавие группы',
            'description': 'Опишите группу',
            'slug': 'URL должно быть написано на английском без пробелов',
        }
        # Получаем из свойста класса Group значение verbose_name для title
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)

    def test_post_verboses(self):
        """Help_text класса Post поля совпадают с ожидаемыми."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст',
            'group': 'Выберите группу',
        }
        # Получаем из свойста класса Group значение verbose_name для title
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
