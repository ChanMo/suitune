export const mediaSessionService = {
  update: (meta) => {
    if ("mediaSession" in navigator) {
      navigator.mediaSession.metadata = new MediaMetadata(meta);
    }
  },
};
