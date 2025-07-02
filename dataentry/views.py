from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .models import Project, DataLingkungan, CatatanPemeliharaan, Kinerja, AktivitasImplementasi
from .forms import ProjectForm, DataLingkunganForm, CatatanPemeliharaanForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from rest_framework.response import Response
import requests
import time
from django.core.files.base import ContentFile
from .models import DataTransaksi
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from rest_framework.views import APIView
import io
from rest_framework import viewsets
from .models import Project
from .serializers import (
    ProjectSerializer,
    DataLingkunganSerializer,
    CatatanPemeliharaanSerializer,
    DataTransaksiSerializer,
    KinerjaSerializer,
    AktivitasImplementasiSerializer,
    ProjectStatusSerializer,
)
from rest_framework.renderers import JSONRenderer
from rest_framework import generics
from .serializers import ProjectDetailSerializer
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required

def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error = 'Invalid username or password'
    return render(request, 'login.html', {'error': error})

@login_required
def user_profile_view(request):
    # Django secara otomatis menyediakan variabel 'user' ke template
    # jika pengguna sudah login.
    return render(request, 'user_profile.html')


def dashboard_view(request):
    # Ambil status unik
    status_list = ['on going', 'Pending', 'Done']
    status_count = {}
    for status in status_list:
        status_count[status] = CatatanPemeliharaan.objects.filter(status__iexact=status).values('project').distinct().count()
    context = {
        'status_list': status_list,
        'status_count': status_count,
    }
    return render(request, 'dashboard.html',context)


def catatanpemeliharaan(request):
    projects = Project.objects.all()
    if request.method == 'POST':
        nama_project = request.POST.get('nama_project')
        project = Project.objects.get(nama_project=nama_project)
        suggest = request.POST.get('rencana_pekerjaan')
        category = request.POST.get('category')
        status = request.POST.get('status')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        stakeholder = request.POST.get('stakeholder')
        role = request.POST.get('role')
        CatatanPemeliharaan.objects.create(
            project=project,
            suggest=suggest,
            category=category,
            status=status,
            start_date=start_date or None,
            end_date=end_date or None,
            stakeholder=stakeholder,
            role=role
        )
        return redirect('nested_catatan')  # Atau redirect ke halaman yang diinginkan
    return render(request, 'catatanpemeliharaan.html', {'projects': projects})


def simpan_project(request):
    if request.method == 'POST':
        nama_project = request.POST.get('nama_project')
        model = request.POST.get('model')
        deskripsi = request.POST.get('deskripsi')

        Project.objects.create(
            nama_project=nama_project,
            model=model,
            deskripsi=deskripsi
        )
        return redirect('/')
    return render(request, 'form_project.html')


# Project -> Data Lingkungan
def project_form_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            projek = form.save()
            # Redirect ke data_lingkungan dengan id_project (PK, integer)
            return redirect('data_lingkungan', project_id=projek.id_project)
        else:
            print(form.errors)
    else:
        form = ProjectForm()
    return render(request, 'project_form.html', {'form': form})


# Data Lingkungan -> Catatan Pemeliharaan
def view_data_lingkungan(request, project_id):
    project = get_object_or_404(Project, pk=project_id)  # ✅ PAKAI pk

    if request.method == 'POST':
        form = DataLingkunganForm(request.POST)
        if form.is_valid():
            data_lingkungan = form.save(commit=False)
            data_lingkungan.project = project
            data_lingkungan.save()
            return redirect('catatan_pemeliharaan') # ubah dari 'catatan_pemeliharaan' ke 'catatanpemeliharaan'
        else:
            print(form.errors)
    else:
        form = DataLingkunganForm()
    return render(request, 'data_lingkungan.html', {'form': form, 'project': project})


