from django.urls import path
from django.contrib import admin
from django.urls import path, include
from .views import main, register, user_login, contests, logout_view, contests_view, contest_detail_view_admin, contest_detail_view, \
    contest_detail_view_admin_checker, contest_detail_results, contest_participants_admin, contest_detail_submissions, \
    admin_panel, blank_page

from django.contrib.auth import views as auth_views

from .quiz_logic_service.quiz_logic import edit_quiz_problem, quiz_view, quiz_field_view, quiz_buy_problem, quiz_results, quiz_participants_admin, \
    quiz_realtime_log, api_get_quiz_last_attempts, quiz_edit_user_profile, api_get_quiz_current_results, quiz_realtime_results, quiz_edit_user_attempts, \
    quiz_field_editor

from .image_processing_service.image_logic import upload_image, image_list

from . import views
# from webproject import *
from django.conf import settings
from django.conf.urls.static import static

from .forms import CustomAuthenticationForm  # Импортируем кастомную форму входа

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main, name='main'),

    path('image_list/', image_list, name="image_list"),
    path('upload_image/', upload_image, name="upload_image"),

    path('blank_page/', blank_page, name="blank_page"),
    path('quiz_realtime_log/<int:contest_id>', quiz_realtime_log, name="quiz_realtime_log"),
    path("api/get_quiz_last_attempts/", api_get_quiz_last_attempts, name="api_get_quiz_last_attempts"),
    path('quiz_realtime_results/<int:contest_id>', quiz_realtime_results, name="quiz_realtime_results"),
    path("api/get_quiz_current_results/", api_get_quiz_current_results, name="api_get_quiz_current_results"),

    path('quiz/edit_profile/<int:quiz_user_id>/', quiz_edit_user_profile, name='quiz_edit_userprofile'),
    path('quiz/edit_user_attempts/<int:quiz_user_id>/', quiz_edit_user_attempts, name='quiz_edit_user_attempts'),

    path('contests/', contests_view, name='contests'),
    path('quizzes/', quiz_view, name='quizzes'),
    path('quiz_field/<int:contest_id>/', quiz_field_view, name='quiz_field'),
    path('quiz_field/edit/<int:quiz_field_id>/', quiz_field_editor, name='quiz_field_editor'),
    path('edit_quiz_problem/<int:quiz_problem_id>/', edit_quiz_problem, name='edit_quiz_problem'),
    path('buy_quiz_problem/<int:quiz_problem_id>/', quiz_buy_problem, name='quiz_buy_problem'),
    path('quiz_results/<int:contest_id>/', quiz_results, name='quiz_results'),
    path('quiz_participants_admin/<int:contest_id>/', quiz_participants_admin, name='quiz_participants_admin'),

    path('contests/admin/<int:contest_id>/', contest_detail_view_admin, name='contest_detail_admin'),
    path('admin_panel/', admin_panel, name='admin_panel'),
    path('contests/<int:contest_id>/', contest_detail_view, name='contest_detail'),

    path('register/', register, name='register'),
    path('login/',
         auth_views.LoginView.as_view(template_name='myapp/login.html', authentication_form=CustomAuthenticationForm),
         name='login'),
    path('logout/', logout_view, name='logout'),

    path('contest/page/<int:page_id>/edit/', views.edit_contest_page, name='edit_contest_page'),  # Новый маршрут
    path('contest/page/<int:page_id>/delete/', views.delete_contest_page, name='delete_contest_page'),  # Новый маршрут для удаления
    path('submitfile/', views.submit_file, name='submit_file'),
    path('editblog/edit/<int:blog_id>/', views.main_blog_edit, name='edit_existing_blog'),
    path('editblog/new/', views.main_blog_edit, name='create_new_blog'),
    path('editblog/delete/<int:blog_id>/', views.main_blog_delete, name='delete_existing_blog'),
    path('move_contest_page/<int:page_id>/<str:direction>/', views.move_contest_page, name='move_contest_page'),
    path('contests/admin/checker/<int:contest_id>/', contest_detail_view_admin_checker, name='contest_detail_admin_checker'),
    path('contests/results/<int:contest_id>/', contest_detail_results, name='contest_detail_results'),
    path('contests/submissions/<int:contest_id>/', contest_detail_submissions, name='contest_detail_submissions'),
    path('contests/participants_admin/<int:contest_id>/', contest_participants_admin, name='contest_participants_admin'),

]

# Для разработки, чтобы сервер мог обслуживать медиа файлы
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
