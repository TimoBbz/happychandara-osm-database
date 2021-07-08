from django import forms
from django.forms import fields

from .models import Session, Student

class SessionForm(forms.ModelForm):

    class Meta:
        model = Session
        fields = [
            'date',
            'duration',
            'project',
            'students',
            'year'
        ]

    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields['students'].queryset = Student.objects.all()
