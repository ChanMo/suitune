import os
import logging
import hashlib
from PIL import Image
from io import BytesIO

from django.core.management.base import BaseCommand
from django.conf import settings
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.m4a import M4A
from mutagen.mp4 import MP4
from mutagen.id3 import APIC

from sui.models import Track

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '从现有音频文件中提取专辑封面'

    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='覆盖已存在的封面文件'
        )

    def handle(self, *args, **options):
        overwrite = options['overwrite']
        
        # 确保封面目录存在
        artwork_dir = os.path.join(settings.MEDIA_ROOT, 'artworks')
        os.makedirs(artwork_dir, exist_ok=True)
        
        # 获取所有没有封面的音频文件
        if overwrite:
            tracks = Track.objects.all()
            self.stdout.write(f"处理所有 {tracks.count()} 个音频文件...")
        else:
            tracks = Track.objects.filter(artwork_path='')
            self.stdout.write(f"处理 {tracks.count()} 个没有封面的音频文件...")
        
        success_count = 0
        error_count = 0
        
        for track in tracks:
            try:
                if not os.path.exists(track.file_path):
                    self.stdout.write(
                        self.style.WARNING(f"文件不存在: {track.file_path}")
                    )
                    continue
                
                # 提取封面
                artwork_path = self.extract_artwork(track.file_path, artwork_dir)
                
                if artwork_path:
                    track.artwork_path = artwork_path
                    track.save(update_fields=['artwork_path'])
                    success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"提取成功: {track.title} - {artwork_path}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"没有封面: {track.title}")
                    )
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f"处理失败 {track.title}: {e}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"处理完成! 成功: {success_count}, 失败: {error_count}"
            )
        )

    def extract_artwork(self, file_path, artwork_dir):
        """从音频文件中提取封面"""
        try:
            # 确定文件类型
            _, file_extension = os.path.splitext(file_path)
            file_extension = file_extension.lower()
            
            audio = None
            if file_extension == '.mp3':
                audio = MP3(file_path)
            elif file_extension == '.flac':
                audio = FLAC(file_path)
            elif file_extension == '.ogg':
                audio = OggVorbis(file_path)
            elif file_extension in ['.m4a', '.mp4']:
                audio = M4A(file_path) if file_extension == '.m4a' else MP4(file_path)
            
            if not audio:
                return None
            
            # 提取封面数据
            artwork_data = None
            
            if isinstance(audio, MP3):
                # MP3文件
                if audio.tags:
                    for tag in audio.tags.values():
                        if isinstance(tag, APIC):
                            artwork_data = tag.data
                            break
            elif isinstance(audio, FLAC):
                # FLAC文件
                if audio.pictures:
                    artwork_data = audio.pictures[0].data
            elif isinstance(audio, (M4A, MP4)):
                # M4A/MP4文件
                if audio.tags:
                    covr_data = audio.tags.get('covr')
                    if covr_data:
                        artwork_data = bytes(covr_data[0])
            elif isinstance(audio, OggVorbis):
                # OGG文件通常不包含图片
                pass
            
            if artwork_data:
                return self.save_artwork(artwork_data, file_path, artwork_dir)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"提取封面失败 {file_path}: {e}")
            )
        
        return None
    
    def save_artwork(self, artwork_data, file_path, artwork_dir):
        """保存专辑封面图片"""
        try:
            # 生成唯一的文件名（基于文件路径的哈希）
            file_hash = hashlib.md5(file_path.encode()).hexdigest()
            
            # 尝试确定图片格式
            try:
                img = Image.open(BytesIO(artwork_data))
                img_format = img.format.lower() if img.format else 'jpg'
                if img_format == 'jpeg':
                    img_format = 'jpg'
            except:
                img_format = 'jpg'  # 默认使用jpg
            
            artwork_filename = f"{file_hash}.{img_format}"
            artwork_path = os.path.join(artwork_dir, artwork_filename)
            
            # 如果文件已存在，直接返回相对路径
            if os.path.exists(artwork_path):
                return f"artworks/{artwork_filename}"
            
            # 保存图片并优化
            img = Image.open(BytesIO(artwork_data))
            
            # 转换为RGB（去除alpha通道）
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 调整大小（最大512x512，保持比例）
            max_size = (512, 512)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 保存图片
            img.save(artwork_path, 'JPEG', quality=85, optimize=True)
            
            return f"artworks/{artwork_filename}"
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"保存封面失败: {e}")
            )
            return None