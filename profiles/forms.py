from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', ]

class LoginForm(AuthenticationForm):
    class Meta:
        fields = ['username', 'password',]

















# class AuthForm(forms.Form):
#     """
#     A generic authentication form that handles both login and registration.
#     """
#     first_name = forms.CharField(
#         required=False,  # Not required for login
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
#         label="First Name"
#     )
#     last_name = forms.CharField(
#         required=False,  # Not required for login
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
#         label="Last Name"
#     )
#     username = forms.CharField(
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
#         label="Username"
#     )
#     password = forms.CharField(
#         widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
#         label="Password"
#     )
#     confirm_password = forms.CharField(
#         required=False,  # Not required for login
#         widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
#         label="Confirm Password"
#     )

#     def __init__(self, *args, **kwargs):
#         self.is_registration = kwargs.pop('is_registration', False)
#         super().__init__(*args, **kwargs)

#         # If this form is for login, remove unnecessary fields
#         if not self.is_registration:
#             del self.fields['first_name']
#             del self.fields['last_name']
#             del self.fields['confirm_password']

#     def clean(self):
#         cleaned_data = super().clean()
#         if self.is_registration:
#             password = cleaned_data.get("password")
#             confirm_password = cleaned_data.get("confirm_password")
#             if password and confirm_password and password != confirm_password:
#                 self.add_error("confirm_password", "Passwords do not match")
#         return cleaned_data
