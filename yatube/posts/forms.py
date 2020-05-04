from django.forms import ModelForm
from .models import Post, Comment
from django import forms


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image']
        labels = {
            'group': 'Группа',
            'text': 'Текст',
            'image': 'Добавление картинки'
        }
        help_texts = {
            'group': 'Сообщество для публикации',
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': 'Текст',
        }
        widgets = {'text': forms.Textarea(attrs={'cols': 80})}
