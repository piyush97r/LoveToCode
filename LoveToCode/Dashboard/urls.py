from django.urls import path,re_path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('signup/',views.signup,name='signup'),
    path('login/',views.login,name='login'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('admin/',views.admin,name='admin'),   
    path('dashboard/practice',views.practice,name="practice"),
    path('dashboard/leaderboard',views.leaderboard,name="leaderboard"),
    path('dashboard/profile',views.profile,name='profile'),
    re_path('dashboard/practice/question/\d+$',views.question,name="question"),
    re_path('dashboard/practice/question/\d+/discussion$',views.discussion,name="discussion"),
    re_path('dashboard/practice/question/\d+/answer',views.answer,name='answer'),
    path('dashboard/error_or_out',views.error_or_out,name="error_or_out"),
]
