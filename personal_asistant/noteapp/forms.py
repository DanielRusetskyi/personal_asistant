from django import forms
from django.conf import settings

from .models import Note


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['description', 'doe_date', 'due_time', 'priority']
        widgets = {
            'doe_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'priority': forms.RadioSelect(),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Опишіть завдання...'
            }),
            'due_time': forms.TimeInput(),
            # 'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }
