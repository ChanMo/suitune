import { create } from "zustand";

export const usePlayerStore = create(() => ({
  current: null,
  queue: [],
  playing: false,
  position: 0,
  volume: 1,
  channel: "music",
  sleep: { stopAt: null },
  leader: { isLeader: true },
}));
