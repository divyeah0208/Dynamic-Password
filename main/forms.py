from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    image = forms.ImageField()
    face_data_url = forms.CharField(widget=forms.HiddenInput())  # From webcam
    lat = forms.CharField(widget=forms.HiddenInput(), required=False)  # Latitude
    lang = forms.CharField(widget=forms.HiddenInput(), required=False)  # Longitude

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'image']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})