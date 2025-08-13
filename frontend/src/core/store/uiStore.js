import { create } from "zustand";

export const useUiStore = create(() => ({
  nowOpen: false,
  toasts: [],
}));
