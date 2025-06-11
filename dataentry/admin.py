from django.contrib import admin

from .models import Project, DataLingkungan, CatatanPemeliharaan, DataTransaksi

admin.site.register(Project)
admin.site.register(DataLingkungan)
admin.site.register(CatatanPemeliharaan)
admin.site.register(DataTransaksi)