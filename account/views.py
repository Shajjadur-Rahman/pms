from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login, logout, authenticate
from .forms import CustomUserCreationForm, ProfileForm
from .models import User, Profile
from project.models import Project
from dashboard.views import get_current_timezone
from account.permission import PermissionForAllUser, AdminAndManagerPermission
from .helpers import forget_password_mail
import uuid



class RegisterView(generic.View):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('dashboard:projects-list'))
        form = CustomUserCreationForm()
        return render(self.request, 'account/register.html', context={'form': form})

    def post(self, *args, **kwargs):
            form = CustomUserCreationForm(self.request.POST)
            if form.is_valid():
                form_obj = form.save(commit=False)
                form_obj.user_type = 'Contact'
                form_obj.save()
                return HttpResponseRedirect(reverse_lazy('account:login-user'))
            return render(self.request, 'account/register.html', context={'form': form})



class LoginUserView(generic.View):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('dashboard:projects-list'))
        return render(self.request, 'account/login.html')

    def post(self, *args, **kwargs):
        email = self.request.POST.get('email')
        password = self.request.POST.get('password')
        if email and password:
            user = authenticate(self.request, email=email, password=password)
            if user is not None:
                login(self.request, user)
                return HttpResponseRedirect(reverse_lazy('dashboard:projects-list'))
        return render(self.request, 'account/login.html')



class LogOutView(generic.View):
    def get(self, *args, **kwargs):
        logout(self.request)
        return HttpResponseRedirect(reverse_lazy('account:login-user'))




class ForgetPassWordView(generic.View):
    email_not_fount = ''
    email_sent_success = ''
    def get(self, *args, **kwargs):
        return render(self.request, 'account/password_reset/forget_password.html')

    def post(self, *args, **kwargs):
        email = self.request.POST['email']
        user = User.objects.filter(email=email).first()
        if not user:
            self.email_not_fount = 'No user fount with this email !'
            return render(self.request, 'account/password_reset/forget_password.html', {'reset_msg': self.email_not_fount})
        token    = str(uuid.uuid4())
        user_obj = User.objects.get(email=self.request.POST['email'])
        user_obj.pass_token = token
        user_obj.save()
        forget_password_mail(user_obj.email, token)
        self.email_sent_success = 'An email is sent . Check your inbox Please!'
        return render(self.request, 'account/password_reset/forget_password.html', {'reset_msg': self.email_sent_success})



class PasswordResetView(generic.View):
    password_error = ''
    user_not_fount = ''
    def get(self, *args, **kwargs):
        token = self.kwargs['token']
        return render(self.request, 'account/password_reset/reset_password_form.html')

    def post(self, *args, **kwargs):
        new_password = self.request.POST.get('new_password')
        confirm_password = self.request.POST.get('confirm_password')
        if new_password != confirm_password:
            self.password_error = "Password mismatch ! Try again ...."
            return render(self.request, 'account/password_reset/reset_password_form.html', {'reset_msg': self.password_error})

        user_obj = User.objects.filter(pass_token=self.kwargs['token']).first()
        if not user_obj:
            self.password_error = "Account not fount ! Something went wrong ....!"
            return render(self.request, 'account/password_reset/reset_password_form.html', {'reset_msg': self.user_not_fount})
        user = User.objects.get(id=user_obj.id)
        user.set_password(new_password)
        user.save()
        return HttpResponseRedirect(reverse_lazy('account:login-user'))



class AddManagerView(LoginRequiredMixin, AdminAndManagerPermission, generic.View):

    def get(self, *args, **kwargs):
        form = CustomUserCreationForm()
        return render(self.request, 'manager_member_and_contact/create_user.html', context={'form': form, 'user_type': 'Manager'})

    def post(self, *args, **kwargs):
        form = CustomUserCreationForm(self.request.POST)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.user_type = 'Manager'
            form_obj.save()
            messages.success(self.request, 'New Manager successfully created !')
            return HttpResponseRedirect(reverse('account:create-manager'))
        return render(request, 'manager_member_and_contact/create_user.html', context={'form': form, 'user_type': 'Manager'})


