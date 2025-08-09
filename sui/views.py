from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Track
from .serializers import TrackSerializer
import json


def home(request):
    return render(request, "sui/index.html")


def favorites(request):
    return render(request, "sui/favorites.html")


class NextTrackView(APIView):
    def get(self, request):
        channel = request.GET.get('channel', 'music')
        
        # Filter by channel if specified
        queryset = Track.objects.filter(channel=channel, banned=False)
        
        # Simple random selection for now
        track = queryset.order_by('?').first()
        
        if not track:
            return Response({'detail': f'no tracks available for channel: {channel}'}, status=status.HTTP_404_NOT_FOUND)
        
        data = TrackSerializer(track).data
        data['stream_url'] = f"/sui_stream{track.file_path}"
        # 添加封面URL
        if track.artwork_path:
            data['artwork_url'] = f"/media/{track.artwork_path}"
        else:
            data['artwork_url'] = None
        return Response(data)


class FeedbackView(APIView):
    def post(self, request):
        try:
            track_id = request.data.get('track_id')
            action = request.data.get('action')
            
            if not track_id or not action:
                return Response({'error': 'track_id and action are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                track = Track.objects.get(id=track_id)
            except Track.DoesNotExist:
                return Response({'error': 'Track not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if action == 'like':
                track.liked = True
                track.save()
                return Response({'status': 'liked', 'liked': True})
            
            elif action == 'unlike':
                track.liked = False
                track.save()
                return Response({'status': 'unliked', 'liked': False})
            
            elif action == 'ban':
                track.banned = True
                track.save()
                return Response({'status': 'banned'})
            
            else:
                return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FavoritesListView(APIView):
    def get(self, request):
        try:
            # Get all liked tracks
            favorites = Track.objects.filter(liked=True, banned=False).order_by('-updated_at')
            
            # Serialize the data
            serialized_data = []
            for track in favorites:
                data = TrackSerializer(track).data
                data['stream_url'] = f"/sui_stream{track.file_path}"
                # 添加封面URL
                if track.artwork_path:
                    data['artwork_url'] = f"/media/{track.artwork_path}"
                else:
                    data['artwork_url'] = None
                serialized_data.append(data)
            
            return Response({
                'count': len(serialized_data),
                'favorites': serialized_data
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# SPA Page API Views
def spa_page_api(request, page):
    """SPA页面内容API"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            if page == 'home':
                return spa_home_page(request)
            elif page == 'favorites':
                return spa_favorites_page(request)
            else:
                return JsonResponse({'error': 'Page not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        # 非AJAX请求，重定向到正常页面
        if page == 'home':
            return home(request)
        elif page == 'favorites':
            return favorites(request)
        else:
            return JsonResponse({'error': 'Page not found'}, status=404)


def spa_home_page(request):
    """首页SPA内容"""
    # 渲染首页内容（使用组件化模板）
    html_content = render_to_string('sui/components/music_card.html', {}, request)
    
    # 包装在页面容器中
    wrapped_content = f'''
    <div class="flex flex-col items-center justify-center min-h-[80vh] max-w-sm mx-auto px-4" data-page="home">
        {html_content}
    </div>
    '''
    
    return JsonResponse({
        'html': wrapped_content,
        'script': '',  # 不需要额外脚本，统一JavaScript已处理
        'title': 'SuiTune - 个人电台'
    })


def spa_favorites_page(request):
    """收藏页SPA内容"""
    # 渲染收藏页内容（使用新模板）
    context = {
        'page_title': '我的收藏',
        'icon_class': 'fas fa-heart',
        'icon_color': 'text-pink-400',
        'page_subtitle': '正在加载你喜欢的音乐...'
    }
    
    # 渲染页面头部
    header_content = render_to_string('sui/components/page_header.html', context, request)
    
    # 构建完整的收藏页面内容
    html_content = f'''
    <div class="max-w-4xl mx-auto" data-page="favorites">
        {header_content}

        <!-- Loading State -->
        <div id="loading-state" class="flex justify-center items-center py-20">
            <div class="text-center">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mx-auto mb-4"></div>
                <p class="text-gray-400">正在加载收藏列表...</p>
            </div>
        </div>

        <!-- Empty State -->
        <div id="empty-state" class="hidden text-center py-20">
            <div class="bg-black/30 backdrop-blur-xl rounded-3xl p-12 shadow-2xl border border-white/10 max-w-md mx-auto">
                <i class="fas fa-heart-broken text-6xl text-gray-500 mb-6"></i>
                <h3 class="text-2xl font-bold text-gray-300 mb-4">还没有收藏音乐</h3>
                <p class="text-gray-400 mb-6">在播放器中点击 ❤️ 按钮来收藏你喜欢的音乐</p>
                <a href="/" class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 rounded-full text-white font-medium transition-all duration-200 hover:scale-105" data-spa-link>
                    <i class="fas fa-music mr-2"></i>
                    去发现音乐
                </a>
            </div>
        </div>

        <!-- Favorites Grid -->
        <div id="favorites-grid" class="hidden">
            <!-- Playback Controls -->
            <div class="bg-black/30 backdrop-blur-xl rounded-2xl p-6 mb-8 shadow-2xl border border-white/10">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                        <button id="play-all-btn" class="flex items-center px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 rounded-full text-white font-medium transition-all duration-200 hover:scale-105" data-action="play-all">
                            <i class="fas fa-play mr-2"></i>
                            播放全部
                        </button>
                        <button id="shuffle-btn" class="flex items-center px-4 py-3 bg-white/10 hover:bg-white/20 rounded-full text-gray-300 transition-all duration-200 hover:scale-105" data-action="shuffle">
                            <i class="fas fa-random mr-2"></i>
                            随机播放
                        </button>
                    </div>
                    <div class="text-sm text-gray-400">
                        <span id="total-duration">总时长：计算中...</span>
                    </div>
                </div>
            </div>

            <!-- Track List -->
            <div class="space-y-4" id="tracks-container">
                <!-- Tracks will be dynamically added here -->
            </div>
        </div>
    </div>
    '''
    
    return JsonResponse({
        'html': html_content,
        'script': '',  # 不需要额外脚本，统一JavaScript已处理
        'title': '我的收藏 - SuiTune'
    })
