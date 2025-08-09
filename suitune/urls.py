from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, Http404
from django.views.static import serve
import os
from sui.views import home, favorites, spa_page_api

def stream_audio(request, file_path):
    """开发环境下的音频文件流媒体服务"""
    full_path = '/' + file_path  # 重建完整路径
    if not os.path.exists(full_path):
        raise Http404("Audio file not found")
    return serve(request, file_path, document_root='/')

urlpatterns = [
    path('', home, name='home'),
    path('favorites/', favorites, name='favorites'),
    path('admin/', admin.site.urls),
    path('api/', include('sui.urls')),
    path('api/page/<str:page>', spa_page_api, name='spa-page-api'),
    path('accounts/', include('allauth.urls')),
    path('sui_stream/<path:file_path>', stream_audio, name='stream-audio'),
]

# 开发环境下服务媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
