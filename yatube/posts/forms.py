from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        error_messages = {
            'text': {
                'required': 'В поле текста должна быть хотя бы одна буква...',
            }
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        error_messages = {
            'text': {
                'required': 'В поле текста должна быть хотя бы одна буква...',
            }
        }
