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
