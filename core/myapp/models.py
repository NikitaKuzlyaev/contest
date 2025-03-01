from django.db import models
from django.contrib.auth.models import User
import os
import uuid


def upload_to(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"  # Уникальное имя
    return os.path.join("uploads", new_filename)


class UploadedImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Пользователь, который загрузил картинку
    image = models.ImageField(upload_to=upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name


class AppConfig(models.Model):
    # Настройки приложения
    allow_registration = models.BooleanField(default=True, verbose_name="Разрешить регистрацию пользователей")

    # Дополнительные настройки, если нужно
    enable_feature_x = models.BooleanField(default=False, verbose_name="Включить функцию X")

    def __str__(self):
        return "Глобальные настройки приложения"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=255, unique=False)
    contest_access = models.ForeignKey(
        'Contest',  # Связь с моделью Contest
        on_delete=models.SET_NULL,  # Указывает, что поле останется null, если Contest будет удалён
        null=True,  # Поле может быть пустым в базе данных
        blank=True,  # Поле не обязательно для заполнения в формах
        related_name='profiles',  # Связь для обратного доступа (от Contest к Profile)
        verbose_name='Доступ к соревнованию'
    )

    def __str__(self):
        return f"Profile of {self.user.username}"


class Contest(models.Model):
    COLOR_CHOICES = [
        ("#FF0000", "Красный"),
        ("#0000FF", "Синий"),
        ("#00FF00", "Зеленый"),
        ("#FFA500", "Оранжевый"),
        ("#FFFF00", "Желтый"),
        ("#800080", "Пурпурный"),
        ("#00FFFF", "Циановый"),
        ("#FFC0CB", "Розовый"),
        ("#000000", "Черный"),
        ("#FFFFFF", "Белый"),  # Добавлен белый цвет
        ("#A52A2A", "Коричневый"),
        ("#808080", "Серый"),
        ("#ADD8E6", "Светло-голубой"),
        ("#FF6347", "Томато"),
        ("#32CD32", "Лаймовый"),
    ]

    name = models.CharField(max_length=255, unique=True)  # Поле Name
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания
    time_start = models.DateTimeField()  # Время начала
    time_end = models.DateTimeField()  # Время окончания

    is_open = models.BooleanField(default=True)  # Флаг, открыт ли конкурс
    is_open_preview = models.BooleanField(default=False)  # Флаг, открыто ли превью
    is_open_results = models.BooleanField(default=False)  # Флаг, открыта ли таблица для участников
    is_open_status = models.BooleanField(default=False)  # Флаг, открыт ли статус

    color = models.CharField(max_length=7, choices=COLOR_CHOICES, default="#0000FF")  # Цвет

    def __str__(self):
        return self.name


class Quiz(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)  # Внешний ключ к соревнованию


class QuizUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_user')  # Пользователь, который сделал попытку
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)  # Внешний ключ к соревнованию
    score = models.PositiveIntegerField(default=1000)
    combo_score = models.PositiveIntegerField(default=0)

    reward_by_problems = models.PositiveIntegerField(default=0)
    reward_by_combo = models.PositiveIntegerField(default=0)

    def decrease_score(self, points):
        self.score = self.score - points
        self.save()

    def increase_score(self, points):
        self.score = self.score + points
        self.reward_by_problems = self.reward_by_problems + points
        self.save()

    def increase_score_by_combo(self, points):
        self.score = self.score + points
        self.reward_by_combo = self.reward_by_combo + points
        self.save()

    def remove_combo_score(self):
        self.combo_score = 0
        self.save()

    def increase_combo_score(self, points):
        self.combo_score = self.combo_score + points
        self.save()


