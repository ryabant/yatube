from django.forms import ModelForm
from .models import Post


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
