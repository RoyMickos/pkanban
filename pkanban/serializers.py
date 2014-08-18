from rest_framework import serializers
from rest_framework.pagination import PaginationSerializer
from pkanban import models
from django.contrib.auth.models import User


class LogSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.PkLog
    fields = ('time', 'event')
    read_only_fields = ('time',)

class TaskSerializer(serializers.ModelSerializer):
  logs = LogSerializer(many=True, read_only=True)
  class Meta:
    model = models.PkTask
    fields = ('id', 'name', 'description', 'completed', 'effort', 'lastmodify', 'valuestream', 'logs')
    read_only_fields = ('valuestream', 'completed')

class PaginatedTaskSerializer(PaginationSerializer):
  class Meta:
    object_serializer_class = TaskSerializer

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('id', 'username')

class PhaseSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.PkWorkPhases
    fields = ('name', 'capacity', 'description')

class WipSerializer(serializers.ModelSerializer):
  phase = serializers.SlugRelatedField(read_only=True, slug_field='name')
  #task = TaskSerializer()
  class Meta:
    model = models.PkWipTasks
    fields = ('phase', 'task')

class ValueStreamSerializer(serializers.ModelSerializer):
  phases = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
  class Meta:
    model = models.PkValuestream
    fields = ('streamname', 'phases')

class ValueStreamIdentitySerializer(serializers.ModelSerializer):
  class Meta:
    model = models.PkValuestream
    fields = ('streamname',)
