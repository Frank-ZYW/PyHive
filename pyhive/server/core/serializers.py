from rest_framework import serializers

from .models import Project, Spider

"""
Define model serialization rules
"""


class ProjectSerializer(serializers.ModelSerializer):
    """
    Project serializer
    """
    client_name = serializers.CharField(allow_null=True, source='client.name')

    class Meta:
        model = Project
        fields = '__all__'


class SpiderSerializer(serializers.ModelSerializer):
    """
    Spider serializer
    """
    project_name = serializers.CharField(allow_null=True, source='project.name')

    class Meta:
        model = Spider
        fields = '__all__'
