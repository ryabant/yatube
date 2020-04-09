from django import forms
from django.forms import ModelForm
from .models import Post, Group


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text']
        labels = {
            'group': 'Группа',
            'text': 'Текст',
        }
        help_texts = {
            'group': 'Сообщество для публикации',
        }
