from django.urls import path
from django.contrib import admin
from django.urls import path, include
from .views import main, register, user_login, contests, logout_view, contests_view, contest_detail_view_admin, contest_detail_view, \
    contest_detail_view_admin_checker, contest_detail_results, contest_participants_admin
from django.contrib.auth import views as auth_views
from . import views

from .forms import CustomAuthenticationForm  # Импортируем кастомную форму входа

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main, name='main'),
    path('contests/', contests_view, name='contests'),
    path('contests/admin/<int:contest_id>/', contest_detail_view_admin, name='contest_detail_admin'),
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
    path('contests/participants_admin/<int:contest_id>/', contest_participants_admin, name='contest_participants_admin'),

]

