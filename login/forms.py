from django import forms
from .models import HistoryUpload

class HistoryUploadForm(forms.ModelForm):
    class Meta:
        model = HistoryUpload
        fields = ('user_id', 'document', )
        #  widgets = { 'user_id': forms.HiddenInput() }
