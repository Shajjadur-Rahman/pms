from rest_framework import serializers
from project.models import Project


class ProjectApproveSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Project
        fields = '__all__'