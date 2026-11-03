import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        help_texts = {
            'username': 'Только английские буквы, цифры и символы @/./+/-/_',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = 'Минимум 8 символов, не только цифры'
        self.fields['password2'].help_text = ''

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[A-Za-z0-9@./+\-_]+$', username):
            raise ValidationError('Имя пользователя должно содержать только английские буквы, цифры и символы @/./+/-/_')
        return username


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar', 'bio', 'birth_date')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'avatar': 'Аватар',
            'bio': 'О себе',
            'birth_date': 'Дата рождения',
        }


class OTPForm(forms.Form):
    code = forms.CharField(
        max_length=16, 
        label='Код из письма',
        widget=forms.TextInput(attrs={'placeholder': 'Введите 16-значный код'})
    )


# ВОТ ТА САМАЯ ФОРМА, КОТОРОЙ НЕ ХВАТАЛО
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = 'Текущий пароль'
        self.fields['new_password1'].label = 'Новый пароль'
        self.fields['new_password2'].label = 'Подтверждение пароля'
        self.fields['old_password'].help_text = ''
        self.fields['new_password1'].help_text = 'Минимум 8 символов'
        self.fields['new_password2'].help_text = ''