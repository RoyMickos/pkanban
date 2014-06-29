from rest_framework import serializers
from pkanban import models
from django.contrib.auth.models import User


class LogSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.PkLog
    fields = ('time', 'event')
    read_only_fields = ('time',)

class TaskSerializer(serializers.ModelSerializer):
  logs = LogSerializer(many=True)
  class Meta:
    model = models.PkTask
    fields = ('name', 'description', 'completed', 'effort', 'lastmodify', 'valuestream', 'logs')

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('id', 'username')
