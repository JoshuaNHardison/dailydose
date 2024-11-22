from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Main route for your app
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),
    path('trivia/<int:trivia_id>/', views.trivia_detail, name='trivia_detail'),
    path('toggle_bookmark/<int:trivia_id>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('bookmarked/', views.index, name='bookmarked'),
    path('add_trivia/', views.add_trivia, name="add_trivia"),
    path('record_trivia_result/', views.record_trivia_result, name='record_trivia_result'),
    path('create_or_update_trivia_record/<int:trivia_id>/', views.create_or_update_trivia_record, name='create_or_update_trivia_record'),
    path('dailytrivia/profile/<str:username>', views.profile, name='profile'),

]
