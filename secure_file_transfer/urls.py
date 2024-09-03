from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('files/', views.files, name='files'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('file-transfer/', views.file_transfer, name='file_transfer'),
    path('serve-file/<int:file_id>/', views.serve_file, name='serve_file'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
