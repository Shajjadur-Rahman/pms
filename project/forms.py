from django import forms
from django.forms import CheckboxSelectMultiple
from .models import Project, Role
from account.models import User
from django.db.models import Q
import django_filters


class ProjectRoleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectRoleForm, self).__init__(*args, **kwargs)
        self.fields['role_title'].widget.attrs.update({'class': 'form-control'})
    class Meta:
        model  = Role
        fields = ['role_title', ]


class AddCrewInRoleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddCrewInRoleForm, self).__init__(*args, **kwargs)
        self.fields['member'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model  = Role
        fields = ['member', ]




class ProjectForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(required=False, queryset=User.objects.filter(Q(user_type='Contact') | Q(user_type='Member')), widget=forms.CheckboxSelectMultiple())
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['members'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['public'].widget.attrs.update({'class': 'form-check-input'})


    class Meta:
        model  = Project
        fields = ['members', 'title', 'description', 'public']



class ProjectCreateForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(required=False, queryset=User.objects.filter(Q(user_type='Contact') | Q(user_type='Member')), widget=forms.CheckboxSelectMultiple())
    project_leader = forms.ModelChoiceField(required=False, queryset=User.objects.filter(Q(user_type='Contact') | Q(user_type='Member') | Q(user_type='Manager')))
    def __init__(self, *args, **kwargs):
        super(ProjectCreateForm, self).__init__(*args, **kwargs)
        self.fields['members'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['project_leader'].widget.attrs.update({'class': 'form-control'})
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Input project name / title'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Input project description'})
        self.fields['public'].widget.attrs.update({'id': 'checkboxPrimary2'})

    class Meta:
        model  = Project
        fields = ['members', 'title', 'project_leader', 'description', 'public']



class ProjectUpdateForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(required=False, queryset=User.objects.filter(Q(user_type='Contact') | Q(user_type='Member')), widget=forms.CheckboxSelectMultiple())
    project_leader = forms.ModelChoiceField(required=False, queryset=User.objects.filter(Q(user_type='Contact') | Q(user_type='Member') | Q(user_type='Member')))
    def __init__(self, *args, **kwargs):
        super(ProjectUpdateForm, self).__init__(*args, **kwargs)
        self.fields['members'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['project_leader'].widget.attrs.update({'class': 'form-control'})
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Input project name / title'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Input project description'})
        self.fields['public'].widget.attrs.update({'id': 'checkboxPrimary2'})

    class Meta:
        model  = Project
        fields = ['members', 'title', 'project_leader', 'description', 'public']