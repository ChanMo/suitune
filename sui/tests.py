from django.test import TestCase
from django.test.utils import override_settings
from django.core.files.temp import NamedTemporaryFile
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from sui.models import Track
from sui.management.commands.watch_music import MusicEventHandler


class MusicEventHandlerTestCase(TestCase):
    """测试音频文件处理器"""
    
    def setUp(self):
        """测试设置"""
        self.handler = MusicEventHandler()
        self.test_file_path = "/test/music/test_file.wav"
        
    def test_supported_formats(self):
        """测试支持的音频格式"""
        expected_formats = {'.mp3', '.flac', '.ogg', '.m4a', '.mp4', '.wav', '.opus', '.aac'}
        actual_formats = set(self.handler.supported_extensions)
        
        self.assertEqual(actual_formats, expected_formats)
        self.assertIn('.wav', self.handler.supported_extensions)
        self.assertIn('.opus', self.handler.supported_extensions)
        self.assertIn('.aac', self.handler.supported_extensions)

    def test_get_metadata_field_success(self):
        """测试成功获取元数据字段"""
        # 创建模拟音频对象
        mock_audio = Mock()
        mock_audio.get.return_value = ['Test Title']
        
        result = self.handler._get_metadata_field(mock_audio, 'title', 'default')
        self.assertEqual(result, 'Test Title')
        
    def test_get_metadata_field_fallback(self):
        """测试元数据获取失败时的回退机制"""
        # 创建模拟音频对象 - get方法返回None
        mock_audio = Mock()
        mock_audio.get.return_value = None
        
        result = self.handler._get_metadata_field(mock_audio, 'title', 'default_title')
        self.assertEqual(result, 'default_title')
        
    def test_get_metadata_field_exception(self):
        """测试元数据获取异常时的处理"""
        # 创建模拟音频对象 - get方法抛出异常
        mock_audio = Mock()
        mock_audio.get.side_effect = Exception("Metadata read failed")
        
        result = self.handler._get_metadata_field(mock_audio, 'title', 'fallback_title')
        self.assertEqual(result, 'fallback_title')
        
    def test_extract_artwork_with_none(self):
        """测试空音频文件的封面提取"""
        result = self.handler.extract_artwork(None, self.test_file_path)
        self.assertIsNone(result)
        
    def test_extract_artwork_with_valid_audio(self):
        """测试有效音频文件的封面提取"""
        # 创建模拟MP3音频对象
        from mutagen.mp3 import MP3
        from mutagen.id3 import APIC
        
        mock_audio = Mock(spec=MP3)
        mock_audio.tags = {}
        
        # 模拟没有封面的情况
        result = self.handler.extract_artwork(mock_audio, self.test_file_path)
        self.assertIsNone(result)
        
    @patch('sui.management.commands.watch_music.MP3')
    @patch('sui.management.commands.watch_music.WAVE')
    @patch('sui.management.commands.watch_music.AAC')
    @patch('sui.management.commands.watch_music.OggOpus')
    def test_process_file_metadata_success(self, mock_opus, mock_aac, mock_wave, mock_mp3):
        """测试元数据读取成功的文件处理"""
        # 设置模拟对象
        mock_audio = Mock()
        mock_audio.info.length = 180  # 3分钟
        mock_audio.get.side_effect = lambda key, default=None: {
            'title': ['Test Song'],
            'artist': ['Test Artist'], 
            'album': ['Test Album']
        }.get(key, default)
        
        mock_mp3.return_value = mock_audio
        
        with patch('os.path.getsize', return_value=5000000):  # 5MB
            with patch('os.path.getmtime', return_value=1640995200):  # 固定时间戳
                with patch.object(self.handler, 'extract_artwork', return_value=None):
                    # 处理MP3文件
                    self.handler._process_file("/test/song.mp3")
                    
        # 验证数据库中是否创建了记录
        track = Track.objects.get(file_path="/test/song.mp3")
        self.assertEqual(track.title, "Test Song")
        self.assertEqual(track.artist, "Test Artist")
        self.assertEqual(track.album, "Test Album")
        self.assertEqual(track.duration, 180)
        
    @patch('sui.management.commands.watch_music.WAVE')
    def test_process_file_metadata_failure(self, mock_wave):
        """测试元数据读取失败时仍能处理文件"""
        # 设置模拟对象抛出异常
        mock_wave.side_effect = Exception("Cannot read WAV metadata")
        
        with patch('os.path.getsize', return_value=3000000):  # 3MB
            with patch('os.path.getmtime', return_value=1640995200):  # 固定时间戳
                # 处理WAV文件（元数据读取会失败）
                self.handler._process_file("/test/audio.wav")
                
        # 验证即使元数据读取失败，文件仍被处理
        track = Track.objects.get(file_path="/test/audio.wav")
        self.assertEqual(track.title, "audio")  # 从文件名提取
        self.assertEqual(track.artist, "Unknown Artist")
        self.assertEqual(track.album, "Unknown Album")
        self.assertEqual(track.duration, 0)  # 无法获取时长
        
    def test_channel_detection(self):
        """测试频道检测逻辑"""
        test_cases = [
            ("/music/song.mp3", "music"),
            ("/talk/相声.mp3", "talk"), 
            ("/tv/电视剧.mp4", "tv"),
            ("/ambient/rain.wav", "ambient"),
            ("/other/normal.flac", "music"),  # 默认
        ]
        
        with patch('sui.management.commands.watch_music.MP3') as mock_mp3:
            mock_audio = Mock()
            mock_audio.info.length = 120
            mock_audio.get.return_value = None
            mock_mp3.return_value = mock_audio
            
            with patch('os.path.getsize', return_value=1000000):
                with patch('os.path.getmtime', return_value=1640995200):
                    with patch.object(self.handler, 'extract_artwork', return_value=None):
                        for file_path, expected_channel in test_cases:
                            # 清理之前的测试数据
                            Track.objects.filter(file_path=file_path).delete()
                            
                            self.handler._process_file(file_path)
                            track = Track.objects.get(file_path=file_path)
                            self.assertEqual(track.channel, expected_channel,
                                           f"File {file_path} should be channel {expected_channel}")


class TrackModelTestCase(TestCase):
    """测试Track模型"""
    
    def test_track_creation(self):
        """测试Track模型创建"""
        track = Track.objects.create(
            file_path="/test/song.mp3",
            title="Test Song",
            artist="Test Artist", 
            album="Test Album",
            duration=180,
            file_size=5000000,
            channel="music"
        )
        
        self.assertEqual(track.title, "Test Song")
        self.assertEqual(track.channel, "music")
        self.assertEqual(track.play_count, 0)  # 默认值
        self.assertFalse(track.liked)  # 默认值
        self.assertFalse(track.banned)  # 默认值
        
    def test_track_str_representation(self):
        """测试Track模型的字符串表示（如果有__str__方法）"""
        track = Track.objects.create(
            file_path="/test/song.mp3",
            title="Test Song",
            artist="Test Artist",
            channel="music"
        )
        
        # 如果模型定义了__str__方法，可以测试
        # self.assertIn("Test Song", str(track))
        
    def test_channel_choices(self):
        """测试频道选择"""
        valid_channels = ['music', 'talk', 'tv', 'ambient']
        
        for channel in valid_channels:
            track = Track.objects.create(
                file_path=f"/test/{channel}.mp3",
                title=f"Test {channel}",
                channel=channel
            )
            self.assertEqual(track.channel, channel)