下面这份是 SuiTune – 最终设计方案（v1）。不讲研发节奏，只给“能落地”的顶层设计，把决策点一次性锁死。偏见：简单 > 花哨、JS > TS（用运行时校验兜底）。

⸻

1) 产品定位 & 范围
	•	定位：个人私有“被动听”电台式音频站点；一键开播，持续播放。
	•	内容：音乐（music）、相声/脱口秀（talk）、影视音轨（tv）、环境声（ambient）。
	•	不做：全网搜索/聚合、重社交、复杂编辑/HLS（首版）。

⸻

2) 设计原则（硬约束）
	1.	不中断：任何路由切换都不卸载播放器。
	2.	单一来源：全站只存在一个 <audio> 实例，由服务层统一驱动。
	3.	轻前端：React + Vite + Tailwind v4 + Zustand（JS），运行时校验替代类型体操。
	4.	瘦后端：Django 只做 API/鉴权/签名 URL；媒体由 Nginx 直出（Range）。
	5.	私有默认：不外发数据；外部补全/上报默认关闭。

⸻

3) 架构总览（ASCII）

Browser SPA (React/Vite/Tailwind)
┌───────────────────────────────────────────────────────────┐
│ RootLayout (never unmount)                                │
│  ├─ PlayerProvider (Zustand stores)                       │
│  ├─ <audio id="sui-audio" preload="metadata" /> (single) │
│  ├─ MiniPlayer (sticky)                                   │
│  ├─ Routes: / /favorites /search /settings (content only)│
│  └─ /now -> NowPlayingModal (overlay modal route)         │
│  CrossTab: BroadcastChannel('suitune-player')             │
└───────────────────────────────────────────────────────────┘
             |  JSON (/api)
             v
Django API (apps: users, library, radio, playback, api)
             |  X-Accel-Redirect (signed)
             v
