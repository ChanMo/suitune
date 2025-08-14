import { z } from "zod";

const nextSchema = z.object({
  track: z.any(),
  stream_url: z.string(),
});

const trackSchema = z.object({
  id: z.number(),
  title: z.string(),
  artist: z.string().optional(),
  audio_url: z.string(),
});

const settingsSchema = z.object({
  volume: z.number().min(0).max(1),
  dark_mode: z.boolean().optional(),
});

export async function fetchNext(channel = "music") {
  const resp = await fetch(
    `${import.meta.env.VITE_API_BASE}/next?channel=${channel}`,
  );
  const json = await resp.json();
  return nextSchema.parse(json);
}

export async function fetchTracks() {
  const resp = await fetch(`${import.meta.env.VITE_API_BASE}/tracks/`);
  const json = await resp.json();
  return z.array(trackSchema).parse(json);
}

export async function fetchFavorites() {
  const resp = await fetch(`${import.meta.env.VITE_API_BASE}/favorites/`);
  const json = await resp.json();
  return z.array(trackSchema).parse(json);
}

export async function searchTracks(query) {
  const resp = await fetch(
    `${import.meta.env.VITE_API_BASE}/search?q=${encodeURIComponent(query)}`,
  );
  const json = await resp.json();
  return z.array(trackSchema).parse(json);
}

export async function fetchSettings() {
  const resp = await fetch(`${import.meta.env.VITE_API_BASE}/settings`);
  const json = await resp.json();
  return settingsSchema.parse(json);
}

export async function updateSettings(settings) {
  const resp = await fetch(`${import.meta.env.VITE_API_BASE}/settings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(settings),
  });
  const json = await resp.json();
  return settingsSchema.parse(json);
}
