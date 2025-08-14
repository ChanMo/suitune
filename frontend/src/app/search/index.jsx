// @ts-check
import React, { useState } from "react";
import { searchTracks } from "../../core/api/client";
import { audioService } from "../../core/services/audioService";

export default function Search() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  const handleSubmit = (e) => {
    e.preventDefault();
    searchTracks(query).then(setResults).catch(console.error);
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Search</h1>
      <form onSubmit={handleSubmit} className="mb-4 flex">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search tracks..."
          className="flex-1 border p-2 rounded-l"
        />
        <button
          type="submit"
          className="px-3 py-2 bg-indigo-600 text-white rounded-r"
        >
          Search
        </button>
      </form>
      <ul className="space-y-2">
        {results.map((t) => (
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
