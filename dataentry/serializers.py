from rest_framework import serializers
from .models import (
    Project,
    DataLingkungan,
    CatatanPemeliharaan,
    DataTransaksi,
    Kinerja,
    AktivitasImplementasi
)

class AktivitasImplementasiSerializer(serializers.ModelSerializer):
    class Meta:
        model = AktivitasImplementasi
        exclude = ['project', 'id'] # Pastikan 'id' juga di-exclude jika tidak ingin muncul di nested

class DataLingkunganSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataLingkungan
        exclude = ['project', 'id']

class CatatanPemeliharaanSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatatanPemeliharaan
        exclude = ['project', 'id']

class DataTransaksiSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataTransaksi
        exclude = ['project', 'id']

class KinerjaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kinerja
        exclude = ['project', 'id']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        # Untuk menghilangkan 'id_project', jangan masukkan 'id_project' atau 'id' di 'fields'
        # atau gunakan 'exclude = ['id']'
        fields = ['nama_project', 'model'] # Hapus 'id_project' dari daftar
        # Atau jika Anda ingin lebih eksplisit dan memastikan 'id' tidak muncul:
        # exclude = ['id'] # Ini akan menampilkan semua field kecuali 'id'

class ProjectDetailSerializer(serializers.ModelSerializer):
    data_lingkungan = DataLingkunganSerializer(many=True, read_only=True)
    catatan_pemeliharaan = CatatanPemeliharaanSerializer(many=True, read_only=True)
    data_transaksi = DataTransaksiSerializer(many=True, read_only=True)
    kinerja = KinerjaSerializer(many=True, read_only=True)
    aktivitas_implementasi = AktivitasImplementasiSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        # Anda sudah memiliki 'exclude = ['id']' di sini, yang seharusnya sudah menghilangkan ID.
        # Jika 'id_project' masih muncul, kemungkinan ada kustomisasi lain
        # atau 'id_project' bukan ID default dari model.
        exclude = ['id_project']
        # Jika Anda masih melihat 'id_project' setelah ini, coba ganti dengan 'fields'
        # fields = [
        #     'nama_project', 'model', 'external_id', 'deskripsi',
        #     'data_lingkungan', 'catatan_pemeliharaan', 'data_transaksi',
        #     'kinerja', 'aktivitas_implementasi'
        # ]




class ProjectStatusSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['external_id', 'status','nama_project']

    def get_status(self, obj):
        # PASTIKAN MENGGUNAKAN 'catatan_pemeliharaan' DENGAN UNDERSCORE
        catatan_pemeliharaan = obj.catatan_pemeliharaan.all() # <--- PERBAIKAN DI SINI

        if catatan_pemeliharaan.exists():
            return catatan_pemeliharaan.first().status

        return None
