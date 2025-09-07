# tangible_heart/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('testapp.urls')),  # ✅ 앱의 urls를 include
]