class QuizField(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    width = models.PositiveIntegerField(default=5)
    height = models.PositiveIntegerField(default=4)


class QuizFieldCell(models.Model):
    quizField = models.ForeignKey(QuizField, related_name='cells', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    row = models.PositiveIntegerField()
    col = models.PositiveIntegerField()

    cell_type = models.CharField(
        max_length=20,
        choices=[
            ('normal', 'Normal'),
            ('not_created', 'NotCreated'),
            ('blocked', 'Blocked'),
            ('special', 'Special'),
        ],
        default='not_created',
    )
    # quizProblem = models.ForeignKey(QuizProblem, null=True, blank=True, on_delete=models.SET_NULL)  # Привязка к вопросу


class QuizProblem(models.Model):
    quizFieldCell = models.ForeignKey(QuizFieldCell, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    answer = models.CharField(max_length=100)
    points = models.PositiveIntegerField()  # Стоимость задачи

    def __str__(self):
        return self.title


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Пользователь, который сделал попытку
    problem = models.ForeignKey(QuizProblem, related_name='attempts', on_delete=models.CASCADE)
    attempt_number = models.PositiveIntegerField(default=1)  # Номер попытки
    answer = models.CharField(max_length=100, default='------------------------2--2-----------#-#--1--')
    is_successful = models.BooleanField(default=False)  # Успешность попытки
    created_at = models.DateTimeField(auto_now_add=True)  # Время попытки


class ContestPage(models.Model):
    contest = models.ForeignKey(Contest, related_name='pages', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)  # Название вкладки
    content = models.TextField()  # Содержимое вкладки
    order = models.IntegerField(default=0)  # Порядок вкладки, если нужно сортировать

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']  # Сортируем страницы по порядку


class BlogPage(models.Model):
    title = models.CharField(max_length=100)  # Название новости
    content = models.TextField()  # Содержимое вкладки
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Внешний ключ к пользователю
    created_at = models.DateTimeField(auto_now_add=True)  # Время создания
    priority = models.IntegerField(default=1000)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['priority', 'created_at']


class SubmissionFile(models.Model):
    file = models.FileField(upload_to='uploads/')  # Сохраняет файл в указанной папке
    file_type = models.CharField(max_length=50, blank=True, null=True)  # Тип файла
    created_at = models.DateTimeField(auto_now_add=True)  # Время создания


class Submission(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)  # Внешний ключ к соревнованию
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Внешний ключ к пользователю
    created_at = models.DateTimeField(auto_now_add=True)  # Время создания
    submission_file = models.ForeignKey(SubmissionFile, on_delete=models.CASCADE)  # Внешний ключ к посылке
    status_code = models.IntegerField(default=0)
    metrics = models.JSONField()


class ContestChecker(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)  # Внешний ключ к соревнованию
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Внешний ключ к пользователю
    created_at = models.DateTimeField(auto_now_add=True)  # Время создания
    checker_file = models.FileField(upload_to='uploads/')  # Сохраняет файл в указанной папке


class ContestCheckerPythonCode(models.Model):
    code = models.TextField()  # Поле для хранения кода
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)  # Внешний ключ к соревнованию
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Внешний ключ к пользователю

    def __str__(self):
        return f"Python code created on {self.created_at}"


class ContestCheckerAnswerFile(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)  # Внешний ключ к соревнованию
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Внешний ключ к пользователю
    file = models.FileField(upload_to='uploads/')  # Сохраняет файл в указанной папке
    file_type = models.CharField(max_length=50, blank=True, null=True)  # Тип файла
    created_at = models.DateTimeField(auto_now_add=True)  # Время создания

    def __str__(self):
        return f"Python code created on {self.created_at}"


class ContestThresholdSubmission(models.Model):
    contest = models.ForeignKey(Contest, related_name='thresholds', on_delete=models.CASCADE)  # Внешний ключ к соревнованию
    title = models.CharField(max_length=100)  # Название порога
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Внешний ключ к пользователю
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)


class ContestTag(models.Model):
    COLOR_CHOICES = [
        ("#FF0000", "Красный"),
        ("#0000FF", "Синий"),
        ("#00FF00", "Зеленый"),
        ("#FFA500", "Оранжевый"),
        ("#FFFF00", "Желтый"),
        ("#800080", "Пурпурный"),
        ("#00FFFF", "Циановый"),
        ("#FFC0CB", "Розовый"),
        ("#000000", "Черный"),
        ("#FFFFFF", "Белый"),  # Добавлен белый цвет
        ("#A52A2A", "Коричневый"),
        ("#808080", "Серый"),
        ("#ADD8E6", "Светло-голубой"),
        ("#FF6347", "Томато"),
        ("#32CD32", "Лаймовый"),
    ]

    contest = models.ForeignKey(Contest, related_name='tag', on_delete=models.CASCADE)  # Внешний ключ к соревнованию
    title = models.CharField(max_length=20)  # Название тега
    color = models.CharField(max_length=7, choices=COLOR_CHOICES, default="#0000FF")  # Цвет
