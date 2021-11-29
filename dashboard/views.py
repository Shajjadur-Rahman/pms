from django.shortcuts import render, get_object_or_404, reverse
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models import Q
from project.models import Project, Role
from account.models import User
from datetime import datetime
from tzlocal import get_localzone
from account.permission import PermissionForAllUser, AdminAndManagerPermission
from project.forms import ProjectForm, ProjectCreateForm, ProjectUpdateForm, ProjectRoleForm
from django.views.generic import (
    View,
    ListView,
    DetailView,
    UpdateView,
    CreateView,
    DeleteView,
)
from rest_framework import status
from rest_framework.views import APIView
from .serializers import ProjectApproveSerializer
from rest_framework.response import Response
from datetime import datetime
import pytz


def get_current_timezone():  # pip install tzlocal
    tz = get_localzone()
    return tz

class ProjectListView(LoginRequiredMixin, View):
    # template_name = 'project/projects.html'

    def get(self, *args, **kwargs):
        print(self.request.GET.get('search_text', ''))
        if self.request.user.user_type == 'Member' or self.request.user.user_type == 'Contact':

            context = {
               'projects': Project.objects.filter(members=self.request.user, completed=False),
               'total_project': Project.objects.filter(members=self.request.user, completed=False).count(),
               'user': self.request.user,
               'local_tz': get_current_timezone(),
            }
            return render(self.request, 'member_and_contact_profile/member_and_contact_profile.html', context=context)

        context = {
            'projects': Project.objects.filter(completed=False),
            'local_tz': get_current_timezone(),
        }
        return render(self.request, 'project/projects.html', context=context)


class PendingProjectView(LoginRequiredMixin, AdminAndManagerPermission, ListView):
    model         = Project
    template_name = 'project/projects.html'

    def get_context_data(self, *args, **kwargs):
        context = super(PendingProjectView, self).get_context_data(*args, **kwargs)
        context['projects'] = Project.objects.filter(completed=False, approve_status='Pending')
        context['local_tz'] = get_current_timezone()
        context['approve_status'] = 'Pending'
        return context


class CompletedProjectView(LoginRequiredMixin, AdminAndManagerPermission, ListView):
    model         = Project
    template_name = 'project/projects.html'

    def get_context_data(self, *args, **kwargs):
        context = super(CompletedProjectView, self).get_context_data(*args, **kwargs)
        context['projects'] = Project.objects.filter(completed=True, approve_status='Approve')
        context['local_tz'] = get_current_timezone()
        context['completed'] = True
        context['approve_status'] = 'Approve'
        return context


class ApprovedProjectView(LoginRequiredMixin, AdminAndManagerPermission, ListView):
    model         = Project
    template_name = 'project/projects.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ApprovedProjectView, self).get_context_data(*args, **kwargs)
        context['projects'] = Project.objects.filter(approve_status='Approve')
        context['local_tz'] = get_current_timezone()
        context['completed'] = False
        context['approve_status'] = 'Approve'
        return context


class ProjectDetailView(LoginRequiredMixin,DetailView):
    model               = Project
    template_name       = 'project/project_detail.html'
    slug_field          = 'pk'
    slug_url_kwarg      = 'pk'

    def get_context_data(self, *args, **kwargs):
        context            = super(ProjectDetailView, self).get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        context['local_tz'] = get_current_timezone()
        return context



class ProjectUpdateView(LoginRequiredMixin, AdminAndManagerPermission, UpdateView):
    model               = Project
    template_name       = 'project/project_update.html'
    slug_field          = 'pk'
    slug_url_kwarg      = 'pk'
    context_object_name = 'project'
    form_class          = ProjectUpdateForm
    success_url         = '/'

    def get_context_data(self, *args, **kwargs):
        context            = super(ProjectUpdateView, self).get_context_data(**kwargs)
        context['local_tz'] = get_current_timezone()
        return context



