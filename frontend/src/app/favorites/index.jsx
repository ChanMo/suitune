// @ts-check
import React, { useEffect, useState } from "react";
import { fetchFavorites } from "../../core/api/client";
import { audioService } from "../../core/services/audioService";

export default function Favorites() {
  const [tracks, setTracks] = useState([]);

  useEffect(() => {
    fetchFavorites().then(setTracks).catch(console.error);
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Favorites</h1>
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
    </div>
  );
}
