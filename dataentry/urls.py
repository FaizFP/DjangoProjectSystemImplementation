from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views 
from .views import (
    ProjectViewSet,
    DataLingkunganViewSet,
    CatatanPemeliharaanViewSet,
    DataTransaksiViewSet,
    KinerjaViewSet,
    AktivitasImplementasiViewSet,
)
from .views import ProjectListNestedAPIView




router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'data-lingkungan', DataLingkunganViewSet)
router.register(r'catatan-pemeliharaan', CatatanPemeliharaanViewSet)
router.register(r'data-transaksi', DataTransaksiViewSet)
router.register(r'kinerja', KinerjaViewSet)
router.register(r'aktivitas-implementasi', AktivitasImplementasiViewSet)

urlpatterns = [
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('catatanpemeliharaan/<str:project_id>/', views.view_catatan_pemeliharaan, name='catatanpemeliharaan'),
    path('simpan_project/', views.simpan_project, name='simpan_project'),
    path('project/form/', views.project_form_view, name='project_form'),
    path('datatransaksi/', views.datatransaksi, name='datatransaksi'),
    path('nested/', views.nested_project_view, name='nested'),
    path('kinerja/', views.kinerja_view, name='kinerja'),

    path('data-lingkungan/<int:project_id>/', views.view_data_lingkungan, name='data_lingkungan'), # ubah dari <int:project_id> ke <str:project_id> pakai str buat value string int buat integer / numerik
    path('projek/form/catatanpemeliharaan/<int:project_id>/', views.view_catatan_pemeliharaan, name='catatanpemeliharaan'),
    path('nested_project/', views.nested_project_view, name='nested_project'),
    path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('fetch_and_save_api_projects/', views.fetch_and_save_api_projects, name='fetch_and_save_api_projects'),
    path('nested_catatan/', views.nested_catatan, name='nested_catatan'),
    path('nested_lingkungan/', views.nested_lingkungan, name='nested_lingkungan'),
    path('nested_datatransaksi/', views.nested_datatransaksi, name='nested_datatransaksi'),
    path('catatanpemeliharaan/delete/<int:catatan_id>/', views.delete_catatan_pemeliharaan, name='delete_catatanpemeliharaan'),
    path('catatanpemeliharaan/edit/<int:catatan_id>/', views.edit_catatan_pemeliharaan, name='edit_catatanpemeliharaan'),
    path('datalingkungan/edit/<int:lingkungan_id>/', views.edit_datalingkungan, name='edit_datalingkungan'),
    path('datalingkungan/delete/<int:lingkungan_id>/', views.delete_datalingkungan, name='delete_datalingkungan'),
    path('delete_datatransaksi/<int:transaksi_id>/', views.delete_datatransaksi, name='delete_datatransaksi'),
    path('edit_datatransaksi/<int:transaksi_id>/', views.edit_datatransaksi, name='edit_datatransaksi'),
    path('edit_project/<str:project_id>/', views.edit_project, name='edit_project'),
    path('fetch_and_save_api_kinerja/', views.fetch_and_save_api_kinerja, name='fetch_and_save_api_kinerja'),
    path('get_kinerja_by_project/<str:project_id>/', views.get_kinerja_by_project, name='get_kinerja_by_project'),
    path('nested_aktivitas/', views.nested_aktivitas, name='nested_aktivitas'),
    path('download/', views.download, name='download'),
    path('download_pdf/<str:project_name>/', views.download_pdf, name='download_pdf'),
    path('add-catatanpemeliharaan/', views.add_catatanpemeliharaan, name='add_catatanpemeliharaan'),
    path('api/',include(router.urls)),
    path('api/projects-nested/', ProjectListNestedAPIView.as_view(), name='projects-nested'),
    path('add-data_lingkungan/',views.add_datalingkungan, name='add_data_lingkungan'),
    path('project/<int:project_id>/data-transaksi/', views.sequential_datatransaksi_view, name='sequential_datatransaksi'),
    path('aktivitas/edit/<int:aktivitas_id>/', views.edit_aktivitas, name='edit_aktivitas'),
    path('aktivitas/delete/<int:aktivitas_id>/', views.delete_aktivitas, name='delete_aktivitas'),
    path('project/<int:project_id>/aktivitas-implementasi/', views.tambah_aktivitas_implementasi, name='tambah_aktivitas_implementasi'),
    path('profile/', views.user_profile_view, name='user_profile'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    

]