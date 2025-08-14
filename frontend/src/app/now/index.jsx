// @ts-check
import React, { useEffect, useState } from "react";
import { fetchNext } from "../../core/api/client";
import { audioService } from "../../core/services/audioService";
import { mediaSessionService } from "../../core/services/mediaSessionService";

export default function Now() {
  const [track, setTrack] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    const audio = document.getElementById("sui-audio");
    const onPlay = () => setIsPlaying(true);
    const onPause = () => setIsPlaying(false);
    audio.addEventListener("play", onPlay);
    audio.addEventListener("pause", onPause);

    if (!audio.src) {
      handleNext();
    }

    return () => {
      audio.removeEventListener("play", onPlay);
      audio.removeEventListener("pause", onPause);
    };
  }, []);

  const handleNext = () => {
    fetchNext()
      .then(({ track, stream_url }) => {
        setTrack(track);
        audioService.load(stream_url);
        audioService.play();
        mediaSessionService.update({
          title: track.title,
          artist: track.artist || "",
          artwork: track.cover_url
            ? [{ src: track.cover_url, sizes: "512x512", type: "image/png" }]
            : [],
        });
      })
      .catch(console.error);
  };

  const toggle = () => {
    if (isPlaying) {
      audioService.pause();
    } else {
      audioService.play();
    }
  };

  return (
    <div className="p-4 text-center">
      {track && (
        <>
          {track.cover_url && (
            <img
              src={track.cover_url}
              alt="cover"
              className="w-48 h-48 object-cover mx-auto mb-4"
            />
          )}
          <h2 className="text-xl font-bold">{track.title}</h2>
          {track.artist && (
            <p className="text-gray-500 mb-4">{track.artist}</p>
          )}
        </>
      )}
      <div className="flex justify-center space-x-4 mt-4">
        <button
          onClick={toggle}
          className="px-4 py-2 bg-indigo-600 text-white rounded"
        >
          {isPlaying ? "Pause" : "Play"}
        </button>
        <button
          onClick={handleNext}
          className="px-4 py-2 bg-gray-200 rounded"
        >
          Next
        </button>
      </div>
    </div>
  );
}
