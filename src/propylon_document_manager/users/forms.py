from django import forms
from allauth.account.forms import SignupForm


class UserSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, request):
        return super().save(request)

    def custom_validation(self):
        pass
