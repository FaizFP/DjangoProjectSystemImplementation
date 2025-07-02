from django import forms
from .models import Project, DataLingkungan, CatatanPemeliharaan

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['nama_project', 'model', 'deskripsi']

class DataLingkunganForm(forms.ModelForm):
    class Meta:
        model = DataLingkungan
        # Jangan masukkan 'project' karena akan di-assign di view
        fields = ['ram', 'database', 'cpu', 'os','input_file']

class CatatanPemeliharaanForm(forms.ModelForm):
    class Meta:
        model = CatatanPemeliharaan
        # Exclude 'project' supaya tidak muncul di form
        exclude = ['project']

    # Jika tidak ada customisasi tambahan, __init__ bisa dihilangkan