# Catatan Pemeliharaan (semua data)
def view_catatan_pemeliharaan(request,project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        suggest = request.POST.get('rencana_pekerjaan')
        category = request.POST.get('category')
        status = request.POST.get('status')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        stakeholder = request.POST.get('stakeholder')
        role = request.POST.get('role')
        CatatanPemeliharaan.objects.create(
            project=project,  # perbaikan di sini
            suggest=suggest,
            category=category,
            status=status,
            start_date=start_date or None,
            end_date=end_date or None,
            stakeholder=stakeholder,
            role=role
        )
        return redirect('sequential_datatransaksi', project_id=project.id_project)
    return render(request, 'catatanpemeliharaan.html', {'project': project})


# Tambah catatan baru untuk 1 proyek
def view_data_lingkungan(request, project_id):
    project = get_object_or_404(Project, pk=project_id)  # ✅ PAKAI pk

    if request.method == 'POST':
        form = DataLingkunganForm(request.POST)
        if form.is_valid():
            data_lingkungan = form.save(commit=False)
            data_lingkungan.project = project
            data_lingkungan.save()
            return redirect('catatanpemeliharaan', project_id=project.pk) # ubah dari 'catatan_pemeliharaan' ke 'catatanpemeliharaan'
        else:
            print(form.errors)
    else:
        form = DataLingkunganForm()
    return render(request, 'data_lingkungan.html', {'form': form, 'project': project})

def kinerja_view(request):
    projects = Project.objects.all()
    return render(request, 'kinerja.html', {'project_list': projects})


def nested_project_view(request):
    projects = Project.objects.all()
    return render(request, 'nested_project.html', {'projects': projects})


def signup_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=email).exists():
            error = "User with this email already exists."
            return render(request, 'signup.html', {'error': error})

        user = User.objects.create_user(username=name, email=email, password=password, first_name=name)
        user.save()
        return redirect('login')
    return render(request, 'signup.html')


def delete_project(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=project_id)
        project.delete()
        return redirect('nested')  # redirect ke halaman daftar project
    else:
        return redirect('nested')


def nested_project_view(request):
    # Data lokal
    projects = Project.objects.all()
    all_projects = []

    # Masukkan data lokal ke list
    for p in projects:
        all_projects.append({
            "id_project": p.id_project,  # pastikan id_project ada
            "nama_project": p.nama_project,
            "model": p.model,
            "deskripsi": p.deskripsi,
            "is_local": True,  # penanda data lokal
        })

    # Data dari API eksternal
    try:
        response = requests.get('')
        if response.status_code == 200:
            data = response.json()
            for item in data:
                all_projects.append({
                    "nama_project": item["project_detail"]["name"],
                    "model": item["model_type"],
                    "deskripsi": item["project_detail"]["description"],
                    "is_local": True,  # penanda data API
                })
    except Exception:
        pass

    return render(request, 'nested_project.html', {
        'all_projects': all_projects
    })

def datatransaksi(request):
    projects = Project.objects.all()
    if request.method == 'POST':
        nama_project = request.POST.get('nama_project')
        deskripsi_data = request.POST.get('input_data')
        input_file = request.FILES.get('upload')
        project = Project.objects.get(nama_project=nama_project)

        if input_file:
            # Buat nama file timestamp
            ext = input_file.name.split('.')[-1]
            filename = time.strftime('%Y%m%d_%H%M%S') + '.' + ext
            input_file.name = filename

        DataTransaksi.objects.create(
            project=project,
            deskripsi_data=deskripsi_data,
            input_file=input_file
        )
        return redirect('nested_datatransaksi')
    return render(request, 'datatransaksi.html', {'projects': projects})
