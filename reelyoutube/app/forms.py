from django import forms
from .models import Channel, Comment, something

class ChannelCreateForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = '__all__'

        widgets = {
            'channelimg': forms.FileInput(attrs={'id': 'filebtn'}),
            'channelname': forms.TextInput(attrs={'placeholder': 'Channel Name'})
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = something
        fields = ['comment_body']
