import { useState, useRef, useEffect } from "react";
import { FaPause, FaPlay } from "react-icons/fa";
import vibes from "../music/vibes.mp3";

export default function MusicPlayer({ triggerPlay }) {
  const [isPlaying, setIsPlaying] = useState(false);

  const audioRef = useRef(null);

  const togglePlayback = () => {
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  useEffect(() => {
    if (triggerPlay && !isPlaying) {
      audioRef.current.play();
      setIsPlaying(true);
    }
  }, [triggerPlay]);

  return (
    <>
      <div
        className={`flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-md shadow-xl border border-white/20cursor-pointer transition-transform hover:scale-105 hover:bg-white/20 ${
          isPlaying ? "ring-2 ring-purple-500 animate-pulse" : ""
        }`}
        onClick={togglePlayback}
      >
        {isPlaying ? (
          <FaPause className="text-xl text-purple-400" />
        ) : (
          <FaPlay className="text-xl text-purple-400" />
        )}
        <span className="text-slate-200 text-sm font-semibold pr-1 select-none">
          {isPlaying ? "Chill Mode: ON" : "Play Vibes"}
        </span>
      </div>
      <audio src={vibes} ref={audioRef} loop preload="auto" />
    </>
  );
}
