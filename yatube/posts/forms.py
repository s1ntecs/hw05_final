from xml.etree.ElementTree import Comment
from django import forms
from django.forms import ModelForm
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        data = self.cleaned_data['text']
        if data.split() == '':
            raise forms.ValidationError('Поле обязательно для заполнения!')
        return data


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        data = self.cleaned_data['text']
        if data.split() == '':
            raise forms.ValidationError('Поле обязательно для заполнения!')
        return data
