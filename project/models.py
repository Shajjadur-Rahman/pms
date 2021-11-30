from django.db import models
from django.conf import settings
from datetime import datetime
from django.template.defaultfilters import truncatechars


class Project(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Approve', 'Approve'),
        ('Cancel', 'Cancel')
    )
    members          = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='members', blank=True)
    created_by       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    project_roles    = models.ManyToManyField('Role', blank=True, related_name='roles')
    title            = models.CharField(max_length=350)
    project_leader   = models.ForeignKey(settings.AUTH_USER_MODEL,  on_delete=models.SET_NULL, blank=True, null=True,
                                         related_name='project_leader')
    description      = models.TextField()
    approve_status   = models.CharField(max_length=20, choices=STATUS, default='Pending')
    approve_by       = models.ForeignKey(settings.AUTH_USER_MODEL,
                                         on_delete=models.SET_NULL,
                                         related_name='projects_approved_by', null=True, blank=True)
    public           = models.BooleanField(blank=True)
    public_shared    = models.DateTimeField(null=True, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)
    confirm_members  = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='confirm_members', blank=True)
    completed        = models.BooleanField(default=False)

    start_time = models.DateTimeField(null=True, blank=True)
    end_time   = models.DateTimeField(null=True, blank=True)



    def __str__(self):
        return self.title

    @property
    def sliced_description(self):
        return truncatechars(self.description, 500)



class Role(models.Model):
    member     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='member_roles')
    role_title = models.CharField(max_length=350)
    start_time = models.DateTimeField()
    end_time   = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed  = models.BooleanField(default=False)


    def __str__(self):
        return self.role_title




