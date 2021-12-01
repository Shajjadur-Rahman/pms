from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register-user'),
    path('login/', views.LoginUserView.as_view(), name='login-user'),
    path('log-out/', views.LogOutView.as_view(), name='logout-user'),
    path('forget-password/', views.ForgetPassWordView.as_view(), name='forget-password'),

    path('create-manager/', views.AddManagerView.as_view(), name='create-manager'),
    path('member-list/', views.MemberListView.as_view(), name='member-list'),
    path('member/profile/<int:pk>/', views.MemberDetailView.as_view(), name='member-profile'),
    path('create-member/', views.CreateMemberView.as_view(), name='create-member'),
    path('contact-list/', views.ContactListView.as_view(), name='contact-list'),
    path('contact/profile/<int:pk>/', views.ContactDetailView.as_view(), name='contact-profile'),
    path('create-contact/', views.CreateContactView.as_view(), name='create-contact'),
]
