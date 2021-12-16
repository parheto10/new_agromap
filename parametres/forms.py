from django import forms
from django.contrib.auth import get_user_model
#from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from parametres.models import Projet

User = get_user_model()
non_allowed_username = ["abc", "123", "admin1", "admin12"]

class LoginForm(forms.Form):
    username = forms.CharField(label="Nom Utilisateur")
    password = forms.CharField(widget=forms.PasswordInput(attrs={"id":"password"}), label="Mot de Passe")

    def clean_username(self):
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username__iexact=username)
        if not qs.exists:
            raise forms.ValidationError("Utilisateur Invalide !!!")
        return username

class UserForm(forms.ModelForm):
    last_name = forms.CharField(label="Nom")
    first_name = forms.CharField(label="Prénoms")
    username = forms.CharField(label="Nom d’utilisateur")
    email = forms.EmailField(label="Adresse électronique")
    password = forms.CharField(widget=forms.PasswordInput(attrs={"id": "password", "class": "form-control"}), label="Mot de Passe")

    class Meta:
        model=User
        fields=['last_name', 'first_name', 'username', 'email', 'password']

# class ProjetForm(ModelForm):
#     class Meta:
#         model = Projet
#         fields = [
#             'client',
#             'categorie',
#             'accronyme',
#             'titre',
#             'chef',
#             'debut',
#             'fin',
#             'etat',
#         ]



# #for contact us page
# class ContactForm(forms.Form):
#     Nom = forms.CharField(max_length=30)
#     Email = forms.EmailField()
#     Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))