class ProjectApproveApiView(APIView):
    def post(self, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        project.approve_status = 'Approve'
        project.approve_by = self.request.user
        project.save()
        return Response({'approve_status': project.approve_status}, status=status.HTTP_200_OK)



class ProjectDeleteApiView(LoginRequiredMixin, AdminAndManagerPermission, APIView):
    def post(self, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        # project.delete()
        return Response({'success': 'Project successfully deleted !'}, status=status.HTTP_200_OK)


class CreateProjectView(LoginRequiredMixin, AdminAndManagerPermission, SuccessMessageMixin, CreateView):

    model               = Project
    template_name       = 'project/project_create.html'
    form_class          = ProjectCreateForm
    success_message     = 'Project successfully created'

    def get_success_url(self):
        return reverse('dashboard:project-add')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.save()
        return super(CreateProjectView, self).form_valid(form)




class AddProjectDateAndRole(LoginRequiredMixin, AdminAndManagerPermission, View):
    def get(self, *args, **kwargs):
        title     = self.kwargs['title']
        try:
            project = Project.objects.get(id=self.kwargs['pk'])
        except:
            project = None
        role_form = ProjectRoleForm()
        if project.start_time and project.end_time:
            return render(self.request, 'project/add_project_date_and_role.html',
                          context={'role_form': role_form, 'title': title, 'project': False})
        else:
            return render(self.request, 'project/add_project_date_and_role.html',
                          context={'role_form': role_form, 'title': title, 'project': True})

    def post(self, *args, **kwargs):
        role_form = ProjectRoleForm(self.request.POST)
        try:
            project = Project.objects.get(id=self.kwargs['pk'])
        except:
            project = None
        role_obj = Role()
        member = self.request.POST['member']
        if role_form.is_valid():
            role_start_datetime = str(self.request.POST['role_start_date_time'])
            role_start_datetime = datetime.strptime(role_start_datetime, '%m/%d/%Y %I:%M %p')

            # Native datetime to UTC server datetime conversion
            utc_role_start_datetime = datetime.combine(role_start_datetime.date(), role_start_datetime.time())
            utc_role_start_datetime = utc_role_start_datetime.astimezone(pytz.utc)

            role_end_datetime = str(self.request.POST['role_end_date_time'])
            role_end_datetime = datetime.strptime(role_end_datetime, '%m/%d/%Y %I:%M %p')

            # Native datetime to UTC server datetime conversion
            utc_role_end_datetime = datetime.combine(role_end_datetime.date(), role_end_datetime.time())
            utc_role_end_datetime = utc_role_end_datetime.astimezone(pytz.utc)

            project_start_datetime = str(self.request.POST['project_start_date_time'])
            project_start_datetime = datetime.strptime(project_start_datetime, '%m/%d/%Y %I:%M %p')

            # Native datetime to UTC server datetime conversion
            utc_project_start_datetime = datetime.combine(project_start_datetime.date(), project_start_datetime.time())
            utc_project_start_datetime = utc_project_start_datetime.astimezone(pytz.utc)

            project_end_datetime = str(self.request.POST['project_end_date_time'])
            project_end_datetime = datetime.strptime(project_end_datetime, '%m/%d/%Y %I:%M %p')

            # Native datetime to UTC server datetime conversion
            utc_project_end_datetime = datetime.combine(project_end_datetime.date(), project_end_datetime.time())
            utc_project_end_datetime = utc_project_end_datetime.astimezone(pytz.utc)

            role_title = role_form.cleaned_data['role_title']
            role_obj.role_title = role_title
            role_obj.member_id = member
            role_obj.start_time = utc_role_start_datetime
            role_obj.end_time = utc_role_end_datetime
            role_obj.save()
            if project is not None:
                if project.start_time and project.end_time:
                    project.project_roles.add(role_obj)
                    pass
                else:
                    project.start_time = utc_project_start_datetime
                    project.end_time = utc_project_end_datetime
                    project.save()
                    project.project_roles.add(role_obj)

                if project.start_time and project.end_time:
                    return render(self.request, 'project/add_project_date_and_role.html',
                                  context={'role_form': role_form, 'project': False})
                else:
                    return render(self.request, 'project/add_project_date_and_role.html',
                                  context={'role_form': role_form, 'project': True})





class DeleteProjectView(LoginRequiredMixin, AdminAndManagerPermission, View):
    def get(self, *args, **kwargs):
        project = get_object_or_404(Project, id=self.kwargs['pk'])
        project.delete()
        messages.warning(self.request, 'Project deleted successfully !')
        return HttpResponseRedirect(reverse('dashboard:projects-list'))