class MemberListView(LoginRequiredMixin, generic.View):
    def get(self, *args, **kwargs):
        search_text = self.request.GET.get('search_text', '')
        members     = User.objects.filter(user_type='Member')
        if search_text:
            members = members.filter(
                Q(username__icontains=search_text) |
                Q(email__icontains=search_text) |
                Q(profile__phone_no=search_text)
            )
        local_tz = get_current_timezone()
        paginator = Paginator(members, 5)
        page_number = self.request.GET.get('page')
        members = paginator.get_page(page_number)
        context = {
            'members': members,
            'local_tz': local_tz
        }
        return render(self.request, 'manager_member_and_contact/member/member_list.html', context=context)


class CreateMemberView(LoginRequiredMixin, AdminAndManagerPermission, generic.View):
    def get(self, *args, **kwargs):
        form = CustomUserCreationForm()
        return render(self.request, 'manager_member_and_contact/create_user.html', context={'form': form, 'user_type': 'Member'})

    def post(self, *args, **kwargs):
        form = CustomUserCreationForm(self.request.POST)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.user_type = 'Member'
            form_obj.save()
            messages.success(self.request, 'New Member successfully created !')
            return HttpResponseRedirect(reverse('account:create-member'))
        return render(self.request, 'manager_member_and_contact/create_user.html', context={'form': form, 'user_type': 'Member'})



class ContactListView(LoginRequiredMixin, generic.View):
    def get(self, *args, **kwargs):
        search_text = self.request.GET.get('search_text', '')
        contacts    = User.objects.filter(user_type='Contact')
        if search_text:
            contacts = contacts.filter(
                Q(username__icontains=search_text) |
                Q(email__icontains=search_text) |
                Q(profile__phone_no=search_text)
            )
        local_tz    = get_current_timezone()
        paginator   = Paginator(contacts, 5)
        page_number = self.request.GET.get('page')
        contacts    = paginator.get_page(page_number)
        context     = {
            'contacts': contacts,
            'local_tz': local_tz
        }
        return render(self.request, 'manager_member_and_contact/contact/contact_list.html', context=context)


class ContactAndMemberDetailView(LoginRequiredMixin, generic.View):
    def get(self, *args, **kwargs):
        search_text = self.request.GET.get('search_text', '')
        user         = get_object_or_404(User, pk=self.kwargs['pk'])
        projects     = Project.objects.filter(members=self.kwargs['pk'], public=True)
        if search_text:
            projects = projects.filter(
                Q(title__icontains=search_text) |
                Q(description__icontains=search_text)
            )
        ttl_projects = projects.count()
        local_tz     = get_current_timezone()
        paginator    = Paginator(projects, 2)
        page_number  = self.request.GET.get('page')
        projects     = paginator.get_page(page_number)
        context      = {
            'user': user,
            'projects': projects,
            'ttl_projects': ttl_projects,
            'local_tz': local_tz
        }
        return render(self.request, 'manager_member_and_contact/user_detail.html', context=context)



class CreateContactView(LoginRequiredMixin, AdminAndManagerPermission, generic.View):
    def get(self, *args, **kwargs):
        form = CustomUserCreationForm()
        return render(self.request, 'manager_member_and_contact/create_user.html', context={'form': form, 'user_type': 'Contact'})

    def post(self, *args, **kwargs):
        form = CustomUserCreationForm(self.request.POST)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.user_type = 'Contact'
            form_obj.save()
            messages.success(self.request, 'New Contact successfully created !')
            return HttpResponseRedirect(reverse('account:create-contact'))
        return render(self.request, 'manager_member_and_contact/create_user.html', context={'form': form, 'user_type': 'Contact'})