from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .models import Project, DataLingkungan, CatatanPemeliharaan, Kinerja, AktivitasImplementasi
from .forms import ProjectForm, DataLingkunganForm, CatatanPemeliharaanForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
import requests
import time
from django.core.files.base import ContentFile
from .models import DataTransaksi
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import io

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


def dashboard_view(request):
    # Ambil status unik
    status_list = ['OnGoing', 'Pending', 'Done']
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
            return redirect('data_lingkungan', project_id=projek.nama_project)  # ✅ PAKAI id # ubah dari projek.id ke projek.nama_project karena dalem model pakai nama_project buat pk nya
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
        return redirect('nested_catatan')
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

        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        user.save()
        return redirect('login')
    return render(request, 'signup.html')


def delete_project(request, project_id):
    if request.method == 'DELETE':
        try:
            project = Project.objects.get(pk=project_id)
            project.delete()
            return JsonResponse({'success': True})
        except Project.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Project tidak ditemukan.'})
    return JsonResponse({'success': False, 'error': 'Metode tidak diizinkan.'})


def nested_project_view(request):
    # Data lokal
    projects = Project.objects.all()
    all_projects = []

    # Masukkan data lokal ke list
    for p in projects:
        all_projects.append({
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
                    "model": item["model_type"],  # samakan key dengan lokal
                    "deskripsi": item["project_detail"]["description"],
                    "is_local": False,  # penanda data API
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

def fetch_and_save_api_projects(request):
    if request.method == 'POST':
        try:
            response = requests.get('https://arlellll.pythonanywhere.com/api-content/training-models/')
            if response.status_code == 200:
                data = response.json()
                created = 0
                for item in data:
                    nama_project = item["project_detail"]["name"]
                    model = item["model_name"]
                    deskripsi = item["project_detail"]["description"]
                    model_type = item.get("model_type", "")
                    algorithm_used = item.get("algorithm_used", "")
                    hyperparameters = item.get("hyperparameters", "")
                    # Cek apakah sudah ada di database
                    if not Project.objects.filter(nama_project=nama_project).exists():
                        Project.objects.create(
                            nama_project=nama_project,
                            model=model,
                            deskripsi=deskripsi
                        )
                        created += 1
                    # Simpan ke AktivitasImplementasi
                    project = Project.objects.get(nama_project=nama_project)
                    from .models import AktivitasImplementasi
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
                return JsonResponse({'success': True, 'created': created})
            else:
                return JsonResponse({'success': False, 'error': 'Gagal fetch dari API'})
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
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        project.delete()
        return redirect('nested')
    return render(request, 'confirm_delete_project.html', {'project': project})


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
                        evaluation_metrics=item.get("evaluation_metrics", ""),
                        hyperparameters=item.get("hyperparameters", "")
                    ).exists():
                        Kinerja.objects.create(
                            project=project,
                            model_performance=item.get("model_performance", ""),
                            evaluation_metrics=item.get("evaluation_metrics", ""),
                            hyperparameters=item.get("hyperparameters", "")
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
                'evaluation_metrics': kinerja.evaluation_metrics,
                'hyperparameters': kinerja.hyperparameters,
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
    project = Project.objects.filter(nama_project=project_name).first()
    if not project:
        return HttpResponse("Project tidak ditemukan.", status=404)
    # Render HTML untuk PDF
    html = render_to_string('pdf_template.html', {'project': project})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{project.nama_project}.pdf"'
    pisa_status = pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=response)
    if pisa_status.err:
        return HttpResponse('Terjadi error saat membuat PDF', status=500)
    return response