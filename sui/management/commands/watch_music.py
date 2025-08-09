import time
import os
import logging
import hashlib
from PIL import Image
from io import BytesIO

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.mp4 import MP4
from mutagen.wave import WAVE
from mutagen.aac import AAC
from mutagen.id3 import APIC

from sui.models import Track

logger = logging.getLogger(__name__)

class MusicEventHandler(FileSystemEventHandler):
    def __init__(self, command=None):
        super().__init__()
        self.command = command
        self.supported_extensions = (
            '.mp3', '.flac', '.ogg', '.m4a', '.mp4',
            '.wav', '.opus', '.aac'
        )
        # 确保专辑封面目录存在
        self.artwork_dir = os.path.join(settings.MEDIA_ROOT, 'artworks')
        os.makedirs(self.artwork_dir, exist_ok=True)
    
    def extract_artwork(self, audio_file, file_path):
        """从音频文件中提取专辑封面"""
        # 如果音频文件为空，直接返回None
        if not audio_file:
            return None
            
        try:
            artwork_data = None
            
            if isinstance(audio_file, MP3):
                # MP3文件
                for tag in audio_file.tags.values():
                    if isinstance(tag, APIC):
                        artwork_data = tag.data
                        break
            elif isinstance(audio_file, FLAC):
                # FLAC文件
                if audio_file.pictures:
                    artwork_data = audio_file.pictures[0].data
            elif isinstance(audio_file, MP4):
                # M4A/MP4文件
                covr_data = audio_file.tags.get('covr')
                if covr_data:
                    artwork_data = bytes(covr_data[0])
            elif isinstance(audio_file, OggVorbis):
                # OGG文件 - 通常封面信息存储在FLAC块中
                # OggVorbis通常不直接包含图片，但有些可能有
                pass
            elif isinstance(audio_file, OggOpus):
                # Opus文件 - 类似OGG，封面信息可能存储在FLAC块中
                # 大多数Opus文件不包含内嵌封面
                pass
            elif isinstance(audio_file, WAVE):
                # WAV文件 - 标准WAV文件通常不包含内嵌封面
                # 某些WAV文件可能有ID3标签，但这种情况较少
                pass
            elif isinstance(audio_file, AAC):
                # AAC文件 - 可能包含封面，但格式复杂
                # 需要检查是否有封面数据
                pass
            
            if artwork_data:
                return self.save_artwork(artwork_data, file_path)
                
        except Exception as e:
            if self.command:
                self.command.stdout.write(
                    self.command.style.WARNING(f"Could not extract artwork: {e}")
                )
        
        return None
    
    def _get_metadata_field(self, audio_file, field_name, default_value):
        """
        从不同格式的音频文件中获取元数据字段
        处理不同格式之间的API差异
        """
        try:
            # 大多数格式支持标准的.get()方法
            if hasattr(audio_file, 'get') and audio_file.get(field_name):
                value = audio_file.get(field_name)
                if isinstance(value, list) and value:
                    return str(value[0])
                elif value:
                    return str(value)
            
            # 某些格式可能使用大写字段名
            upper_field = field_name.upper()
            if hasattr(audio_file, 'get') and audio_file.get(upper_field):
                value = audio_file.get(upper_field)
                if isinstance(value, list) and value:
                    return str(value[0])
                elif value:
                    return str(value)
            
            # WAVE格式可能没有标准元数据，尝试从文件名提取
            from mutagen.wave import WAVE
            from mutagen.aac import AAC
            
            if isinstance(audio_file, (WAVE, AAC)):
                # 这些格式可能没有丰富的元数据支持
                if field_name == 'title':
                    # 从文件名提取标题（去除扩展名）
                    import os
                    filename = getattr(audio_file, 'filename', default_value)
                    if filename:
                        return os.path.splitext(os.path.basename(filename))[0]
                    
            return default_value
            
        except Exception as e:
            if self.command:
                self.command.stdout.write(
                    self.command.style.WARNING(f"Could not get {field_name}: {e}")
                )
            return default_value
    
    def save_artwork(self, artwork_data, file_path):
        """保存专辑封面图片"""
        try:
            # 生成唯一的文件名（基于文件路径的哈希）
            file_hash = hashlib.md5(file_path.encode()).hexdigest()
            
            # 尝试确定图片格式
            try:
                img = Image.open(BytesIO(artwork_data))
                img_format = img.format.lower() if img.format else 'jpg'
            except:
                img_format = 'jpg'  # 默认使用jpg
            
            artwork_filename = f"{file_hash}.{img_format}"
            artwork_path = os.path.join(self.artwork_dir, artwork_filename)
            
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
            
            if self.command:
                self.command.stdout.write(
                    self.command.style.SUCCESS(f"Saved artwork: {artwork_filename}")
                )
            
            return f"artworks/{artwork_filename}"
            
        except Exception as e:
            if self.command:
                self.command.stdout.write(
                    self.command.style.ERROR(f"Error saving artwork: {e}")
                )
            return None

    def _process_file(self, event_path):
        if not os.path.isfile(event_path):
            return

        file_name, file_extension = os.path.splitext(event_path)
        file_extension = file_extension.lower()

        if file_extension not in self.supported_extensions:
            logger.info(f"Skipping unsupported file type: {event_path}")
            return

        try:
            audio = None
            metadata_readable = True
            
            # 尝试读取音频元数据
            try:
                if file_extension == '.mp3':
                    audio = MP3(event_path)
                elif file_extension == '.flac':
                    audio = FLAC(event_path)
                elif file_extension == '.ogg':
                    audio = OggVorbis(event_path)
                elif file_extension == '.opus':
                    audio = OggOpus(event_path)
                elif file_extension == '.m4a' or file_extension == '.mp4':
                    audio = MP4(event_path)
                elif file_extension == '.wav':
                    audio = WAVE(event_path)
                elif file_extension == '.aac':
                    audio = AAC(event_path)
            except Exception as metadata_error:
                metadata_readable = False
                if self.command:
                    self.command.stdout.write(
                        self.command.style.WARNING(
                            f"Could not read metadata for {event_path}: {metadata_error}"
                        )
                    )

            # 获取元数据，如果读取失败则使用默认值
            if audio and metadata_readable:
                title = self._get_metadata_field(audio, 'title', os.path.basename(event_path))
                artist = self._get_metadata_field(audio, 'artist', 'Unknown Artist')
                album = self._get_metadata_field(audio, 'album', 'Unknown Album')
                duration = int(audio.info.length) if audio.info and audio.info.length else 0
                artwork_path = self.extract_artwork(audio, event_path)
            else:
                # 元数据读取失败，使用文件名和默认值
                title = os.path.splitext(os.path.basename(event_path))[0]
                artist = 'Unknown Artist'
                album = 'Unknown Album'
                duration = 0
                artwork_path = None
                if self.command:
                    self.command.stdout.write(
                        self.command.style.WARNING(
                            f"Using filename as title for {event_path}"
                        )
                    )

            # Determine channel based on file path or name
            channel = 'music'  # Default channel
            file_lower = event_path.lower()
            if 'talk' in file_lower or '相声' in file_lower:
                channel = 'talk'
            elif 'tv' in file_lower or '电视' in file_lower:
                channel = 'tv'
            elif 'ambient' in file_lower or '环境' in file_lower:
                channel = 'ambient'
            
            # 创建或更新数据库记录（即使元数据读取失败也要处理）
            music, created = Track.objects.update_or_create(
                file_path=event_path,
                defaults={
                    'title': title,
                    'artist': artist,
                    'album': album,
                    'duration': duration,
                    'file_size': os.path.getsize(event_path),
                    'last_modified': os.path.getmtime(event_path),
                    'channel': channel,
                    'artwork_path': artwork_path or '',
                }
            )
            
            if created:
                status_msg = " (metadata unavailable)" if not metadata_readable else ""
                message = f"Added new music: {music.title} - {music.artist}{status_msg}"
                logger.info(message)
                if self.command:
                    self.command.stdout.write(self.command.style.SUCCESS(message))
            else:
                status_msg = " (metadata unavailable)" if not metadata_readable else ""
                message = f"Updated existing music: {music.title} - {music.artist}{status_msg}"
                logger.info(message)
                if self.command:
                    self.command.stdout.write(self.command.style.WARNING(message))

        except Exception as e:
            message = f"Error processing file {event_path}: {e}"
            logger.error(message)
            if self.command:
                self.command.stdout.write(self.command.style.ERROR(message))

    def on_created(self, event):
        message = f"File created: {event.src_path}"
        logger.info(message)
        if self.command:
            self.command.stdout.write(self.command.style.SUCCESS(message))
        self._process_file(event.src_path)

    def on_modified(self, event):
        message = f"File modified: {event.src_path}"
        logger.info(message)
        if self.command:
            self.command.stdout.write(self.command.style.WARNING(message))
        self._process_file(event.src_path)

    def on_deleted(self, event):
        message = f"File deleted: {event.src_path}"
        logger.info(message)
        if self.command:
            self.command.stdout.write(self.command.style.ERROR(message))
        try:
            Track.objects.filter(file_path=event.src_path).delete()
            success_message = f"Removed deleted music: {event.src_path}"
            logger.info(success_message)
            if self.command:
                self.command.stdout.write(self.command.style.SUCCESS(success_message))
        except Exception as e:
            error_message = f"Error deleting music {event.src_path}: {e}"
            logger.error(error_message)
            if self.command:
                self.command.stdout.write(self.command.style.ERROR(error_message))


