from django import template
from project.models import Project

register = template.Library()

@register.filter
def confirmed_m_or_c(user):
    return Project.objects.filter(confirm_members=user.pk)