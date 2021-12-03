from django.contrib import admin
from .models import (
    Role,
    Project,
    AttachmentFile
)

admin.site.register(Role)
admin.site.register(Project)
admin.site.register(AttachmentFile)

