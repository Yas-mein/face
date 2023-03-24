
from django.contrib import admin
from django.urls import path
from facerecognition import views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('r/', views.face_recognition_api),
    path('r/c/', views.capture_and_save_image),

]
