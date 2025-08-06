SuiTune

少做决定，直接开播。
SuiTune 是一个面向“被动听”的个人电台式音频站点：只需点一下，系统就按你的喜好与习惯，持续播下去。主打本地私有曲库，轻前端、稳后端。

⸻

0) TL;DR
	•	定位：私有化、极简的“随机电台”Web 站点，覆盖音乐、相声、TV 音频、环境声等多类型音频。
	•	理念：少决策、不中断、熟悉为主 + 少量新鲜。
	•	技术取向：Django 负责 API 与鉴权，Nginx 直出媒体（X-Accel-Redirect），前端仅用 <audio> + Media Session。
	•	规模目标：200–2,000 首级别的个人曲库优先，强调稳定与维护成本低。

⸻

1) 产品定位
	•	人群：想要“开了就听”的个人/小团队；对“自己挑歌”已疲惫、偏好电台式被动播放的用户。
	•	场景：写代码/通勤/做饭/睡前。
	•	内容：
	•	音乐（Music）
	•	相声/脱口秀（Talk）
	•	影视音轨/TV 音频（TV）
	•	环境声/白噪音（Ambient）

明确取舍：不追求“全网”版权流媒体；只服务你自有/自用的音频文件。

⸻

2) 设计原则
	1.	少决策：首页只保留一个大按钮「随便播」。喜欢、跳过、切频道即可。
	2.	不中断：永远预置后备队列，播放永不“断档”。
	3.	熟悉优先：默认“熟悉 70% + 新鲜 30%”，既稳又不腻。
	4.	后端稳：Django 只负责“给出下一首”和签名 URL；媒体文件由 Nginx 直出，节省资源。
	5.	前端轻：HTML5 <audio> + Media Session；PWA 仅作外观增强。
	6.	隐私优先：本地文件、本地索引；任何联网补全/上报都默认关闭。

⸻

3) 架构一览

[ Browser / PWA ]
     |   (GET /api/next?channel=music)
     v
[ Django API ] -----> returns JSON {track, signed_stream_url, artwork}
     |                              (no file IO here)
     |  (internal redirect)
     v
[ Nginx ]  <--- X-Accel-Redirect /sui_stream/<relative_path>
     |
     v
[ Local Filesystem / Object Storage ]

	•	Django：鉴权、频道/电台出队、反馈收集（like/ban/skip）、短时签名 URL。
	•	Nginx：静态媒体直出，支持 Range，负责真正的流。
	•	前端：<audio src="signed_stream_url">，Media Session 提供锁屏信息与耳机按钮。

⸻

4) 主要功能

4.1 电台式播放（核心）
	•	一键开播：按频道（Music/Talk/TV/Ambient）随机但“懂你”。
	•	动态队列：播放中后台补齐 5–10 首，永不空播。
	•	轻反馈：喜欢（+1）、完成播放（+0.5）、跳过（−0.7），即时影响后续采样。
	•	冷却机制：近播去重、同艺人冷却、防“循环卡壳”。

4.2 多类型音频支持
	•	频道化呈现：音乐、相声、TV 音频、环境声，切换不刷新队列。
	•	环境声/睡前场景优化：渐弱停播、低交互打扰模式。

4.3 睡眠定时
	•	快捷：15/30/45/60 分钟；渐弱（fade-out）后暂停。
	•	即使页面切后台，仍以播放进度事件校准停止点。

4.4 元数据与封面
	•	初期：读取文件内嵌标签/同目录封面。
	•	可选：接入 MusicBrainz/Cover Art Archive/AcoustID 做补全（默认关闭，节流缓存）。

4.5 PWA 与锁屏体验
	•	Media Session：标题、艺人、封面、进度。
	•	PWA：添加到主屏、离线缓存页面与封面（不缓存音频）。

⸻

5) 信息架构与命名约定
	•	产品名：SuiTune
	•	短码：sui
	•	环境变量前缀：SUITUNE_（如 SUITUNE_MEDIA_ROOT）
	•	数据库表前缀：sui_（如 sui_track）
	•	Nginx 内部流路径：/sui_stream/
	•	静态资源路径：/static/suitune/
	•	频道：music | talk | tv | ambient

⸻

6) 数据模型（概要）

sui_track
- id
- path (relative)
- title, artist, album
- duration, bitrate, channels, year, genre
- channel (music|talk|tv|ambient)
- artwork_path (optional)
- mbid (optional for future)
- added_at, updated_at
- play_count, last_played_at
- liked (bool), banned (bool)

