from django.contrib import admin
from .models import (
    Role,
    Project
)

admin.site.register(Role)
admin.site.register(Project)

