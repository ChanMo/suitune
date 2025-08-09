/**
 * SuiTune - 现代化单页应用管理器
 * 使用原生JavaScript + Fetch API + History API
 */

class SuiTuneApp {
    constructor() {
        this.currentPage = this.getCurrentPageType();
        this.favoritesData = [];
        this.globalMusicManager = window.globalMusicManager;
        
        // 等待DOM加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initialize());
        } else {
            this.initialize();
        }
    }

    // 更新globalMusicManager引用的方法
    updateGlobalMusicManager() {
        this.globalMusicManager = window.globalMusicManager;
    }

    initialize() {
        console.log('SuiTune App initializing...', this.currentPage);
        
        // 初始化SPA导航
        this.initializeNavigation();
        
        // 初始化页面特定功能
        this.initializePageFeatures();
        
        // 初始化全局事件监听
        this.initializeGlobalEvents();
    }

    // 获取当前页面类型
    getCurrentPageType() {
        const pageElement = document.querySelector('[data-page]');
        return pageElement ? pageElement.dataset.page : 'unknown';
    }

    // 初始化SPA导航 - 简化版，让base.html中的路由器处理
    initializeNavigation() {
        // 监听页面变化事件，重新初始化功能
        window.addEventListener('spaPageChanged', (e) => {
            this.currentPage = this.getCurrentPageType();
            this.initializePageFeatures();
        });
    }

    // 初始化页面特定功能
    initializePageFeatures() {
        switch (this.currentPage) {
            case 'home':
                this.initializeHomePage();
                break;
            case 'favorites':
                this.initializeFavoritesPage();
                break;
        }
    }

    // 初始化首页功能
    initializeHomePage() {
        console.log('Initializing home page...');
        
        const musicCard = document.querySelector('[data-component="music-card"]');
        if (!musicCard) return;

        // 获取控制元素
        const playBtn = musicCard.querySelector('[data-action="toggle-play"]');
        const nextBtn = musicCard.querySelector('[data-action="previous"]');
        const randomBtn = musicCard.querySelector('[data-action="random"]');
        
        // 绑定事件监听器
        if (playBtn) {
            playBtn.addEventListener('click', (e) => this.handlePlayToggle(e));
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', (e) => this.handleNextTrack(e));
        }
        
        if (randomBtn) {
            randomBtn.addEventListener('click', (e) => this.handleRandomTrack(e));
        }

        // 更新首页显示
        this.updateHomeDisplay();
    }

    // 初始化收藏页面功能
    initializeFavoritesPage() {
        console.log('Initializing favorites page...');
        
        // 加载收藏列表
        this.loadFavorites();
        
        // 绑定控制按钮
        const playAllBtn = document.getElementById('play-all-btn');
        const shuffleBtn = document.getElementById('shuffle-btn');
        
        if (playAllBtn) {
            playAllBtn.addEventListener('click', () => this.playAllFavorites());
        }
        
        if (shuffleBtn) {
            shuffleBtn.addEventListener('click', () => this.shuffleFavorites());
        }

        // 使用事件委托处理歌曲点击
        const tracksContainer = document.getElementById('tracks-container');
        if (tracksContainer) {
            tracksContainer.addEventListener('click', (e) => this.handleTrackClick(e));
        }
    }

    // 初始化全局事件监听
    initializeGlobalEvents() {
        // 监听全局音乐播放器状态变化
        window.addEventListener('globalPlayerStateChanged', (e) => {
            if (this.currentPage === 'home') {
                this.updateHomeDisplay();
            }
        });

        // 监听全局按键事件
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
                e.preventDefault();
                this.handlePlayToggle();
            }
        });
    }

    // 处理播放/暂停
    async handlePlayToggle(e) {
        if (e) e.preventDefault();
        
        if (!this.globalMusicManager) {
            console.error('GlobalMusicManager not available');
            return;
        }

        try {
            const currentTrack = this.globalMusicManager.getCurrentTrack();
            
            if (!currentTrack) {
                this.showLoading();
                await this.globalMusicManager.loadNext();
                this.hideLoading();
                this.updateHomeDisplay(true);
            } else {
                await this.globalMusicManager.togglePlayPause();
                this.updateHomeDisplay();
            }
            
            // 添加视觉反馈
            if (e && e.target) {
                this.addButtonAnimation(e.target, 'bounce');
                this.addRippleEffect(e.target);
            }
        } catch (error) {
            console.error('Play toggle failed:', error);
        }
    }

    // 处理下一首
    async handleNextTrack(e) {
        if (e) e.preventDefault();
        
        if (!this.globalMusicManager) return;

        try {
            this.showLoading();
            await this.globalMusicManager.loadNext();
            this.hideLoading();
            this.updateHomeDisplay(true);
            
            // 添加视觉反馈
            if (e && e.target) {
                this.addButtonAnimation(e.target, 'spin');
                this.addRippleEffect(e.target);
                this.createParticles();
            }
        } catch (error) {
            console.error('Next track failed:', error);
            this.hideLoading();
        }
    }

    // 处理随机播放
    async handleRandomTrack(e) {
        if (e) e.preventDefault();
        
        // 随机播放逻辑与下一首相同
        await this.handleNextTrack(e);
    }

    // 更新首页显示
    updateHomeDisplay(withAnimation = false) {
        if (this.currentPage !== 'home' || !this.globalMusicManager) return;

        const currentTrack = this.globalMusicManager.getCurrentTrack();
        const currentChannel = this.globalMusicManager.currentChannel;
        const isPlaying = this.globalMusicManager.getIsPlaying();

        // 更新音乐卡片内容
        const musicCard = document.querySelector('[data-component="music-card"]');
        if (!musicCard) return;

        const titleEl = musicCard.querySelector('.track-title');
        const artistEl = musicCard.querySelector('.track-artist');
        const albumEl = musicCard.querySelector('.track-album');
        const channelEl = musicCard.querySelector('.channel-display');
        const playBtn = musicCard.querySelector('[data-action="toggle-play"]');
        const albumCover = musicCard.querySelector('#album-cover');

        if (currentTrack) {
            if (titleEl) titleEl.textContent = currentTrack.title || '未知音乐';
            if (artistEl) artistEl.textContent = currentTrack.artist || '未知艺术家';  
            if (albumEl) albumEl.textContent = currentTrack.album || '未知专辑';
            
            // 更新专辑封面
            this.updateAlbumCover(albumCover, currentTrack, withAnimation);
        } else {
            if (titleEl) titleEl.textContent = '点击开始探索音乐';
            if (artistEl) artistEl.textContent = 'SuiTune';
            if (albumEl) albumEl.textContent = '个人电台';
            
            // 重置专辑封面
            this.resetAlbumCover(albumCover);
        }

        // 更新播放按钮状态
        if (playBtn) {
            const icon = playBtn.querySelector('i');
            if (icon) {
                if (isPlaying) {
                    icon.className = 'fas fa-pause text-white text-xl';
                    if (albumCover) albumCover.classList.add('music-playing');
                } else {
                    icon.className = 'fas fa-play text-white text-xl ml-1';
                    if (albumCover) albumCover.classList.remove('music-playing');
                }
            }
        }

        // 更新频道显示
        if (channelEl) {
            const channelNames = {
                'music': '音乐频道',
                'talk': '相声频道', 
                'tv': 'TV音频频道',
                'ambient': '环境音频道'
            };
            channelEl.textContent = channelNames[currentChannel] || '音乐频道';
        }
    }

    // 更新专辑封面
    updateAlbumCover(coverElement, track, withAnimation = false) {
        if (!coverElement) return;

        if (withAnimation) {
            coverElement.style.animation = 'cardFlip 0.6s ease-in-out';
            setTimeout(() => {
                coverElement.style.animation = '';
            }, 600);
        }

        if (track && track.artwork_url) {
            const imageHtml = `
                <img src="${track.artwork_url}" 
                     alt="${track.album || '专辑封面'}" 
                     class="w-full h-full object-cover rounded-2xl"
                     onerror="this.parentElement.innerHTML='<i class=\\'fas fa-music text-6xl text-white/80\\'></i>'"
                />
                <div class="particles-container absolute inset-0 pointer-events-none"></div>
            `;
            
            if (withAnimation) {
                setTimeout(() => {
                    coverElement.innerHTML = imageHtml;
                }, 300);
            } else {
                coverElement.innerHTML = imageHtml;
            }
        } else {
            if (withAnimation) {
                setTimeout(() => {
                    this.resetAlbumCover(coverElement);
                }, 300);
            } else {
                this.resetAlbumCover(coverElement);
            }
        }
    }

    // 重置专辑封面
    resetAlbumCover(coverElement) {
        if (coverElement) {
            coverElement.innerHTML = `
                <i class="fas fa-music text-6xl text-white/80"></i>
                <div class="particles-container absolute inset-0 pointer-events-none"></div>
            `;
        }
    }

    // 加载收藏列表
    async loadFavorites() {
        try {
            const loadingState = document.getElementById('loading-state');
            const emptyState = document.getElementById('empty-state');
            const favoritesGrid = document.getElementById('favorites-grid');
            const pageSubtitle = document.getElementById('page-subtitle');

            if (loadingState) loadingState.classList.remove('hidden');
            if (emptyState) emptyState.classList.add('hidden');
            if (favoritesGrid) favoritesGrid.classList.add('hidden');

            const response = await fetch('/api/favorites');
            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            this.favoritesData = data.favorites;

            if (loadingState) loadingState.classList.add('hidden');

            if (this.favoritesData.length === 0) {
                if (emptyState) emptyState.classList.remove('hidden');
                if (pageSubtitle) pageSubtitle.textContent = '还没有收藏任何音乐';
            } else {
                if (favoritesGrid) favoritesGrid.classList.remove('hidden');
                if (pageSubtitle) pageSubtitle.textContent = `共收藏了 ${data.count} 首音乐`;
                this.renderFavorites();
                this.calculateTotalDuration();
            }

        } catch (error) {
            console.error('Error loading favorites:', error);
            const loadingState = document.getElementById('loading-state');
            const pageSubtitle = document.getElementById('page-subtitle');
            if (loadingState) loadingState.classList.add('hidden');
            if (pageSubtitle) pageSubtitle.textContent = '加载失败：' + error.message;
        }
    }

    // 渲染收藏列表
    renderFavorites() {
        const tracksContainer = document.getElementById('tracks-container');
        if (!tracksContainer) return;

        tracksContainer.innerHTML = '';

        this.favoritesData.forEach((track, index) => {
            const trackHtml = this.generateTrackItemHTML(track, index);
            tracksContainer.insertAdjacentHTML('beforeend', trackHtml);
        });
    }

    // 生成歌曲项HTML
    generateTrackItemHTML(track, index) {
        return `
            <div class="group bg-black/30 backdrop-blur-xl rounded-2xl p-6 shadow-xl border border-white/10 hover:bg-black/40 transition-all duration-300 hover:scale-[1.02] track-item cursor-pointer" 
                 data-component="track-item" 
                 data-track-id="${track.id}" 
                 data-index="${index}">
                
                <div class="flex items-center space-x-4">
                    <!-- Album Cover -->
                    <div class="flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center shadow-lg">
                        ${track.artwork_url ? 
                            `<img src="${track.artwork_url}" alt="${track.album || '专辑封面'}" class="w-full h-full object-cover" onerror="this.parentElement.innerHTML='<i class=\\'fas fa-music text-white text-xl\\'></i>'"/>` : 
                            `<i class="fas fa-music text-white text-xl"></i>`
                        }
                    </div>
                    
                    <!-- Track Info -->
                    <div class="flex-grow min-w-0">
                        <h3 class="text-white text-lg font-semibold truncate">${track.title}</h3>
                        <p class="text-gray-300 truncate">${track.artist}</p>
                        <div class="flex items-center space-x-4 mt-2">
                            <span class="text-gray-400 text-sm">${track.album}</span>
                            <span class="text-gray-500 text-xs">•</span>
                            <span class="text-gray-400 text-sm flex items-center">
                                <i class="${this.getChannelIcon(track.channel)} mr-1"></i>
                                ${this.getChannelName(track.channel)}
                            </span>
                            <span class="text-gray-500 text-xs">•</span>
                            <span class="text-gray-400 text-sm">${this.formatTime(track.duration)}</span>
                        </div>
                    </div>
                    
                    <!-- Actions -->
                    <div class="flex items-center space-x-2" data-no-click="true">
                        <button class="unlike-btn w-10 h-10 bg-pink-500/20 hover:bg-pink-500/30 rounded-full flex items-center justify-center transition-all duration-200 hover:scale-110" 
                                data-action="unlike" 
                                data-track-id="${track.id}">
                            <i class="fas fa-heart text-pink-400"></i>
                        </button>
                        <button class="ban-btn w-10 h-10 bg-red-500/20 hover:bg-red-500/30 rounded-full flex items-center justify-center transition-all duration-200 hover:scale-110" 
                                data-action="ban" 
                                data-track-id="${track.id}">
                            <i class="fas fa-ban text-red-400"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    // 处理歌曲项点击
    handleTrackClick(e) {
        // 不处理操作按钮的点击
        if (e.target.closest('[data-no-click]')) {
            return this.handleTrackAction(e);
        }

        const trackItem = e.target.closest('[data-component="track-item"]');
        if (!trackItem) return;

        const index = parseInt(trackItem.dataset.index);
        const track = this.favoritesData[index];
        
        if (track && this.globalMusicManager) {
            this.globalMusicManager.playTrack(track);
        }
    }

    // 处理歌曲操作（收藏、屏蔽）
    async handleTrackAction(e) {
        const button = e.target.closest('[data-action]');
        if (!button) return;

        const action = button.dataset.action;
        const trackId = button.dataset.trackId;

        switch (action) {
            case 'unlike':
                await this.removeFavorite(trackId);
                break;
            case 'ban':
                await this.banTrack(trackId);
                break;
        }
    }

    // 移除收藏
    async removeFavorite(trackId) {
        try {
            const response = await fetch('/api/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    track_id: trackId,
                    action: 'unlike'
                })
            });

            if (response.ok) {
                // 重新加载收藏列表
                await this.loadFavorites();
            }
        } catch (error) {
            console.error('Error removing favorite:', error);
        }
    }

    // 屏蔽歌曲
    async banTrack(trackId) {
        if (!confirm('确定要屏蔽这首音乐吗？这将从收藏中移除并不再推荐。')) {
            return;
        }

        try {
            const response = await fetch('/api/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    track_id: trackId,
                    action: 'ban'
                })
            });

            if (response.ok) {
                // 重新加载收藏列表
                await this.loadFavorites();
            }
        } catch (error) {
            console.error('Error banning track:', error);
        }
    }

    // 播放所有收藏
    playAllFavorites() {
        if (this.favoritesData.length > 0 && this.globalMusicManager) {
            this.globalMusicManager.playTrack(this.favoritesData[0]);
        }
    }

    // 随机播放收藏
    shuffleFavorites() {
        if (this.favoritesData.length > 0 && this.globalMusicManager) {
            const randomIndex = Math.floor(Math.random() * this.favoritesData.length);
            this.globalMusicManager.playTrack(this.favoritesData[randomIndex]);
        }
    }

    // 计算总时长
    calculateTotalDuration() {
        const totalDurationEl = document.getElementById('total-duration');
        if (!totalDurationEl) return;

        const totalSeconds = this.favoritesData.reduce((sum, track) => sum + (track.duration || 0), 0);
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);

        if (hours > 0) {
            totalDurationEl.textContent = `总时长：${hours}小时${minutes}分钟`;
        } else {
            totalDurationEl.textContent = `总时长：${minutes}分钟`;
        }
    }

    // 工具方法
    getChannelIcon(channel) {
        const icons = {
            'music': 'fas fa-music',
            'talk': 'fas fa-microphone',
            'tv': 'fas fa-tv',
            'ambient': 'fas fa-leaf'
        };
        return icons[channel] || 'fas fa-music';
    }

    getChannelName(channel) {
        const names = {
            'music': '音乐',
            'talk': '相声',
            'tv': 'TV音频',
            'ambient': '环境音'
        };
        return names[channel] || '音乐';
    }

    formatTime(seconds) {
        if (!seconds || isNaN(seconds)) return '0:00';
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    getCSRFToken() {
        const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }

    // 动画效果方法
    addButtonAnimation(element, type) {
        element.classList.add(`button-${type}`);
        setTimeout(() => {
            element.classList.remove(`button-${type}`);
        }, 300);
    }

    addRippleEffect(element) {
        const ripple = document.createElement('span');
        ripple.className = 'absolute inset-0 bg-white/20 rounded-full animate-ping';
        element.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
    }

    createParticles() {
        const container = document.querySelector('.particles-container');
        if (!container) return;

        const colors = ['rgba(147, 51, 234, 0.8)', 'rgba(236, 72, 153, 0.8)', 'rgba(59, 130, 246, 0.8)'];
        
        for (let i = 0; i < 8; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.top = Math.random() * 100 + '%';
            particle.style.background = colors[Math.floor(Math.random() * colors.length)];
            particle.style.animationDelay = Math.random() * 2 + 's';
            
            container.appendChild(particle);
            
            setTimeout(() => particle.remove(), 3000);
        }
    }

    showLoading() {
        const loadingSpinner = document.querySelector('.loading-spinner');
        if (loadingSpinner) {
            loadingSpinner.classList.remove('hidden');
        }
    }

    hideLoading() {
        const loadingSpinner = document.querySelector('.loading-spinner');
        if (loadingSpinner) {
            loadingSpinner.classList.add('hidden');
        }
    }
}

// 初始化应用 - 等待globalMusicManager就绪
function initializeSuiTuneApp() {
    if (window.globalMusicManager && !window.suiTuneApp) {
        window.suiTuneApp = new SuiTuneApp();
    } else if (!window.globalMusicManager) {
        // 如果globalMusicManager还没初始化，等待一下再尝试
        setTimeout(initializeSuiTuneApp, 50);
    }
}

// 开始初始化
initializeSuiTuneApp();