sui_playback
- id, track_id
- started_at, finished_at
- skipped (bool)
- source_channel
- device / user_agent

sui_feature (optional)
- track_id
- bpm, energy, chroma_mean, ...
- version


⸻

7) API 面（无具体实现细节）
	•	GET /api/next?channel=music&seed=<id?>
返回下一首：{ id, title, artist, duration, artwork, stream_url }
	•	POST /api/feedback
请求体：{ track_id, action: "like" | "ban" | "skip" | "complete" }
	•	GET /api/artwork/<id>
返回封面（可由 Nginx 缓存）。
	•	GET /api/me
返回当前用户与默认配置（默认频道/默认睡眠时长）。

备注：stream_url 为短时签名，后端通过 X-Accel-Redirect 指向受保护的真实文件。

⸻

8) 电台算法（简化版）
	1.	候选池：按频道过滤，剔除 banned。
	2.	冷却：排除近 N 首播放的曲目；同艺人设置冷却（避免连播）。
	3.	打分：
	•	喜欢 +1；最近完成 +0.5；最近跳过 −0.7
	•	多样性惩罚：同艺人出现次数 * −0.2
	•	新鲜度：exp(-days_since_added/30)
	4.	采样：按分数加权随机取 1 首；队列低于阈值时自动补位。
	5.	探索比例：默认“熟悉 70% + 新鲜 30%”（可配）。

态度明确：纯随机≈灾难。最少也要“近播去重 + 同艺人冷却 + 简单加权”。

⸻

9) 关键体验
	•	主页：频道标签 + 大按钮「Play」。
	•	Now Playing：大封面、进度条、上一首/下一首、喜欢/不喜欢、睡眠定时。
	•	锁屏/耳机：显示封面/标题；支持基本控制（系统兼容差异可接受）。
	•	无中断：自动补队列；错误回退到下一首。

⸻

10) 非目标（当前阶段不做）
	•	在线全网搜索/聚合与版权分发。
	•	复杂的编辑/剪辑/多端同步。
	•	重社交（评论/关注/公开广场）。
	•	“强 AI”个性化（端侧大模型/云端画像），以简单可解释为第一优先。

⸻

11) 指标与运行质量
	•	TTFP（Time To First Play）：< 3s（首页到开播）。
	•	每小时交互次数：越低越好（在留存不降的前提）。
	•	完成率/跳过率：按频道分开监控。
	•	夜间收听占比 + 定时使用率：验证“睡前场景”。
	•	错误率：流读取失败、签名过期、封面缺失等。

⸻

12) 隐私与安全
	•	默认不调用外部补全服务；如开启，需显式同意并节流缓存。
	•	媒体文件仅在内网/私有存储；外链以短时签名控制访问。
	•	仅记录必要的播放日志（可匿名化 UA/设备信息）。

⸻

13) 路线图（无实现细节）
	•	Phase 1：最小可用
	•	电台出队 / 轻反馈 / 睡眠定时 / Media Session / Nginx 直出
	•	Phase 2：体验打磨
	•	同艺人冷却、多样性采样、封面缓存、PWA
	•	Phase 3：可选增强
	•	Last.fm scrobble、MusicBrainz/CAA 补元数据（限流+缓存）、HLS（若确有需求）

⸻

14) 已知限制与取舍（直说）
	•	移动端浏览器后台限制：长时间后台时，定时器可能被节流；用 timeupdate 做兜底。
	•	格式兼容：统一 MP3/AAC 可省心；FLAC/APE 在部分移动端上表现不稳定。
	•	HLS 不是必需：在个人曲库规模下，HTTP Range 已足够；HLS 增复杂度，按需评估。

⸻

15) 品牌与文案
	•	品牌：SuiTune（中文：随听电台）
	•	一句话：Press Play, let it flow.
	•	副标：Less choice, more listening.

⸻

16) 项目约定（目录/命名示例）
	•	ENV 前缀：SUITUNE_*（如 SUITUNE_MEDIA_ROOT, SUITUNE_SIGNING_SECRET）
	•	DB 表前缀：sui_
	•	受保护流：/sui_stream/relative/path/to/file.mp3
	•	频道常量：music/talk/tv/ambient

⸻

想法保守一点：先把 Phase 1 跑通（能稳定“闭眼播一晚”），再加花。被动听的价值在“稳+懂你”，而不是在堆功能。需要我把这份 README 同步成仓库 README.md 的起始版本吗？我也可以顺手加上 issue 模板与里程碑清单。
