// @ts-check
import React, { useEffect, useState } from "react";
import { fetchTracks } from "../../core/api/client";
import { audioService } from "../../core/services/audioService";

export default function Home() {
  const [tracks, setTracks] = useState([]);

  useEffect(() => {
    fetchTracks().then(setTracks).catch(console.error);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="p-4 text-2xl font-bold text-center">SuiTune</header>
      <main className="p-4">
        <ul className="space-y-2">
          {tracks.map((t) => (
            <li
              key={t.id}
              className="flex items-center justify-between bg-white p-4 rounded shadow"
            >
              <div>
                <p className="font-medium">{t.title}</p>
                {t.artist && (
                  <p className="text-sm text-gray-500">{t.artist}</p>
                )}
              </div>
              <button
                className="px-3 py-1 text-sm text-white bg-indigo-600 rounded"
                onClick={() => {
                  audioService.load(t.audio_url);
                  audioService.play();
                }}
              >
                Play
              </button>
            </li>
          ))}
        </ul>
      </main>
    </div>
  );
}
