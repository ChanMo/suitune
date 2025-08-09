from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Track, Playback


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'artist', 'album', 'channel', 'duration_display', 
        'file_size_display', 'play_count', 'liked', 'banned', 
        'artwork_preview', 'added_at'
    ]
    list_filter = [
        'channel', 'liked', 'banned', 'added_at', 'last_played_at'
    ]
    search_fields = ['title', 'artist', 'album', 'file_path']
    ordering = ['-added_at']
    readonly_fields = [
        'file_path', 'file_size', 'last_modified', 'added_at', 
        'updated_at', 'play_count', 'last_played_at', 'artwork_preview'
    ]
    list_per_page = 50
    list_select_related = []
    
    fieldsets = (
        ('音频信息', {
            'fields': ('title', 'artist', 'album', 'duration', 'channel')
        }),
        ('文件信息', {
            'fields': ('file_path', 'file_size', 'last_modified'),
            'classes': ('collapse',)
        }),
        ('专辑封面', {
            'fields': ('artwork_path', 'artwork_preview'),
            'classes': ('collapse',)
        }),
        ('播放统计', {
            'fields': ('play_count', 'last_played_at'),
            'classes': ('collapse',)
        }),
        ('用户反馈', {
            'fields': ('liked', 'banned')
        }),
        ('时间戳', {
            'fields': ('added_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_liked', 'mark_as_banned', 'mark_as_unbanned']
    
    def duration_display(self, obj):
        """格式化显示时长"""
        if obj.duration:
            minutes = obj.duration // 60
            seconds = obj.duration % 60
            return f"{minutes:02d}:{seconds:02d}"
        return "未知"
    duration_display.short_description = "时长"
    
    def file_size_display(self, obj):
        """格式化显示文件大小"""
        if obj.file_size:
            if obj.file_size > 1024 * 1024:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
            elif obj.file_size > 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size} B"
        return "未知"
    file_size_display.short_description = "文件大小"
    
    def artwork_preview(self, obj):
        """显示专辑封面预览"""
        if obj.artwork_path:
            return format_html(
                '<img src="/media/{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;">',
                obj.artwork_path
            )
        return "无封面"
    artwork_preview.short_description = "专辑封面"
    
    def mark_as_liked(self, request, queryset):
        """标记为喜欢"""
        count = queryset.update(liked=True)
        self.message_user(request, f"已将 {count} 首音频标记为喜欢")
    mark_as_liked.short_description = "标记为喜欢"
    
    def mark_as_banned(self, request, queryset):
        """标记为禁播"""
        count = queryset.update(banned=True)
        self.message_user(request, f"已将 {count} 首音频标记为禁播")
    mark_as_banned.short_description = "标记为禁播"
    
    def mark_as_unbanned(self, request, queryset):
        """取消禁播"""
        count = queryset.update(banned=False)
        self.message_user(request, f"已将 {count} 首音频取消禁播")
    mark_as_unbanned.short_description = "取消禁播"


@admin.register(Playback)
class PlaybackAdmin(admin.ModelAdmin):
    list_display = [
        'track_info', 'started_at', 'duration_played', 'skipped', 
        'source_channel', 'user_agent_short'
    ]
    list_filter = [
        'skipped', 'source_channel', 'started_at'
    ]
    search_fields = ['track__title', 'track__artist', 'user_agent']
    ordering = ['-started_at']
    readonly_fields = [
        'track', 'started_at', 'finished_at', 'skipped', 
        'source_channel', 'user_agent'
    ]
    list_per_page = 100
    list_select_related = ['track']
    
    fieldsets = (
        ('播放信息', {
            'fields': ('track', 'started_at', 'finished_at', 'skipped')
        }),
        ('来源信息', {
            'fields': ('source_channel', 'user_agent')
        })
    )
    
    def track_info(self, obj):
        """显示音频信息链接"""
        if obj.track:
            url = reverse('admin:sui_track_change', args=[obj.track.id])
            return format_html(
                '<a href="{}">{} - {}</a>',
                url,
                obj.track.title,
                obj.track.artist or "Unknown Artist"
            )
        return "未知音频"
    track_info.short_description = "音频"
    
    def duration_played(self, obj):
        """计算播放时长"""
        if obj.finished_at and obj.started_at:
            duration = obj.finished_at - obj.started_at
            total_seconds = int(duration.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes:02d}:{seconds:02d}"
        elif obj.skipped:
            return "跳过"
        else:
            return "进行中"
    duration_played.short_description = "播放时长"
    
    def user_agent_short(self, obj):
        """简化显示用户代理"""
        if obj.user_agent:
            if len(obj.user_agent) > 50:
                return obj.user_agent[:50] + "..."
            return obj.user_agent
        return "未知"
    user_agent_short.short_description = "用户代理"


# 自定义admin站点标题
admin.site.site_header = "SuiTune 音频管理"
admin.site.site_title = "SuiTune Admin"
admin.site.index_title = "音频内容管理"