class Command(BaseCommand):
    help = 'Watches specified directories for music file changes and updates the database.'

    def add_arguments(self, parser):
        parser.add_argument('paths', nargs='+', type=str, help='One or more paths to watch.')
        parser.add_argument('--scan-existing', action='store_true', 
                           help='Scan existing files in directories before starting to watch.')

    def scan_existing_files(self, paths):
        """扫描现有的音频文件并添加到数据库"""
        self.stdout.write(self.style.SUCCESS("Scanning existing files..."))
        event_handler = MusicEventHandler(command=self)
        
        total_files = 0
        for path in paths:
            self.stdout.write(f"Scanning directory: {path}")
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if any(file.lower().endswith(ext) for ext in event_handler.supported_extensions):
                        event_handler._process_file(file_path)
                        total_files += 1
        
        self.stdout.write(self.style.SUCCESS(f"Scanned {total_files} audio files."))

    def handle(self, *args, **options):
        paths = options['paths']
        scan_existing = options['scan_existing']

        if not paths:
            raise CommandError('Please provide at least one path to watch.')

        event_handler = MusicEventHandler(command=self)
        observer = Observer()
        
        valid_paths = []
        for path in paths:
            if not os.path.isdir(path):
                self.stdout.write(self.style.WARNING(f"Warning: Path '{path}' is not a valid directory. Skipping."))
                continue
            self.stdout.write(self.style.SUCCESS(f"Watching directory: {path}"))
            observer.schedule(event_handler, path, recursive=True)
            valid_paths.append(path)

        if not valid_paths:
            raise CommandError('No valid directories to watch were provided.')

        if scan_existing:
            self.scan_existing_files(valid_paths)

        observer.start()
        self.stdout.write(self.style.SUCCESS("Music file watcher started. Press Ctrl+C to stop."))
        self.stdout.write(self.style.SUCCESS("Try creating, modifying, or deleting music files to test the watcher..."))

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
        self.stdout.write(self.style.SUCCESS("Music file watcher stopped."))