'''
def fetch_and_save_api_projects(request):
    if request.method == 'POST':
        try:
            response = requests.get('https://arlellll.pythonanywhere.com/api-content/training-models/')
            if response.status_code == 200:
                data = response.json()
                created = 0
                updated = 0 # Tambahkan counter untuk proyek yang diperbarui

                for item in data:
                    nama_project = item["project_detail"]["name"]
                    model_name = item["model_name"] # Ganti 'model' menjadi 'model_name' agar lebih jelas
                    deskripsi = item["project_detail"]["description"]
                    external_id = item["project_detail"]["external_id"] # Ambil external_id
                    model_type = item.get("model_type", "")
                    algorithm_used = item.get("algorithm_used", "")
                    hyperparameters = item.get("hyperparameters", "")

                    # Cek apakah sudah ada di database berdasarkan nama_project atau external_id
                    # Prioritaskan external_id jika dianggap sebagai identifikasi unik utama dari API
                    project, project_created = Project.objects.update_or_create(
                        external_id=external_id, # Cari berdasarkan external_id
                        defaults={
                            'nama_project': nama_project,
                            'model': model_name, # Sesuaikan dengan nama field di model Anda
                            'deskripsi': deskripsi,
                        }
                    )

                    if project_created:
                        created += 1
                    else:
                        updated += 1

                    # Simpan ke AktivitasImplementasi
                    # Pastikan AktivitasImplementasi diimpor dengan benar
                    if not AktivitasImplementasi.objects.filter(
                        project=project,
                        model_type=model_type,
                        algorithm_used=algorithm_used,
                        hyperparameters=hyperparameters
                    ).exists():
                        AktivitasImplementasi.objects.create(
                            project=project,
                            model_type=model_type,
                            algorithm_used=algorithm_used,
                            hyperparameters=hyperparameters
                        )

                return JsonResponse({'success': True, 'created_projects': created, 'updated_projects': updated})
            else:
                return JsonResponse({'success': False, 'error': f'Gagal fetch dari API. Status: {response.status_code}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Metode tidak diizinkan'})
'''
'''
def fetch_and_save_api_projects(request):
    if request.method == 'POST':
        try:
            # === BAGIAN 1: FETCH DARI API PERTAMA (arlellll) - KODE ANDA YANG SUDAH ADA ===
            response_projects = requests.get('https://arlellll.pythonanywhere.com/api-content/training-models/')

            if response_projects.status_code != 200:
                return JsonResponse({'success': False, 'error': f'Gagal fetch dari API Projects. Status: {response_projects.status_code}'})

            data_projects = response_projects.json()
            created_projects = 0
            updated_projects = 0

            for item in data_projects:
                project, project_created = Project.objects.update_or_create(
                    external_id=item["project_detail"]["external_id"],
                    defaults={
                        'nama_project': item["project_detail"]["name"],
                        'model': item["model_name"],
                        'deskripsi': item["project_detail"]["description"],
                    }
                )

                if project_created:
                    created_projects += 1
                else:
                    updated_projects += 1

                # Simpan ke AktivitasImplementasi
                AktivitasImplementasi.objects.update_or_create(
                    project=project,
                    model_type=item.get("model_type", ""),
                    algorithm_used=item.get("algorithm_used", ""),
                    hyperparameters=item.get("hyperparameters", ""),
                    # defaults diperlukan jika ada field lain yang ingin diupdate
                    defaults={}
                )

            # === BAGIAN 2: FETCH DARI API KEDUA (michaelbriant) UNTUK CATATAN PEMELIHARAAN ===
            response_status = requests.get('https://michaelbriant.pythonanywhere.com/api/proyek/status-only/')

            notes_created = 0
            notes_updated = 0

            if response_status.status_code == 200:
                data_status = response_status.json()

                for item_status in data_status:
                    project_name = item_status.get("name")

                    try:
                        # Cari project yang sesuai di database berdasarkan nama
                        project_to_update = Project.objects.get(nama_project__iexact=project_name)

                        # Buat atau perbarui CatatanPemeliharaan
                        # Kita gunakan project dan status sebagai kunci unik agar tidak duplikat
                        note, note_created = CatatanPemeliharaan.objects.update_or_create(
                            project=project_to_update,
                            status=item_status.get("status", ""), # Jadikan status sebagai bagian dari key
                            defaults={
                                'suggest': f'Status Proyek: {item_status.get("status", "")}', # Mengisi 'suggest' dengan status
                                'stakeholder': item_status.get("supervisor", ""),
                                # 'role' dan 'category' bisa diisi default jika perlu
                                # 'role': 'Supervisor Proyek',
                            }
                        )

                        if note_created:
                            notes_created += 1
                        else:
                            notes_updated += 1

                    except Project.DoesNotExist:
                        # Jika project dengan nama tersebut tidak ditemukan, lewati item ini
                        # Anda bisa menambahkan logging di sini jika perlu
                        print(f"Project dengan nama '{project_name}' tidak ditemukan di database.")
                        continue
            else:
                # Jika fetch API kedua gagal, tetap lanjutkan dan laporkan di response
                print(f"Gagal fetch status dari API kedua. Status: {response_status.status_code}")


            return JsonResponse({
                'success': True,
                'created_projects': created_projects,
                'updated_projects': updated_projects,
                'created_notes': notes_created,
                'updated_notes': notes_updated,
                'status_api_2_code': response_status.status_code # Memberi info status code API kedua
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Metode tidak diizinkan'})
'''
def fetch_and_save_api_projects(request):
    if request.method == 'POST':
        try:
            # === BAGIAN 1: FETCH DARI API PROYEK (Sudah Benar) ===
            response_projects = requests.get('https://arlellll.pythonanywhere.com/api-content/training-models/')
            if response_projects.status_code != 200:
                return JsonResponse({'success': False, 'error': f'Gagal fetch dari API Projects. Status: {response_projects.status_code}'})

            data_projects = response_projects.json()
            created_projects = 0
            updated_projects = 0

            for item in data_projects:
                project, project_created = Project.objects.update_or_create(
                    external_id=item["project_detail"]["external_id"],
                    defaults={
                        'nama_project': item["project_detail"]["name"],
                        'model': item["model_name"],
                        'deskripsi': item["project_detail"]["description"],
                    }
                )

                if project_created:
                    created_projects += 1
                else:
                    updated_projects += 1

                AktivitasImplementasi.objects.update_or_create(
                    project=project,
                    model_type=item.get("model_type", ""),
                    algorithm_used=item.get("algorithm_used", ""),
                    hyperparameters=item.get("hyperparameters", ""),
                    defaults={}
                )

            # === BAGIAN 2: FETCH DARI API STATUS (INI YANG DIPERBAIKI) ===
            response_status = requests.get('https://michaelbriant.pythonanywhere.com/api/proyek/status-only/')
            notes_created = 0
            notes_updated = 0

            if response_status.status_code == 200:
                data_status = response_status.json()

                for item_status in data_status:
                    # <-- PERBAIKAN 1: Gunakan 'nama_proyek' bukan 'name'
                    project_name = item_status.get("nama_proyek")
                    # <-- PERBAIKAN 2: Gunakan 'status_proyek' bukan 'status'
                    status = item_status.get("status_proyek", "")
                    # <-- PERBAIKAN 3: Gunakan 'supervisor_proyek' bukan 'supervisor'
                    stakeholder = item_status.get("supervisor_proyek", "")

                    if not project_name:
                        continue # Lewati jika tidak ada nama proyek

                    try:
                        project_to_update = Project.objects.get(nama_project__iexact=project_name)

                        # Buat atau perbarui CatatanPemeliharaan
                        note, note_created = CatatanPemeliharaan.objects.update_or_create(
                            project=project_to_update,
                            # Kita bisa asumsikan satu proyek hanya punya satu catatan status dari API ini
                            # Jadi kita cari berdasarkan proyek dan kategori 'Status API'
                            category='', 
                            defaults={
                                'suggest': f'{status}',
                                
                                'stakeholder': stakeholder,
                                'role': 'Supervisor' # Beri peran default
                            }
                        )

                        if note_created:
                            notes_created += 1
                        else:
                            notes_updated += 1

                    except Project.DoesNotExist:
                        print(f"Project dengan nama '{project_name}' tidak ditemukan di database lokal.")
                        continue
            else:
                print(f"Gagal fetch status dari API kedua. Status: {response_status.status_code}")

            return JsonResponse({
                'success': True,
                'created_projects': created_projects,
                'updated_projects': updated_projects,
                'created_notes': notes_created,
                'updated_notes': notes_updated,
                'status_api_2_code': response_status.status_code
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Metode tidak diizinkan'})

def nested_catatan(request):
    # Ambil semua catatan pemeliharaan
    catatan_list = CatatanPemeliharaan.objects.select_related('project').all()
    return render(request, 'nested_catatan.html', {'catatan_list': catatan_list})

def nested_lingkungan(request):
    data_lingkungan_list = DataLingkungan.objects.select_related('project').all()
    return render(request, 'nested_lingkungan.html', {'data_lingkungan_list': data_lingkungan_list})

def nested_datatransaksi(request):
    from .models import DataTransaksi
    data_transaksi_list = DataTransaksi.objects.select_related('project').all()
    return render(request, 'nested_datatransaksi.html', {'data_transaksi_list': data_transaksi_list})

def delete_catatan_pemeliharaan(request, catatan_id):
    catatan = get_object_or_404(CatatanPemeliharaan, pk=catatan_id)
    catatan.delete()
    return redirect('nested_catatan')


def edit_catatan_pemeliharaan(request, catatan_id):
    catatan = get_object_or_404(CatatanPemeliharaan, pk=catatan_id)
    if request.method == 'POST':
        catatan.suggest = request.POST.get('rencana_pekerjaan')
        catatan.category = request.POST.get('category')
        catatan.status = request.POST.get('status')
        catatan.start_date = request.POST.get('start_date') or None
        catatan.end_date = request.POST.get('end_date') or None
        catatan.stakeholder = request.POST.get('stakeholder')
        catatan.role = request.POST.get('role')
        catatan.save()
        return redirect('nested_catatan')
    return render(request, 'edit_catatanpemeliharaan.html', {'catatan': catatan})

def edit_datalingkungan(request, lingkungan_id):
    lingkungan = get_object_or_404(DataLingkungan, pk=lingkungan_id)
    if request.method == 'POST':
        lingkungan.os = request.POST.get('os')
        lingkungan.cpu = request.POST.get('cpu')
        lingkungan.ram = request.POST.get('ram')
        lingkungan.database = request.POST.get('database')

        # Handle file update
        if 'input_file' in request.FILES:
            lingkungan.input_file = request.FILES['input_file']
        elif request.POST.get('clear_file'): # To clear the file if a checkbox is used
             lingkungan.input_file = None

        lingkungan.save()
        return redirect('nested_lingkungan')
    return render(request, 'edit_datalingkungan.html', {'lingkungan': lingkungan})


def delete_datalingkungan(request, lingkungan_id):
    lingkungan = get_object_or_404(DataLingkungan, pk=lingkungan_id)
    if request.method == 'POST':
        lingkungan.delete()
        return redirect('nested_lingkungan')
    return render(request, 'confirm_delete.html', {'lingkungan': lingkungan})

def delete_datatransaksi(request, transaksi_id):
    transaksi = get_object_or_404(DataTransaksi, pk=transaksi_id)
    if request.method == 'DELETE':
        transaksi.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Metode tidak diizinkan.'})


def edit_datatransaksi(request, transaksi_id):
    transaksi = get_object_or_404(DataTransaksi, pk=transaksi_id)
    if request.method == 'POST':
        transaksi.deskripsi_data = request.POST.get('input_data')
        if request.FILES.get('upload'):
            transaksi.input_file = request.FILES.get('upload')
        transaksi.save()
        return redirect('nested_datatransaksi')
    return render(request, 'edit_datatransaksi.html', {'transaksi': transaksi})


def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        project.model = request.POST.get('model')
        project.deskripsi = request.POST.get('deskripsi')
        project.save()
        return redirect('nested')
    return render(request, 'edit_project.html', {'project': project})

def delete_project(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=project_id)
        project.delete()
        return redirect('nested')  # redirect ke halaman daftar project
    else:
        return redirect('nested')


def fetch_and_save_api_kinerja(request):
    if request.method == 'POST':
        try:
            response = requests.get('https://arlellll.pythonanywhere.com/api-content/training-models/')
            if response.status_code == 200:
                data = response.json()
                created = 0
                for item in data:
                    # Ambil nama project dari API
                    nama_project = item["project_detail"]["name"]
                    # Pastikan project sudah ada di database lokal
                    project, _ = Project.objects.get_or_create(
                        nama_project=nama_project,
                        defaults={
                            "model": item.get("model_type", ""),
                            "deskripsi": item["project_detail"].get("description", "")
                        }
                    )
                    # Cek apakah sudah ada data kinerja untuk project ini
                    if not Kinerja.objects.filter(
                        project=project,
                        model_performance=item.get("model_performance", ""),

                    ).exists():
                        Kinerja.objects.create(
                            project=project,
                            model_performance=item.get("model_performance", ""),

                        )
                        created += 1
                return JsonResponse({'success': True, 'created': created})
            else:
                return JsonResponse({'success': False, 'error': 'Gagal fetch dari API'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Metode tidak diizinkan'})


def get_kinerja_by_project(request, project_id):
    try:
        kinerja = Kinerja.objects.filter(project__pk=project_id).first()
        if kinerja:
            return JsonResponse({
                'success': True,
                'model_performance': kinerja.model_performance,

            })
        else:
            return JsonResponse({'success': False, 'error': 'Data tidak ditemukan'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def nested_aktivitas(request):
    aktivitas_list = AktivitasImplementasi.objects.select_related('project').all()
    return render(request, 'nested_aktivitas.html', {'aktivitas_list': aktivitas_list})


def download(request):
    projects = Project.objects.all()
    return render(request, 'download.html', {'projects': projects})

def download_pdf(request, project_name):
    # Gunakan prefetch_related untuk mengambil semua data terkait dalam satu query besar
    # Ini jauh lebih efisien daripada query satu per satu
    try:
        project = Project.objects.prefetch_related(
            'data_lingkungan',
            'catatan_pemeliharaan',
            'data_transaksi',
            'kinerja',
            'aktivitas_implementasi'
        ).get(nama_project=project_name)
    except Project.DoesNotExist:
        return HttpResponse("Project tidak ditemukan.", status=404)

    # Siapkan context dengan semua data yang sudah diambil
    context = {
        'project': project,
        'data_lingkungan_list': project.data_lingkungan.all(),
        'catatan_pemeliharaan_list': project.catatan_pemeliharaan.all(),
        'data_transaksi_list': project.data_transaksi.all(),
        'kinerja_list': project.kinerja.all(),
        'aktivitas_list': project.aktivitas_implementasi.all(),
    }

    # Render HTML untuk PDF menggunakan context yang sudah lengkap
    html = render_to_string('pdf_template.html', context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Laporan - {project.nama_project}.pdf"'

    pisa_status = pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=response)

    if pisa_status.err:
        return HttpResponse('Terjadi error saat membuat PDF', status=500)

    return response



def add_catatanpemeliharaan(request):
    projects = Project.objects.all()
    if request.method == 'POST':
        nama_project = request.POST.get('nama_project')
        project = Project.objects.get(nama_project=nama_project)
        suggest = request.POST.get('rencana_pekerjaan')
        category = request.POST.get('category')
        status = request.POST.get('status')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        stakeholder = request.POST.get('stakeholder')
        role = request.POST.get('role')
        CatatanPemeliharaan.objects.create(
            project=project,
            suggest=suggest,
            category=category,
            status=status,
            start_date=start_date or None,
            end_date=end_date or None,
            stakeholder=stakeholder,
            role=role
        )
        return redirect('nested_catatan')
    return render(request, 'add_catatanpemeliharaan.html', {'projects': projects})

def add_datalingkungan(request):
    projects = Project.objects.all()

    if request.method == 'POST':
        nama_project = request.POST.get('nama_project')
        project = Project.objects.get(nama_project=nama_project)

        os = request.POST.get('os')
        cpu = request.POST.get('cpu')
        ram = request.POST.get('ram')
        database = request.POST.get('database')
        input_file = request.FILES.get('input_file') # Get the uploaded file

        DataLingkungan.objects.create(
            project=project,
            os=os,
            cpu=cpu,
            ram=ram,
            database=database,
            input_file=input_file
        )

        return redirect('nested_lingkungan')

    return render(request, 'add_datalingkungan.html', {'projects': projects})

def sequential_datatransaksi_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        deskripsi_data = request.POST.get('deskripsi_data')
        input_file = request.FILES.get('input_file')

        DataTransaksi.objects.create(
            project=project,
            deskripsi_data=deskripsi_data,
            input_file=input_file
        )

        # === INI BARIS YANG ANDA UBAH ===
        # Arahkan ke halaman daftar semua transaksi.
        # Pastikan nama URL untuk nested_transaksi.html Anda adalah 'nested_transaksi'.
        return redirect('nested_datatransaksi' )

    # Bagian ini untuk menampilkan halaman form (tidak perlu diubah)
    data_transaksi_list = DataTransaksi.objects.filter(project=project)
    context = {
        'project': project,
        'data_transaksi_list': data_transaksi_list,
    }
    return render(request, 'sequential_datatransaksi.html', context)

def edit_aktivitas(request, aktivitas_id):
    # Ambil objek yang akan di-edit, atau tampilkan 404 jika tidak ada
    aktivitas = get_object_or_404(AktivitasImplementasi, pk=aktivitas_id)

    # Jika form di-submit (method POST)
    if request.method == 'POST':
        # Ambil data baru dari form
        aktivitas.model_type = request.POST.get('model_type')
        aktivitas.algorithm_used = request.POST.get('algorithm_used')
        aktivitas.hyperparameters = request.POST.get('hyperparameters')

        # Simpan perubahan ke database
        aktivitas.save()

        # Arahkan kembali ke halaman daftar
        return redirect('nested_aktivitas')

    # Jika method GET, tampilkan form dengan data yang sudah ada
    context = {
        'aktivitas': aktivitas
    }
    return render(request, 'edit_aktivitas.html', context)

def delete_aktivitas(request, aktivitas_id):
    # Ambil objek yang akan dihapus
    aktivitas = get_object_or_404(AktivitasImplementasi, pk=aktivitas_id)

    # Lakukan delete hanya jika metodenya POST untuk keamanan
    if request.method == 'POST':
        aktivitas.delete()
        # Arahkan kembali ke halaman daftar
        return redirect('nested_aktivitas')

    # Jika diakses via GET, bisa arahkan kembali atau tampilkan halaman konfirmasi
    # Untuk simpelnya, kita redirect saja.
    return redirect('nested_aktivitas')

def tambah_aktivitas_implementasi(request, project_id):

    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        # Ambil data dari form
        model_type = request.POST.get('model_type')
        algorithm_used = request.POST.get('algorithm_used')
        hyperparameters = request.POST.get('hyperparameters')

        # Buat objek baru di database
        AktivitasImplementasi.objects.create(
            project=project,
            model_type=model_type,
            algorithm_used=algorithm_used,
            hyperparameters=hyperparameters
        )

        # Karena ini langkah terakhir, arahkan ke halaman daftar project
        return redirect('nested') # Ganti jika nama URL daftar project Anda berbeda

    # Jika bukan POST, tampilkan halaman dengan daftar aktivitas yang sudah ada
    aktivitas_list = AktivitasImplementasi.objects.filter(project=project)
    context = {
        'project': project,
        'aktivitas_list': aktivitas_list,
    }
    return render(request, 'aktivitas_implementasi.html', context)



class ProjectViewSet(viewsets.ModelViewSet):
    renderer_classes = [JSONRenderer]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class DataLingkunganViewSet(viewsets.ModelViewSet):
    queryset = DataLingkungan.objects.all()
    serializer_class = DataLingkunganSerializer

class CatatanPemeliharaanViewSet(viewsets.ModelViewSet):
    queryset = CatatanPemeliharaan.objects.all()
    serializer_class = CatatanPemeliharaanSerializer

class DataTransaksiViewSet(viewsets.ModelViewSet):
    queryset = DataTransaksi.objects.all()
    serializer_class = DataTransaksiSerializer

class KinerjaViewSet(viewsets.ModelViewSet):
    queryset = Kinerja.objects.all()
    serializer_class = KinerjaSerializer

class AktivitasImplementasiViewSet(viewsets.ModelViewSet):
    queryset = AktivitasImplementasi.objects.all()
    serializer_class = AktivitasImplementasiSerializer


class ProjectListNestedAPIView(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectDetailSerializer



class ProjectStatusAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Ambil semua proyek atau filter sesuai kebutuhan
        projects = Project.objects.all()
        serializer = ProjectStatusSerializer(projects, many=True)
        return Response(serializer.data)