Nginx (/sui_stream/<relpath> -> /srv/media/* , Accept-Ranges: bytes)


⸻

4) 单仓（monorepo）目录

suitune/
├─ README.md  .env.example  .editorconfig  .pre-commit-config.yaml
├─ backend/            # Django
├─ frontend/           # React + Vite + Tailwind v4 (JavaScript)
├─ shared/             # schemas/assets/docs（前后端共用）
├─ ops/                # nginx/docker/compose/k8s
├─ scripts/            # dev/build/ops 脚本
└─ .github/workflows/  # CI

后端（Django）

backend/
├─ manage.py
├─ suitune/settings/{base.py,dev.py,prod.py}
├─ suitune/{urls.py,asgi.py,wsgi.py}
├─ apps/
│  ├─ core/        # 通用 utils/middleware/selectors
│  ├─ users/       # 登录/鉴权，/api/me
│  ├─ library/     # Track/Artist/Album/Artwork + 扫描/封面
│  ├─ radio/       # 打分/采样服务，/api/next
│  ├─ playback/    # 签名/日志/反馈，/api/feedback
│  └─ api/         # DRF/路由装配
├─ config/         # logging/gunicorn
├─ tests/          # 单测：scoring/sign_url/api_next/...
└─ .env.example

前端（React + Vite + Tailwind v4，JS）

frontend/
├─ index.html  vite.config.ts  tailwind.config.ts  public/
├─ src/
│  ├─ App.js  router.js  styles/index.css
│  ├─ app/ (pages): home/ favorites/ search/ settings/ now/
│  ├─ components/ (player/common)
│  ├─ core/
│  │  ├─ store/      # playerStore.js / radioStore.js / uiStore.js
│  │  ├─ services/   # audioService.js / mediaSessionService.js
│  │  │              # crossTabService.js / radioService.js / sleepTimer.js
│  │  ├─ api/        # client.js + schemas/*.js（Zod/Ajv）
│  │  └─ types.d.ts  # 仅声明，供编辑器提示（JS 仍然是 .js）
└─ .env.example


⸻

5) 前端设计（定稿）
	•	栈：React 18、Vite、Tailwind v4、Zustand、React Router、BroadcastChannel、Media Session API。
	•	语言：JavaScript（开启 // @ts-check + JSDoc + ESLint），types.d.ts 只用于编辑器提示。
	•	播放器：
	•	<audio> 单例固定在 RootLayout。
	•	audioService 唯一入口（load/play/pause/seek/volume/fadeOut）。
	•	mediaSessionService 统一更新锁屏信息与耳机按钮处理。
	•	状态（Zustand）
	•	playerStore：current, queue, playing, position, volume, channel, sleep{stopAt}, leader{isLeader}。
	•	radioStore：近播去重、同艺人冷却、打分参数。
	•	uiStore：nowOpen、toasts。
	•	路由：/、/favorites、/search、/settings 为普通页面；/now 为 modal route（overlay）。
	•	运行时校验：所有 /api 响应与跨标签消息均用 Zod/Ajv 校验，不合规直接 fail & 上报。
	•	跨标签仲裁：BroadcastChannel 'suitune-player'，保证只有一个 Leader 播放（见 §9）。
	•	睡眠定时：基于目标时间戳；Leader 执行渐弱（30s），Follower 镜像显示。

⸻

6) 后端设计（定稿）
	•	应用边界：
	•	library：曲库模型（Track, Artist, Album, Artwork）、扫描（Mutagen）、封面处理。
	•	radio：打分/采样服务；提供 /api/next。
	•	playback：签名 URL（短时有效，HMAC+TTL）、日志、反馈 /api/feedback。
	•	users：最简鉴权（自用：Session/Cookie）；提供 /api/me。
	•	X-Accel-Redirect：视图只返回头部 X-Accel-Redirect: /sui_stream/<relpath>，由 Nginx 直出媒体（支持 Range）。
	•	表前缀：sui_。
	•	ENV（核心）：
	•	SUITUNE_MEDIA_ROOT=/srv/media
	•	SUITUNE_STREAM_PREFIX=/sui_stream/
	•	SUITUNE_SIGNING_SECRET=...
	•	DATABASE_URL=...、SUITUNE_ALLOWED_HOSTS=...

⸻

7) API 规范（首版最小集）
	•	GET /api/me → { user: {id, name}, defaultChannel, defaultSleep }
	•	GET /api/next?channel=music&seed=<id?>
→ { track: {id,title,artist,album,duration,artwork,channel}, stream_url }
	•	POST /api/feedback
请求：{ track_id, action: "like"|"ban"|"skip"|"complete" } → 200 OK
	•	GET /api/artwork/{id} → 图片

错误体（统一）：{ error: { code, message } }

⸻

8) 流媒体通路（受保护）
	•	签名 URL：/api/next 返回 stream_url（含 exp/sig），TTL（默认 10 分钟）。
	•	Nginx（要点）：
	•	/app/ → 前端静态（长 Cache）
	•	/api/ → Django
	•	/sui_stream/（internal; alias /srv/media/; add_header Accept-Ranges bytes;）

⸻

9) 跨标签协议（Leader/Follower）
	•	通道：BroadcastChannel('suitune-player')
	•	消息：
	•	who_is_leader / iam_leader{state}
	•	heartbeat{t}（1s）
	•	command{type:'play'|'pause'|'next'|'seek', payload}
	•	take_over（接管）
	•	state{state}（状态广播）
	•	规则：
	1.	新标签询问 who_is_leader；若无响应，自举为 Leader 并 iam_leader。
	2.	Follower 可发 command；Leader 执行并广播 state。
	3.	接管：发送 take_over，旧 Leader 停播并降级。
	4.	断联：Follower 超时无 heartbeat → 发起竞选。
	5.	bfcache：pageshow.persisted 时重新握手，避免“幽灵 Leader”。

⸻

10) 电台算法（v1 简版）
	1.	候选池：按频道 & 非 banned。
	2.	冷却：近播去重（N=50），同艺人冷却窗口（默认 3 首）。
	3.	打分：
	•	喜欢 +1；最近完成 +0.5；最近跳过 −0.7
	•	多样性惩罚：同艺人出现次数 × −0.2
	•	新鲜度：exp(-days_since_added/30)
	4.	采样：按分数加权随机取 1 首；保持队列长度 K=7。
	5.	探索比例：熟悉 70% / 新鲜 30%（可配置）。

⸻

11) 数据模型（核心表）
	•	sui_track(id, path, title, artist, album, duration, bitrate, channels, genre, year, channel, artwork_path, added_at, play_count, last_played_at, liked bool, banned bool)
	•	sui_playback(id, track_id, started_at, finished_at, skipped bool, source_channel)
	•	sui_artist(id, name) / sui_album(id, name, year)（可按需简化为字符串）

⸻

12) 性能与目标（SLO）
	•	TTFP（进入到首播） < 3s（已缓存封面/JSON）。
	•	路由切换掉播率 ≈ 0。
	•	双标签同时出声 ≈ 0（有监控）。
	•	控制延迟（Follower 指令 → Leader 响应） < 150ms（同机）。

⸻

13) 监控与日志
	•	前端：play/pause/next/ended/error 事件、TTFP、跨标签冲突计数、睡眠触发。
	•	后端：/api/next 耗时、签名校验失败、Nginx 4xx/5xx。
	•	错误：统一前端 Toast + 后端日志记录（可接 Sentry，非必需）。

⸻

14) 安全与隐私
	•	仅发放短时签名的 stream_url；不暴露真实路径。
	•	默认不启用外部补全/上报；如启用需显式配置与速率限制。
	•	播放日志最小化，可匿名化 UA/设备。

⸻

15) 兼容性 & 可达性
	•	首次播放需用户手势（移动端策略）。
	•	iOS 锁屏的“下一首”偶有系统接管，屏内提供等效控制。
	•	A11y：Now Playing 使用 aria-live="polite" 宣告“正在播放：歌名 — 艺术家”；控件 44px 命中区；键盘快捷键（空格/J/K/L/←/→）。

⸻

16) 配置（ENV 一览）
	•	后端（prefix: SUITUNE_）
	•	MEDIA_ROOT、STREAM_PREFIX、SIGNING_SECRET、ALLOWED_HOSTS、DATABASE_URL
	•	前端（prefix: VITE_）
	•	API_BASE=/api、APP_NAME=SuiTune、DEFAULT_CHANNEL=music

⸻

17) 风险 & 对策
	•	DOM 误卸载播放器 → <audio> 固定在根壳；路由只换内容。
	•	跨标签协议漂移 → 所有消息运行时校验 + 版本号。
	•	签名过期 → 前端自动 next() 续播 + 轻量提示；后端 TTL 合理。
	•	格式兼容 → 统一 MP3/AAC；FLAC/APE 非首选。
	•	移动端后台节流 → 定时基于目标时间戳 + timeupdate 兜底。

⸻

18) 未来扩展（不影响当前结构）
	•	PWA（安装到主屏，缓存壳与封面）。
	•	Last.fm/ListenBrainz scrobble。
	•	MusicBrainz/CAA/AcoustID 补全（限流 + 缓存）。
	•	HLS（若以后有远程/弱网需求）。

⸻

19) 验收清单（DoD v1）
	•	进入首页点“随便播”，3 秒内开播。
	•	路由在 /、/favorites、/search、/settings、/now 间切换，不断播。
	•	开两个浏览器标签，只有一个出声，另一个可遥控；接管可用。
	•	睡眠定时 30 分钟可触发 渐弱停播。
	•	/api/next 返回可播的 stream_url（短时签名），Nginx 支持 Range。
	•	“喜欢/跳过”会改变后续采样（明显体感：减少重复，提升熟悉度）。

⸻

一句话收尾：把“播放器单例 + 路由不卸载 + 跨标签只认一个 Leader”三件事做到位，SuiTune 的体验就稳如原生。其余一切，都是锦上添花。
