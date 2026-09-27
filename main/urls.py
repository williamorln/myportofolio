from django.urls import path

from main.views import (
    create_experience,
    update_experience,
    delete_experience,
    get_experience_json,
    create_project,
    delete_project,
    get_projects_json,
    login_user,
    logout_user,
    register,
    show_experience,
    show_main,
    show_projects,
    toggle_star,
)


app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('experience/', show_experience, name='show_experience'),
    path('experience/add/', create_experience, name='create_experience'),
    path('experience/<uuid:experience_id>/edit/', update_experience, name='update_experience'),
    path('experience/<uuid:experience_id>/delete/', delete_experience, name='delete_experience'),
    path('api/experience/', get_experience_json, name='get_experience_json'),
    path('projects/', show_projects, name='show_projects'),
    path('projects/add/', create_project, name='create_project'),
    path('projects/<uuid:project_id>/delete/', delete_project, name='delete_project'),
    path('projects/<uuid:project_id>/star/', toggle_star, name='toggle_star'),
    path('api/projects/', get_projects_json, name='get_projects_json'),
]
