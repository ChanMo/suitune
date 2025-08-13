export const audioService = {
  load: (src) => {
    const audio = document.getElementById("sui-audio");
    audio.src = src;
  },
  play: () => document.getElementById("sui-audio").play(),
  pause: () => document.getElementById("sui-audio").pause(),
};
