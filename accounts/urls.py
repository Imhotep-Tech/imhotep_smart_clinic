from django.urls import path, include
from . import auth
from . import user_profile, views  # Make sure to add this import

urlpatterns = [
    #the main url
    path("", views.landing_page, name="landing_page"),
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
    path('google/handle-details/', auth.add_details_google_login, name='add_details_google_login'),

    # Add this to your urlpatterns list
    path('update-profile/', user_profile.update_profile, name='update_profile'),
    path('password_change/', user_profile.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', user_profile.CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('activate-profile-update/<str:uidb64>/<str:token>/<str:new_email>/', user_profile.activate_profile_update, name='activate_profile_update'),
]
