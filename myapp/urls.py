from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('home/', views.home),
    path('splitPDF/', views.splitPDF),
    path('mergePDF/', views.mergePDF),
    path('detect_face/', views.detect_face)
]