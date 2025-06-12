from django.db import models

class Project(models.Model):
    nama_project = models.CharField(max_length=255, primary_key=True)  # jadi PK, otomatis unik dan not null
    model = models.CharField(max_length=255)
    deskripsi = models.TextField()
    
    def __str__(self):
        return self.nama_project


class DataLingkungan(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='data_lingkungan')
    ram = models.CharField(max_length=100)
    database = models.CharField(max_length=100)
    cpu = models.CharField(max_length=100)
    os = models.CharField(max_length=100)


class CatatanPemeliharaan(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='catatan_pemeliharaan')
    suggest = models.TextField()  # Untuk "Rencana Pekerjaan"
    category = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    stakeholder = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=255, null=True, blank=True)


class DataTransaksi(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='data_transaksi')
    deskripsi_data = models.TextField()
    input_file = models.FileField(upload_to='transaksi_files/')


class Kinerja(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='kinerja')
    model_performance = models.CharField(max_length=255)
    evaluation_metrics = models.CharField(max_length=255)
    hyperparameters = models.CharField(max_length=255)

    def __str__(self):
        return f'Kinerja {self.project.nama_project}'
    
class AktivitasImplementasi(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='aktivitas_implementasi')
    model_type = models.CharField(max_length=255)
    algorithm_used = models.CharField(max_length=255)
    hyperparameters = models.CharField(max_length=255)

    def __str__(self):
        return f'Aktivitas {self.project.nama_project} - {self.model_type}'