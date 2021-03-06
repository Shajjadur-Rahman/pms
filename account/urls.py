from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register-user'),
    path('login/', views.LoginUserView.as_view(), name='login-user'),
    path('log-out/', views.LogOutView.as_view(), name='logout-user'),
    path('forget-password/', views.ForgetPassWordView.as_view(), name='forget-password'),
    path('reset-password/<token>/', views.PasswordResetView.as_view(), name='reset-password'),

    path('create-manager/', views.AddManagerView.as_view(), name='create-manager'),
    path('member-list/', views.MemberListView.as_view(), name='member-list'),
    path('create-member/', views.CreateMemberView.as_view(), name='create-member'),
    path('contact-list/', views.ContactListView.as_view(), name='contact-list'),
    path('contact/profile/<int:pk>/', views.ContactAndMemberDetailView.as_view(), name='contact-profile'),
    path('member/profile/<int:pk>/', views.ContactAndMemberDetailView.as_view(), name='member-profile'),
    path('create-contact/', views.CreateContactView.as_view(), name='create-contact'),
]
