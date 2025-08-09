from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Track
from .serializers import TrackSerializer
import json


def welcome(request):
    """欢迎页面 - 未认证用户的着陆页"""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, "sui/welcome.html")


@login_required
def home(request):
    return render(request, "sui/index.html")


@login_required
def favorites(request):
    return render(request, "sui/favorites.html")


@login_required
def profile(request):
    return render(request, "sui/profile.html")


class NextTrackView(APIView):
    permission_classes = [IsAuthenticated]
    
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
    permission_classes = [IsAuthenticated]
    
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
    permission_classes = [IsAuthenticated]
    
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
@login_required
def spa_page_api(request, page):
    """SPA页面内容API"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            if page == 'home':
                return spa_home_page(request)
            elif page == 'favorites':
                return spa_favorites_page(request)
            elif page == 'profile':
                return spa_profile_page(request)
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
        elif page == 'profile':
            return profile(request)
        else:
            return JsonResponse({'error': 'Page not found'}, status=404)


@login_required
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
        'script': '''
            // 等待globalMusicManager初始化完成后再初始化SuiTune应用
            function initializeHomeAfterMusicManager() {
                if (window.globalMusicManager) {
                    // 重新初始化SuiTune应用
                    if (window.suiTuneApp) {
                        window.suiTuneApp.currentPage = window.suiTuneApp.getCurrentPageType();
                        window.suiTuneApp.updateGlobalMusicManager();
                        window.suiTuneApp.initializePageFeatures();
                    } else {
                        window.suiTuneApp = new SuiTuneApp();
                        window.suiTuneApp.updateGlobalMusicManager();
                    }
                    
                    // 如果当前没有音轨，尝试从localStorage恢复状态
                    if (!window.globalMusicManager.getCurrentTrack()) {
                        window.globalMusicManager.loadState();
                    }
                    
                    // 触发首页显示更新
                    setTimeout(() => {
                        if (window.suiTuneApp && window.suiTuneApp.currentPage === 'home') {
                            window.suiTuneApp.updateHomeDisplay();
                        }
                    }, 100);
                } else {
                    // 如果globalMusicManager还没初始化，等待一下再尝试
                    setTimeout(initializeHomeAfterMusicManager, 50);
                }
            }
            
            // 开始初始化
            initializeHomeAfterMusicManager();
        ''',
        'title': 'SuiTune - 个人电台'
    })


@login_required
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
        'script': '''
            // 重新初始化SuiTune应用
            if (window.suiTuneApp) {
                window.suiTuneApp.currentPage = window.suiTuneApp.getCurrentPageType();
                window.suiTuneApp.initializePageFeatures();
            } else {
                window.suiTuneApp = new SuiTuneApp();
            }
        ''',
        'title': '我的收藏 - SuiTune'
    })


@login_required
def spa_profile_page(request):
    """个人资料页SPA内容"""
    # 直接构建个人资料页面的内容HTML，而不使用完整模板
    html_content = f'''
    <div class="max-w-4xl mx-auto space-y-8">
        <!-- 个人资料卡片 -->
        <div class="music-card backdrop-blur-xl rounded-3xl p-8 shadow-2xl border border-white/10">
            <div class="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-8">
                <!-- 头像区域 -->
                <div class="relative">
                    <div class="w-32 h-32 rounded-3xl bg-gradient-to-br from-blue-400 via-purple-500 to-pink-500 flex items-center justify-center shadow-2xl transform hover:scale-105 transition-all duration-500 relative overflow-hidden glow-effect">
                        <i class="fas fa-user text-5xl text-white/90"></i>
                        <!-- 旋转光环效果 -->
                        <div class="absolute inset-0 rounded-3xl border-2 border-white/20 animate-spin" style="animation-duration: 20s;"></div>
                    </div>
                    <!-- 状态指示器 -->
                    <div class="absolute -bottom-2 -right-2 w-8 h-8 bg-green-500 rounded-full border-4 border-gray-800 flex items-center justify-center">
                        <i class="fas fa-music text-xs text-white"></i>
                    </div>
                </div>
                
                <!-- 基本信息 -->
                <div class="flex-1 text-center md:text-left">
                    <h1 class="text-3xl font-bold mb-2 text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text">
                        {request.user.username}
                    </h1>
                    <p class="text-gray-300 text-lg mb-4">SuiTune 音乐爱好者</p>
                    <div class="flex flex-wrap justify-center md:justify-start gap-4 text-sm text-gray-400">
                        <div class="flex items-center">
                            <i class="fas fa-calendar-alt text-blue-400 mr-2"></i>
                            <span>加入时间：{request.user.date_joined.strftime('%Y年%m月%d日')}</span>
                        </div>
                        <div class="flex items-center">
                            <i class="fas fa-clock text-purple-400 mr-2"></i>
                            <span>上次活跃：{request.user.last_login.strftime('%Y-%m-%d %H:%M') if request.user.last_login else '从未'}</span>
                        </div>
                        {'<div class="flex items-center"><i class="fas fa-envelope text-pink-400 mr-2"></i><span>' + request.user.email + '</span></div>' if request.user.email else ''}
                    </div>
                </div>
                
                <!-- 操作按钮 -->
                <div class="flex flex-col space-y-3">
                    <a href="/accounts/logout/" class="px-6 py-2 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white font-medium rounded-2xl transition-all duration-300 transform hover:scale-105 text-center">
                        <i class="fas fa-sign-out-alt mr-2"></i>登出
                    </a>
                </div>
            </div>
        </div>
        
        <!-- 统计卡片网格 -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <!-- 收藏音乐统计 -->
            <div class="music-card backdrop-blur-xl rounded-3xl p-6 shadow-2xl border border-white/10 text-center">
                <div class="w-16 h-16 bg-gradient-to-br from-pink-400 to-red-400 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                    <i class="fas fa-heart text-2xl text-white"></i>
                </div>
                <h3 class="text-2xl font-bold text-white mb-1" id="favorites-count">-</h3>
                <p class="text-gray-400 text-sm">收藏音乐</p>
            </div>
            
            <!-- 总播放时长 -->
            <div class="music-card backdrop-blur-xl rounded-3xl p-6 shadow-2xl border border-white/10 text-center">
                <div class="w-16 h-16 bg-gradient-to-br from-blue-400 to-indigo-400 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                    <i class="fas fa-play text-2xl text-white"></i>
                </div>
                <h3 class="text-2xl font-bold text-white mb-1" id="total-playtime">-</h3>
                <p class="text-gray-400 text-sm">播放时长</p>
            </div>
            
            <!-- 偏好频道 -->
            <div class="music-card backdrop-blur-xl rounded-3xl p-6 shadow-2xl border border-white/10 text-center">
                <div class="w-16 h-16 bg-gradient-to-br from-purple-400 to-pink-400 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                    <i class="fas fa-music text-2xl text-white"></i>
                </div>
                <h3 class="text-lg font-bold text-white mb-1" id="favorite-channel">音乐</h3>
                <p class="text-gray-400 text-sm">偏好频道</p>
            </div>
            
            <!-- 在线状态 -->
            <div class="music-card backdrop-blur-xl rounded-3xl p-6 shadow-2xl border border-white/10 text-center">
                <div class="w-16 h-16 bg-gradient-to-br from-green-400 to-emerald-400 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                    <i class="fas fa-circle text-2xl text-white"></i>
                </div>
                <h3 class="text-lg font-bold text-green-400 mb-1">在线</h3>
                <p class="text-gray-400 text-sm">当前状态</p>
            </div>
        </div>
        
        <!-- 偏好设置卡片 -->
        <div class="music-card backdrop-blur-xl rounded-3xl p-8 shadow-2xl border border-white/10">
            <h2 class="text-2xl font-bold mb-6 text-transparent bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text">
                <i class="fas fa-sliders-h mr-3 text-purple-400"></i>播放偏好
            </h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <!-- 频道偏好 -->
                <div class="space-y-4">
                    <h3 class="text-lg font-semibold text-white mb-4">频道偏好</h3>
                    <div class="space-y-3">
                        <div class="flex items-center justify-between p-4 bg-white/5 rounded-2xl">
                            <div class="flex items-center">
                                <i class="fas fa-music text-purple-400 mr-3"></i>
                                <span class="text-white">音乐</span>
                            </div>
                            <div class="text-purple-400 font-semibold">90%</div>
                        </div>
                        <div class="flex items-center justify-between p-4 bg-white/5 rounded-2xl">
                            <div class="flex items-center">
                                <i class="fas fa-microphone text-orange-400 mr-3"></i>
                                <span class="text-white">相声</span>
                            </div>
                            <div class="text-gray-400 font-semibold">5%</div>
                        </div>
                        <div class="flex items-center justify-between p-4 bg-white/5 rounded-2xl">
                            <div class="flex items-center">
                                <i class="fas fa-tv text-blue-400 mr-3"></i>
                                <span class="text-white">TV音频</span>
                            </div>
                            <div class="text-gray-400 font-semibold">3%</div>
                        </div>
                        <div class="flex items-center justify-between p-4 bg-white/5 rounded-2xl">
                            <div class="flex items-center">
                                <i class="fas fa-leaf text-green-400 mr-3"></i>
                                <span class="text-white">环境音</span>
                            </div>
                            <div class="text-gray-400 font-semibold">2%</div>
                        </div>
                    </div>
                </div>
                
                <!-- 播放习惯 -->
                <div class="space-y-4">
                    <h3 class="text-lg font-semibold text-white mb-4">播放习惯</h3>
                    <div class="space-y-3">
                        <div class="p-4 bg-white/5 rounded-2xl">
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-gray-300">平均会话时长</span>
                                <span class="text-blue-400 font-semibold">45分钟</span>
                            </div>
                            <div class="w-full bg-gray-700 rounded-full h-2">
                                <div class="bg-gradient-to-r from-blue-400 to-purple-400 h-2 rounded-full" style="width: 75%"></div>
                            </div>
                        </div>
                        <div class="p-4 bg-white/5 rounded-2xl">
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-gray-300">收藏率</span>
                                <span class="text-pink-400 font-semibold">23%</span>
                            </div>
                            <div class="w-full bg-gray-700 rounded-full h-2">
                                <div class="bg-gradient-to-r from-pink-400 to-red-400 h-2 rounded-full" style="width: 23%"></div>
                            </div>
                        </div>
                        <div class="p-4 bg-white/5 rounded-2xl">
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-gray-300">跳过率</span>
                                <span class="text-orange-400 font-semibold">12%</span>
                            </div>
                            <div class="w-full bg-gray-700 rounded-full h-2">
                                <div class="bg-gradient-to-r from-orange-400 to-red-400 h-2 rounded-full" style="width: 12%"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 最近活动卡片 -->
        <div class="music-card backdrop-blur-xl rounded-3xl p-8 shadow-2xl border border-white/10">
            <h2 class="text-2xl font-bold mb-6 text-transparent bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text">
                <i class="fas fa-history mr-3 text-purple-400"></i>最近活动
            </h2>
            
            <div class="space-y-4" id="recent-activities">
                <!-- 活动项目将由JavaScript动态加载 -->
                <div class="flex items-center justify-center py-8">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400"></div>
                    <span class="ml-3 text-gray-400">加载中...</span>
                </div>
            </div>
        </div>
    </div>
    '''
    
    # JavaScript脚本
    script = '''
    // 加载统计数据
    loadProfileStats();
    
    // 加载最近活动
    loadRecentActivities();
    
    async function loadProfileStats() {
        try {
            // 加载收藏数量
            const favoritesResponse = await fetch('/api/favorites');
            if (favoritesResponse.ok) {
                const favoritesData = await favoritesResponse.json();
                document.getElementById('favorites-count').textContent = favoritesData.count || 0;
            }
        } catch (error) {
            console.error('Error loading profile stats:', error);
            document.getElementById('favorites-count').textContent = '0';
        }
    }
    
    function loadRecentActivities() {
        // 模拟最近活动数据（实际项目中应该从API获取）
        const activities = [
            {
                type: 'favorite',
                action: '收藏了音乐',
                track: '《夜的钢琴曲五》',
                time: '2分钟前',
                icon: 'fas fa-heart',
                color: 'text-pink-400'
            },
            {
                type: 'play',
                action: '播放了音乐',
                track: '《River Flows In You》',
                time: '15分钟前',
                icon: 'fas fa-play',
                color: 'text-blue-400'
            },
            {
                type: 'skip',
                action: '跳过了音乐',
                track: '《Untitled》',
                time: '23分钟前',
                icon: 'fas fa-step-forward',
                color: 'text-orange-400'
            },
            {
                type: 'channel',
                action: '切换到相声频道',
                track: '',
                time: '1小时前',
                icon: 'fas fa-microphone',
                color: 'text-purple-400'
            },
            {
                type: 'login',
                action: '登录到电台',
                track: '',
                time: '2小时前',
                icon: 'fas fa-sign-in-alt',
                color: 'text-green-400'
            }
        ];
        
        const container = document.getElementById('recent-activities');
        container.innerHTML = '';
        
        activities.forEach(activity => {
            const activityHtml = `
                <div class="flex items-center space-x-4 p-4 bg-white/5 rounded-2xl hover:bg-white/10 transition-all duration-200">
                    <div class="w-10 h-10 bg-gradient-to-br from-gray-600 to-gray-700 rounded-xl flex items-center justify-center">
                        <i class="${activity.icon} ${activity.color}"></i>
                    </div>
                    <div class="flex-1">
                        <p class="text-white font-medium">
                            ${activity.action}${activity.track ? ` ${activity.track}` : ''}
                        </p>
                        <p class="text-gray-400 text-sm">${activity.time}</p>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', activityHtml);
        });
    }
    
    // 添加入场动画
    const cards = document.querySelectorAll('.music-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s cubic-bezier(0.22, 1, 0.36, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
    '''
    
    return JsonResponse({
        'html': html_content,
        'script': script,  # 包含必要的JavaScript
        'title': '个人资料 - SuiTune'
    })
