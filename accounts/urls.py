from django.urls import path, include
from . import  auth

urlpatterns = [
    #the main url
    #the register url
    path("register/", auth.register, name="register"),
    #login url
    path("login/", auth.user_login, name="login"),
    #logout url
    path("logout/", auth.user_logout, name="logout"),
    
    #URL to activate the users account with the Email
    path('activate/<uidb64>/<token>/', auth.activate, name='activate'),

    #URLs for the forget password
    path('password_reset/', auth.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('google/login/', auth.google_login, name='google_login'),
    path('google/callback/', auth.google_callback, name='google_callback'),
    path('google/handle-username/', auth.add_username_google_login, name='add_username_google_login'),
]
