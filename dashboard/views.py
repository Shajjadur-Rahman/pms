from django.shortcuts import render, get_object_or_404, reverse
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from project.models import Project, Role, AttachmentFile
from account.models import User, Profile
from datetime import datetime
from tzlocal import get_localzone
from account.permission import PermissionForAllUser, AdminAndManagerPermission
from project.forms import ProjectForm, ProjectCreateForm, ProjectUpdateForm, ProjectRoleForm, AddCrewInRoleForm
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


# ==========================================================
def native_to_utc_1(dt):
    utc_dt = dt.combine(dt.now().date(), dt.now().time())
    utc__datetime = utc_dt.astimezone(pytz.utc)
    return utc__datetime

# ============================================================

class ProjectListView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        approve_status = self.request.GET.get('approve_status', '')
        if self.request.user.user_type == 'Member' or self.request.user.user_type == 'Contact':
            projects = Project.objects.filter(Q(members=self.request.user) |
                                              Q(confirm_members=self.request.user), Q(completed=False)
                                              )
            total_project = projects.count()
            if approve_status:
                projects = projects.filter(approve_status=approve_status)
            paginator     = Paginator(projects, 4)
            page_number   = self.request.GET.get('page')
            projects      = paginator.get_page(page_number)
            context       = {
               'projects': projects,
               'total_project': total_project,
               'user': self.request.user,
               'local_tz': get_current_timezone(),
            }
            return render(self.request, 'member_and_contact_profile/member_and_contact_profile.html', context=context)

        context = {
            'projects': Project.objects.filter(completed=False),
            'local_tz': get_current_timezone(),
        }
        return render(self.request, 'project/projects.html', context=context)


class ProjectRequestAcceptApiView(APIView):
    def post(self, *args, **kwargs):
        project        = get_object_or_404(Project, pk=self.kwargs['pk'])
        project.confirm_members.add(self.request.user.id)
        project.members.remove(self.request.user.id)
        project.save()
        return Response({'approve_status': 'Confirmed', 'approved_msg': f"You added this project : {project.title}"}, status=status.HTTP_200_OK)



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

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        if form.cleaned_data['public']:
            form.instance.public_shared = native_to_utc_1(datetime)
        else:
            form.instance.public_shared = None
        self.object = form.save()
        images = self.request.FILES.getlist('file_name')
        for image in images:
            project = AttachmentFile.objects.create(project_id=self.object.id)
            project.attach_file = image
            project.save()
        return super(ProjectUpdateView, self).form_valid(form)


class ProjectApproveApiView(APIView):
    def post(self, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        project.approve_status = 'Approve'
        project.approve_by = self.request.user
        project.save()
        return Response({'approve_status': project.approve_status, 'approved_msg': 'Project approved !'}, status=status.HTTP_200_OK)



class ProjectDeleteApiView(APIView):
    def post(self, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        project.delete()
        return Response({'success': 'Project successfully deleted !'}, status=status.HTTP_200_OK)


class AttachFileDeleteApiView(APIView):
    def post(self, *args, **kwargs):
        file = get_object_or_404(AttachmentFile, pk=self.kwargs['pk'])
        file.delete()
        return Response({'success': 'Attachment file successfully deleted !'}, status=status.HTTP_200_OK)


class CreateProjectView(LoginRequiredMixin, AdminAndManagerPermission, SuccessMessageMixin, CreateView):
    model               = Project
    template_name       = 'project/project_create.html'
    form_class          = ProjectCreateForm
    success_message     = 'Project successfully created'

    def get_success_url(self):
        return reverse('dashboard:project-add')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        if form.cleaned_data['public']:
            form.instance.public_shared = native_to_utc_1(datetime)
        self.object = form.save()
        images = self.request.FILES.getlist('file_name')
        for image in images:
            project = AttachmentFile.objects.create(project_id=self.object.id)
            project.attach_file = image
            project.save()
        return super(CreateProjectView, self).form_valid(form)



# =================================================

def native_to_utc_2(dt):
    str_date = str(dt)
    formatted_dt = datetime.strptime(str_date, '%m/%d/%Y %I:%M %p')
    combine_datetime = formatted_dt.combine(formatted_dt.date(), formatted_dt.time())
    utc_datetime = combine_datetime.astimezone(pytz.utc)
    return utc_datetime

# =================================================


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
                          context={'role_form': role_form, 'title': title,  'datetime_add': False, 'project': project})
        else:
            return render(self.request, 'project/add_project_date_and_role.html',
                          context={'role_form': role_form, 'title': title, 'datetime_add': True, 'project': project})


    def post(self, *args, **kwargs):
        role_form = ProjectRoleForm(self.request.POST)
        try:
            project = Project.objects.get(id=self.kwargs['pk'])
        except:
            project = None
        try:
            member = self.request.POST['member']
        except:
            member = None
        if role_form.is_valid():
            role_start_datetime = self.request.POST.get('role_start_date_time', '')
            role_start_datetime = native_to_utc_2(role_start_datetime) # Native datetime to UTC server datetime conversion
            role_end_datetime = self.request.POST.get('role_end_date_time', '')
            role_end_datetime = native_to_utc_2(role_end_datetime)

            project_start_datetime = self.request.POST.get('project_start_date_time', '')
            if project_start_datetime:
                project_start_datetime = native_to_utc_2(project_start_datetime)
            project_end_datetime = self.request.POST.get('project_end_date_time', '')
            if project_end_datetime:
                project_end_datetime = native_to_utc_2(project_end_datetime)
            role_form_obj = role_form.save(commit=False)

            if member:
                role_form_obj.member_id = member
            role_form_obj.project_id = project.id
            role_form_obj.start_time = role_start_datetime
            role_form_obj.end_time = role_end_datetime
            role_form_obj.save()
            if project is not None:
                if project.start_time and project.end_time:
                    pass
                else:
                    project.start_time = project_start_datetime
                    project.end_time = project_end_datetime
                    project.save()
                if project.start_time and project.end_time:
                    return render(self.request, 'project/add_project_date_and_role.html',

                                  context={'role_form': role_form,  'datetime_add': False, 'project': project})
                else:
                    return render(self.request, 'project/add_project_date_and_role.html',
                                  context={'role_form': role_form,  'datetime_add': True, 'project': project})



class AddCrewInRoleView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        title   = self.kwargs['title']
        role    = get_object_or_404(Role, id=self.kwargs['role_id'])
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        form    = AddCrewInRoleForm(instance=role)
        context = {'form': form, 'title': title, 'role': role, 'project': project}
        return render(self.request, 'project/add_crew_in_role.html', context=context)

    def post(self, *args, **kwargs):
        url = self.request.META.get('HTTP_REFERER')
        role  = get_object_or_404(Role, id=self.kwargs['role_id'])
        form = AddCrewInRoleForm(self.request.POST, instance=role)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(url)












