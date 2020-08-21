from django import forms

class ContactForm(forms.Form):
    yourname = forms.CharField(max_length=100, label='User Name')
    email = forms.EmailField(label='Email Address')
    password = forms.CharField(max_length=100, label='Password to set')
    source = forms.CharField(max_length=100, label='How do you know about me ?')