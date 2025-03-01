from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# your_app/forms.py
from django import forms
from .models import Contest
from .models import Profile
from .models import QuizField
from .models import ContestPage
from .models import ContestCheckerPythonCode
from .models import ContestThresholdSubmission
from .models import QuizProblem
from django.core.exceptions import ValidationError

from django.contrib.auth.forms import AuthenticationForm

from .models import ContestTag

from django.forms import modelformset_factory

TagFormSet = modelformset_factory(ContestTag, fields=('title', 'color'), extra=1)

from .models import UploadedImage


class SinglePasswordChangeForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Новый пароль",
        min_length=4,  # Пример минимальной длины
    )

    def save(self, user):
        new_password = self.cleaned_data['new_password']
        user.set_password(new_password)
        user.save()


class FileUploadForm(forms.Form):
    image = forms.ImageField(label='Choose an image')


# class ImageUploadForm(forms.ModelForm):
#     class Meta:
#         model = UploadedImage
#         fields = ['image']
#
#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         # Устанавливаем пользователя перед сохранением
#         if not instance.user and hasattr(self, 'request'):
#             instance.user = self.request.user  # Устанавливаем текущего пользователя
#         if commit:
#             instance.save()
#         return instance


from .models import AppConfig


class AppConfigForm(forms.ModelForm):
    class Meta:
        model = AppConfig
        fields = ['allow_registration', 'enable_feature_x']


class QuizFieldForm(forms.ModelForm):
    class Meta:
        model = QuizField
        fields = ['width', 'height']

class QuizProblemForm(forms.ModelForm):
    # class Meta:
    #     model = QuizProblem
    #     fields = ['title', 'content', 'answer', 'points']

    class Meta:
        model = QuizProblem
        fields = ['title', 'content', 'answer', 'points']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название темы задачи'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Условие задачи', 'rows': 10}),
        }
        labels = {
            'title': 'Название темы задачи',
            'content': 'Условие задачи',
        }


class ContestTagForm(forms.ModelForm):
    class Meta:
        model = ContestTag
        fields = ['title', 'color']  # Поля для ввода названия и цвета тега
        widgets = {
            'color': forms.Select(choices=ContestTag.COLOR_CHOICES),
        }


class CodeEditForm(forms.ModelForm):
    class Meta:
        model = ContestCheckerPythonCode
        fields = ['code']  # Включаем поле code из модели
        widgets = {
            'code': forms.Textarea(attrs={'rows': 20, 'cols': 80}),  # Кастомизация виджета для textarea
        }


class ContestUserProfileForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)  # Поле для пароля
    name = forms.CharField(max_length=255)  # Поле для имени пользователя
    contest_access = forms.ModelChoiceField(queryset=Contest.objects.all(), widget=forms.HiddenInput())  # Скрытое поле для выбора соревнования

    class Meta:
        model = User
        fields = ['username', 'password']  # Поля для имени пользователя и пароля

    def save(self, commit=True, *args, **kwargs):
        # Сначала создаем пользователя, но не сохраняем его сразу в БД
        user = super().save(commit=False)

        # Устанавливаем пароль в зашифрованном виде
        user.set_password(self.cleaned_data['password'])

        # Сохраняем пользователя, если нужно
        if commit:
            user.save()

        # Создаем профиль и связываем его с пользователем
        profile = Profile.objects.create(user=user, name=self.cleaned_data['name'], contest_access=self.cleaned_data['contest_access'])
        profile.save()
        return user


class ContestForm(forms.ModelForm):
    class Meta:
        model = Contest
        fields = ['name', 'time_start', 'time_end', 'is_open', 'is_open_preview', 'is_open_results', 'is_open_status', 'color']  # Добавляем 'color'
        widgets = {
            'time_start': forms.DateTimeInput(
                attrs={
                    'class': 'form-control datetimepicker',
                    'type': 'datetime-local',  # HTML5-тип для выбора даты и времени
                }
            ),
            'time_end': forms.DateTimeInput(
                attrs={
                    'class': 'form-control datetimepicker',
                    'type': 'datetime-local',
                }
            ),
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Название соревнования',
                }
            ),
            'is_open': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
            'is_open_preview': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
            'is_open_results': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
            'is_open_status': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
            'color': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
        }
        labels = {
            'name': 'Название',
            'time_start': 'Время начала соревнования',
            'time_end': 'Время завершения соревнования',
            'is_open': 'Открытое соревнование',  # Подпись для чекбокса
            'is_open_preview': 'Доступен предпросмотр',
            'is_open_results': 'Участники видят результаты',
            'is_open_status': 'Участники видят статус',
            'color': 'Цвет плашки',  # Подпись для выбора цвета
        }

    def clean(self):
        cleaned_data = super().clean()
        time_start = cleaned_data.get('time_start')
        time_end = cleaned_data.get('time_end')

        if time_start and time_end and time_end < time_start:
            raise ValidationError("Дата окончания не может быть раньше даты начала.")

        return cleaned_data


class ContestPageForm(forms.ModelForm):
    class Meta:
        model = ContestPage
        fields = ['title', 'content']  # Поля, которые нужно редактировать
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Заголовок страницы'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Содержимое страницы', 'rows': 5}),
        }
        labels = {
            'title': 'Заголовок',
            'content': 'Содержимое',
        }


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="Логин",
        max_length=10,
        min_length=1,
        required=True,
        help_text='',
        error_messages={
            'required': 'Пожалуйста, введите имя пользователя.',
            'max_length': 'Имя пользователя не должно превышать 10 символов.',
            'min_length': 'Имя пользователя должно содержать как минимум 1 символ.'
        }
    )
    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput,
        min_length=1,
        max_length=10,
        error_messages={
            'required': 'Пожалуйста, введите пароль.',
            'min_length': 'Пароль должен содержать как минимум 1 символ.',
            'max_length': 'Пароль не должен превышать 10 символов.'
        }
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput,
        strip=False,
        min_length=1,
        max_length=10,
        error_messages={
            'required': 'Пожалуйста, подтвердите пароль.',
            'min_length': 'Пароль должен содержать как минимум 1 символ.',
            'max_length': 'Пароль не должен превышать 10 символов.'
        }
    )
    profile_name = forms.CharField(
        max_length=50,
        min_length=1,
        required=True,
        help_text='',
        error_messages={
            'required': 'Пожалуйста, введите имя пользователя.',
            'max_length': 'Имя пользователя не должно превышать 10 символов.',
            'min_length': 'Имя пользователя должно содержать как минимум 1 символ.'
        }
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")
        return password2

    def save(self, commit=True):
        # Сохраняем пользователя через родительский метод
        user = super().save(commit=False)

        # Сохраняем профиль после создания пользователя
        if commit:
            user.save()  # Сначала сохраняем пользователя, чтобы получить его ID
            profile = Profile.objects.create(
                user=user,
                name=self.cleaned_data['profile_name']  # Присваиваем имя профиля из формы
            )

        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Логин",
        max_length=10,
        min_length=1,
        required=True,
        initial='',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Пожалуйста, введите имя пользователя.',
            'max_length': 'Имя пользователя не должно превышать 10 символов.',
            'min_length': 'Имя пользователя должно содержать как минимум 1 символ.'
        }
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput,
        initial='',
        min_length=1,
        max_length=10,
        error_messages={
            'required': 'Пожалуйста, введите пароль.',
            'min_length': 'Пароль должен содержать как минимум 1 символ.',
            'max_length': 'Пароль не должен превышать 10 символов.'
        }
    )
