# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

SuiTune 是一个面向"被动听"的个人电台式音频站点。主要特点：
- Django 后端负责 API 与鉴权，Nginx 直出媒体文件
- 支持音乐、相声、TV音频、环境声四个频道
- 电台式播放：一键开播，智能推荐，轻量反馈
- 私有化音频库管理
- 跨页面音乐播放：使用SPA架构保持播放连续性
- 专辑封面提取和显示：从音频文件中自动提取封面图片

## 开发环境设置

- 使用虚拟环境：`env/` 目录
- 激活环境：`source env/bin/activate` (macOS/Linux) 或 `env\Scripts\activate` (Windows)
- 安装依赖：`pip install -e .`

## 常用命令

### 开发服务器
```bash
python manage.py runserver
```

### 数据库操作
```bash
# 创建迁移文件
python manage.py makemigrations

# 应用迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

### 音频文件管理
```bash
# 监听指定目录的音频文件变化，自动添加到数据库
python manage.py watch_music /path/to/music/directory

# 从现有音频文件中提取专辑封面
python manage.py extract_artworks

# 覆盖已存在的封面文件
python manage.py extract_artworks --overwrite
```

### 测试和代码质量
由于项目处于初期开发阶段，暂无配置测试框架。建议在添加新功能时手动测试相关API端点。

## 项目架构

### 核心应用：`sui/`
- **models.py**: 核心数据模型
  - `Track`: 音频文件元数据，包含路径、标题、艺人、播放统计、专辑封面等
  - `Playback`: 播放记录，用于统计和推荐算法
- **views.py**: API视图
  - `NextTrackView`: 获取下一首推荐音频
  - `FeedbackView`: 处理用户反馈（喜欢/跳过/完成播放）
  - SPA页面API：`spa_home_page`, `spa_favorites_page`
- **management/commands/**:
  - `watch_music.py`: 文件系统监听，自动扫描音频文件并提取封面
  - `extract_artworks.py`: 从现有音频文件批量提取专辑封面

### 配置
- **pyproject.toml**: 项目依赖和基本信息
- **suitune/settings.py**: Django配置，支持环境变量
- **suitune/urls.py**: 主URL配置

### 前端架构 (现代化重构)
- **现代化SPA架构**: 使用原生Fetch API + History API，零jQuery依赖
- **组件化模板系统**: Django模板组件复用，消除代码冗余
- **统一JavaScript管理**: 单一`app.js`文件管理所有页面交互
- **全局音乐管理器**: `GlobalMusicManager`类处理音乐播放状态同步
- **Media Session集成**: 支持锁屏和系统通知控制
- **模板文件**:
  - `sui/base.html`: 基础模板，包含全局播放器和SPA路由器
  - `sui/index.html`: 首页组件化模板
  - `sui/favorites.html`: 收藏页组件化模板
  - `sui/components/`: 可复用模板组件目录
    - `music_card.html`: 音乐播放卡片组件
    - `track_list_item.html`: 歌曲列表项组件
    - `page_header.html`: 页面头部组件
  - `static/css/animations.css`: 统一动画样式
  - `static/js/app.js`: 现代化应用管理器

## 核心功能

### 频道系统
四个频道类型：`music`、`talk`、`tv`、`ambient`

### 跨页面音乐播放 (现代化实现)
- **现代SPA架构**: 使用原生Fetch API + History API实现无刷新页面切换
- **组件化设计**: Django模板组件化，零代码冗余
- **状态持久化**: LocalStorage保存播放状态，支持跨标签页同步
- **全局播放器**: 底部固定播放器，所有页面共享
- **播放连续性**: 页面切换时音乐不中断
- **统一交互**: 单一JavaScript文件管理所有页面逻辑

### 专辑封面系统
- **自动提取**: 从MP3、FLAC、M4A、MP4等格式中提取内嵌封面
- **图片优化**: 自动调整大小（最大512x512）和格式转换
- **多尺寸显示**: 支持主页面（256x256）、收藏列表（64x64）、底部播放器（48x48）
- **优雅降级**: 无封面时显示默认音乐图标

### 推荐算法
基于以下因素进行音频推荐：
- 播放历史和用户反馈
- 冷却机制防止重复播放
- 多样性平衡

### 文件格式支持
支持的音频格式：MP3、FLAC、OGG、M4A、MP4

## 数据库设计

### 表前缀：`sui_`
- `sui_track`: 音频文件信息
- `sui_playback`: 播放记录

## 环境变量

项目使用 `SUITUNE_` 前缀的环境变量：
- `SUITUNE_SECRET_KEY`: Django密钥
- `SUITUNE_DEBUG`: 调试模式开关
- `SUITUNE_MEDIA_ROOT`: 媒体文件根目录

## API端点

### 核心API（`/api/`）
- `GET /api/next?channel=music`: 获取下一首推荐音频（包含专辑封面URL）
- `POST /api/feedback`: 提交用户反馈
- `GET /api/favorites`: 获取收藏列表
- `GET /api/page/home`: SPA首页内容
- `GET /api/page/favorites`: SPA收藏页面内容

### 媒体资源
- `/media/artworks/<filename>`: 专辑封面图片
- `/sui_stream/<path>`: 音频流（需认证，Nginx X-Accel-Redirect）

### 其他端点
- `/`: 首页
- `/favorites/`: 收藏页面
- `/admin/`: Django管理后台
- `/accounts/`: 用户认证（django-allauth）

## 现代化架构重构成果

### 🎯 解决的核心问题
- **代码冗余消除**: 彻底解决了服务器端渲染与SPA版本的代码重复问题
- **维护复杂度降低**: 从双套代码维护简化为单一代码源
- **技术债务清理**: 移除了传统jQuery依赖，采用现代Web标准

### 🚀 技术升级亮点
- **零第三方依赖**: 使用原生Fetch API替代jQuery AJAX
- **现代Web标准**: History API、ES6+ Class、事件委托
- **组件化设计**: Django模板组件可复用，DRY原则彻底执行
- **统一状态管理**: 单一JavaScript类管理所有页面逻辑
- **性能优化**: 更小的代码体积，更快的加载速度

### 📁 新的文件组织结构
```
sui/
├── static/
│   ├── css/
│   │   └── animations.css          # 统一动画样式
│   └── js/
│       └── app.js                  # 现代化应用管理器
├── templates/sui/
│   ├── components/                 # 可复用模板组件
│   │   ├── music_card.html         # 音乐播放卡片
│   │   ├── track_list_item.html    # 歌曲列表项  
│   │   └── page_header.html        # 页面头部
│   ├── base.html                   # 基础模板 + SPA路由器
│   ├── index.html                  # 组件化首页
│   └── favorites.html              # 组件化收藏页
```

### 🎵 用户体验提升
- **一致性保证**: 无论直接访问还是SPA导航，体验完全一致
- **SEO友好**: 保持服务器端渲染的搜索引擎优化优势
- **平滑过渡**: 页面切换带有淡入淡出动画效果
- **错误处理**: 优雅的降级机制，网络问题时自动回退

## 开发注意事项

1. **音频文件处理**：使用 `mutagen` 库处理音频元数据和专辑封面提取
2. **图片处理**：使用 `Pillow (PIL)` 库优化和转换专辑封面
3. **文件监听**：`watchdog` 库实现实时文件系统监听
4. **路径处理**：音频文件存储相对路径，便于部署迁移
5. **认证系统**：集成 django-allauth 处理用户登录
6. **现代化SPA**：使用原生Fetch API + History API，零jQuery依赖
7. **组件化开发**：使用Django模板组件，确保代码复用
8. **统一状态管理**：通过`app.js`和事件系统实现跨页面同步

## 部署相关

- 静态文件路径：`/static/suitune/`
- 媒体流路径约定：`/sui_stream/`（用于Nginx X-Accel-Redirect）
- 专辑封面路径：`/media/artworks/`
- 数据库：默认SQLite，生产环境可配置其他数据库
- 媒体文件存储：支持本地文件系统，封面图片自动优化

## 技术特性

### 现代化SPA架构
- **零依赖实现**: 使用原生Fetch API + History API，无jQuery等第三方库
- **组件化模板**: Django模板组件完全复用，彻底消除代码冗余
- **统一JavaScript管理**: 单一`app.js`类管理所有页面逻辑和状态
- **事件委托机制**: 高效的事件处理，无需重复绑定
- **优雅降级**: 网络问题时自动回退到传统页面跳转

### 跨页面播放实现
- **轻量级SPA**: 避免重型框架，使用原生Web API
- **History API**: 实现URL更新而不刷新页面
- **状态持久化**: 播放状态、进度、频道设置持久保存
- **跨标签页同步**: storage事件实现多标签页状态同步
- **平滑过渡**: 页面切换带有淡入淡出动画效果

### 专辑封面处理
- **多格式支持**: MP3 (APIC), FLAC (pictures), M4A/MP4 (covr), OGG
- **自动优化**: 尺寸调整、格式转换（统一为JPEG）、质量压缩
- **哈希命名**: 基于文件路径MD5避免重复和冲突
- **渐进增强**: 无封面时优雅降级到默认音乐图标

### Media Session集成
- **系统通知**: 锁屏显示当前播放信息
- **硬件控制**: 耳机按钮、媒体键支持
- **封面展示**: 系统通知中显示专辑封面
- **进度同步**: 播放进度与系统媒体控制同步

### 代码质量保证
- **DRY原则**: 完全消除代码重复，单一信息源
- **组件复用**: 模板组件可在任何页面使用
- **统一维护**: 修改一次即可影响所有使用场景
- **现代标准**: ES6+ 语法，原生Web API，无技术债务