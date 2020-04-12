from django import forms
from .models import File



class FileUploadForm(forms.Form):
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    year = forms.CharField(label="year", max_length=20)
    value = forms.CharField(label="value", max_length=20)

    def clean_file(self):
        file = self.cleaned_data['file']
        ext = file.name.split('.')[-1].lower()
        if ext not in ["pdf"]:
            raise forms.ValidationError("Only pdf files are allowed.")
        return file


class CsvUploadForm(forms.Form):
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))


