from django import forms
from .models import HistoryUpload

class HistoryUploadForm(forms.ModelForm):
    class Meta:
        model = HistoryUpload
        fields = ('user', 'document', )
        widgets = { 'user': forms.HiddenInput() }
