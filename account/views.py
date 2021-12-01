from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
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
    def get(self, *args, **kwargs):
        return render(self.request, 'account/password_reset/forget_password.html')

    def post(self, *args, **kwargs):
        email = self.request.POST['email']
        user = User.objects.filter(email=email).first()
        if not user:
            self.email_not_fount = 'No user fount with this email !'
            return render(self.request, 'account/password_reset/forget_password.html', {'error': self.email_not_fount})
        token    = str(uuid.uuid4())
        user_obj = User.objects.get(email=self.request.POST['email'])
        user_obj.pass_token = token
        user_obj.save()
        forget_password_mail(user_obj, token)
















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



class MemberListView(LoginRequiredMixin, generic.ListView):
    model         = User
    template_name = 'manager_member_and_contact/member/member_list.html'
    context_object_name = 'members'

    def get_queryset(self, *args, **kwargs):
        search_text = self.request.GET.get('search_text', '')
        members     = User.objects.filter(user_type='Member')
        if search_text:
            members = members.filter(
                Q(username__icontains=search_text) |
                Q(email__icontains=search_text) |
                Q(profile__phone_no=search_text)
            )
            return members
        return members

    def get_context_data(self, *args, **kwargs):
        context = super(MemberListView, self).get_context_data(**kwargs)
        context['local_tz'] = get_current_timezone()
        return context


class MemberDetailView(LoginRequiredMixin, generic.DetailView):
    model               = User
    template_name       = 'manager_member_and_contact/user_detail.html'
    slug_field          = 'pk'
    slug_url_kwarg      = 'pk'

    def get_context_data(self, *args, **kwargs):
        context            = super(MemberDetailView, self).get_context_data(**kwargs)
        context['user'] = get_object_or_404(User, pk=self.kwargs['pk'])
        context['projects'] = Project.objects.filter(members=self.kwargs['pk'])
        context['local_tz'] = get_current_timezone()
        return context



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
        return render(request, 'manager_member_and_contact/create_user.html', context={'form': form, 'user_type': 'Member'})



class ContactListView(LoginRequiredMixin, generic.ListView):
    model               = User
    template_name       = 'manager_member_and_contact/contact/contact_list.html'
    context_object_name = 'contacts'

    def get_queryset(self, *args, **kwargs):
        search_text = self.request.GET.get('search_text', '')
        contacts    = User.objects.filter(user_type='Contact')
        if search_text:
            contacts = contacts.filter(
                Q(username__icontains=search_text) |
                Q(email__icontains=search_text) |
                Q(profile__phone_no=search_text)
            )
            return contacts
        return contacts

    def get_context_data(self, *args, **kwargs):
        context = super(ContactListView, self).get_context_data(**kwargs)
        context['local_tz'] = get_current_timezone()
        return context



class ContactDetailView(LoginRequiredMixin, generic.DetailView):
    model               = User
    template_name       = 'manager_member_and_contact/user_detail.html'
    slug_field          = 'pk'
    slug_url_kwarg      = 'pk'

    def get_context_data(self, *args, **kwargs):
        context            = super(ContactDetailView, self).get_context_data(**kwargs)
        context['user'] = get_object_or_404(User, pk=self.kwargs['pk'])
        context['projects'] = Project.objects.filter(members=self.kwargs['pk'])
        context['local_tz'] = get_current_timezone()
        return context


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