# a form for entering task data
from django import forms
from models import PkTask

class TaskForm(forms.ModelForm):
    #name = forms.CharField(max_length=150, required=True)
    #description = forms.CharField()
    class Meta:
        model = PkTask
        #exclude = ['completed','effort','lastmodify']
        fields = ['name', 'description']
    
#class PhaseForm(forms.ModelForm):
#    class Meta:
#        model = PkWorkPhases

    