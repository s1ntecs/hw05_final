from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import CreatedModel, PubdateModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заглавие',
        help_text='Введите заглавие группы'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='URL',
        help_text=('URL должно быть написано на английском без пробелов')
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Опишите группу'
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('group', kwargs={'slug': self.slug})


class Post(PubdateModel):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Введите текст'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:15]

    def get_absolute_url(self):
        return f'/person/{self.author}/'

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(CreatedModel):
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписаться'
    )
