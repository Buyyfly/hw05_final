from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import (PasswordChangeView,
                                       PasswordChangeDoneView)

from .forms import CreationForm, PasswordChange


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('index:post_list')
    template_name = 'users/signup.html'


class ChangePassword(PasswordChangeView):
    form_class = PasswordChange
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'


class ChangePasswordDone(PasswordChangeDoneView):
    template_name = 'users/password_change_done.html'
