from rest_framework import serializers
from .models import (
    Project,
    DataLingkungan,
    CatatanPemeliharaan,
    DataTransaksi,
    Kinerja,
    AktivitasImplementasi
)

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        # Pilih field sederhana untuk ditampilkan di daftar
        fields = ['id_project', 'nama_project', 'model']

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

class AktivitasImplementasiSerializer(serializers.ModelSerializer):
    class Meta:
        model = AktivitasImplementasi
        exclude = ['project', 'id']


class ProjectDetailSerializer(serializers.ModelSerializer):
    data_lingkungan = DataLingkunganSerializer(many=True, read_only=True)
    catatan_pemeliharaan = CatatanPemeliharaanSerializer(many=True, read_only=True)
    data_transaksi = DataTransaksiSerializer(many=True, read_only=True)
    kinerja = KinerjaSerializer(many=True, read_only=True)
    aktivitas_implementasi = AktivitasImplementasiSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = '__all__'